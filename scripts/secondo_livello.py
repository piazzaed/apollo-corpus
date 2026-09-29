#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FONTI DI SECONDO LIVELLO (v0.34): i testi che normattiva non serve — CCNL, regolamenti e disposizioni delle
autorita', codici deontologici — come file Markdown che si descrivono da soli.

PERCHE'
-------
Il corpus normattiva (codici.json + *-indice.json) vive di URN: download, confronto settimanale, date di vigenza
per articolo. Un CCNL o un regolamento IVASS un URN non ce l'ha. Qui ogni fonte e' UN file
`wiki-studio/normativa/testi/secondo-livello/<alias>.md` che porta nell'intestazione tutto cio' che serve per
servirla e verificarla: da dove viene (url pubblico, sha256 del documento d'origine, esito del confronto col
documento), quando e' stata presa, per quale periodo vale, come la si cita. Il registro si ricava dai file:
due fonti aggiunte da due persone diverse non toccano mai lo stesso file.

FORMATO
-------
    ---
    alias: "ccnl-esempio-2024"
    nome: "CCNL di esempio — rinnovo 22 marzo 2024"
    famiglia: "ccnl-esempio"
    genere: "ccnl"
    natura: "testo-integrale"
    fonte: "Archivio CNEL"
    url: "https://www.cnel.it/..."
    scaricato_il: "2026-09-29"
    sha256_fonte: "<64 cifre esadecimali del documento scaricato>"
    fedelta: "verificata"
    codice_cnel: "Z999"
    vigenza_da: "2024-04-01"
    vigenza_a: "2027-03-31"
    sinonimi: ["ccnl esempio", "contratto collettivo esempio"]
    ---
    ### Art. 1 — Sfera di applicazione
    ...

Una riga per chiave, valore in JSON (stringhe fra virgolette, liste fra quadre), niente valori su piu' righe,
intestazione di al massimo 8 KB. Articoli con `### Art. <n> [— rubrica]`; i testi non divisi per articoli
dichiarano `struttura: "sezioni"`. Un CCNL ha un file per edizione, legate dalla stessa `famiglia`: la lettura
alla data sceglie l'edizione in vigore. Un accordo di rinnovo (`natura: "accordo-di-rinnovo"`) e' un file a
sezioni con `articoli_modificati`. Ritiro: stesso file con `stato: "ritirato"`, `ritirato_il`, `motivo`, corpo
vuoto e, perche' chi la cita sappia che e' ritirata, `nome` e `sinonimi` della fonte (si propaga come ogni altra
modifica e vince sulla copia vecchia).

DOVE SI LEGGE
-------------
Due cartelle: il seed del plugin (`wiki-studio/normativa/testi/secondo-livello/`) e la copia sincronizzata dal
corpus pubblico (`<stato>/testi/secondo-livello/`). Per ogni alias vince la copia piu' recente per data
d'intestazione; a parita', la sincronizzata. `secondo-livello.json` resta per i puntatori (atti serviti dal
corpus normattiva o da un resolver) e per i segnaposto delle fonti non ancora scaricate.

Uso:
  python3 scripts/secondo_livello.py --valida FILE.md [...]     # controllo strutturale (exit 1 se errori)
  python3 scripts/secondo_livello.py --elenco                    # il registro: alias, famiglia, edizione, stato
  python3 scripts/secondo_livello.py --trova "art. 5 ccnl esempio" [--data 2025-01-10]
Solo stdlib, Python 3.9. Nessun import pesante: lo usano anche gli hook.
"""
from __future__ import annotations

import argparse
import bisect
import datetime as _dt
import functools
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import WIKI, stato_root  # noqa: E402

CARTELLA = "secondo-livello"
REGISTRO_BUNDLE = WIKI / "normativa" / "secondo-livello.json"
MAX_INTESTAZIONE = 8192
MAX_BYTE = 8 * 1024 * 1024
MAX_ALIAS = 80
RX_ALIAS = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RISERVATI_WINDOWS = {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} | {f"lpt{i}" for i in range(1, 10)}

GENERI = ("ccnl", "accordo-collettivo", "regolamento", "disposizioni", "istruzioni", "codice-deontologico",
          "specifiche-tecniche", "altro")
NATURE = ("testo-integrale", "testo-coordinato", "accordo-di-rinnovo")
STRUTTURE = ("articoli", "sezioni")
FEDELTA = ("verificata", "non_verificata")
OBBLIGATORI = ("alias", "nome", "famiglia", "genere", "fonte", "url", "scaricato_il", "sha256_fonte", "fedelta")
LISTE = ("sinonimi", "materie", "parti", "articoli_modificati")
DATE = ("scaricato_il", "vigenza_da", "vigenza_a", "data_stipula", "ritirato_il", "vigente_al")
#: ordine delle chiavi quando lo strumento scrive un'intestazione (le altre seguono in ordine alfabetico)
ORDINE = ("alias", "nome", "famiglia", "genere", "natura", "struttura", "fonte", "url", "url_pagina", "scaricato_il",
          "sha256_fonte", "fedelta", "estratto", "codice_cnel", "parti", "data_stipula", "vigenza_da", "vigenza_a",
          "articoli_modificati", "citazione", "sinonimi", "materie", "vigente_al", "note", "stato", "ritirato_il",
          "motivo")
#: parole che da sole non identificano una fonte: un sinonimo di un solo token deve essere una sigla vera
#: (gdpr, cdf) o contenere una cifra
GENERICHE = {"ccnl", "cnel", "contratto", "contratti", "collettivo", "accordo", "accordi", "regolamento", "disposizioni",
             "istruzioni", "codice", "legge", "decreto", "norma", "norme", "testo", "art", "articolo", "allegato",
             "tabella", "tabelle", "provvedimento", "circolare", "delibera", "rinnovo", "commercio", "industria"}
_SUFFISSI = ("bis|ter|quater|quinquies|sexies|septies|octies|novies|nonies|decies|undecies|duodecies|terdecies|"
             "quaterdecies|quindecies")


# ---------------------------------------------------------------- testo e intestazione

def norm_token(grezzo: str) -> str:
    """La chiave di un articolo, identica a `codice_locale._norm_token` («281 undecies» → «281-undecies»,
    «nonies» → «novies»), piu' la forma incollata dei CCNL («25bis» → «25-bis»)."""
    s = grezzo.lower().replace("art.", "").strip(" .")
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    s = re.sub(rf"^(\d+)({_SUFFISSI})\b", r"\1-\2", s)
    return s.replace("nonies", "novies")


@functools.lru_cache(maxsize=8192)
def norm_testo(s: str) -> str:
    """Minuscole, senza accenti, solo [a-z0-9/] a spazi singoli: la forma su cui si confrontano i riferimenti."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return " ".join(re.sub(r"[^a-z0-9/ ]", " ", s.replace("’", "'")).split())


def decodifica(dati: bytes) -> str:
    """UTF-8 (con o senza BOM), a capo normalizzati a LF."""
    t = dati.decode("utf-8-sig")
    return t.replace("\r\n", "\n").replace("\r", "\n")


def dividi(testo: str):
    """(blocco dell'intestazione o None, corpo)."""
    if not testo.startswith("---\n"):
        return None, testo
    fine = testo.find("\n---\n", 3)
    if fine >= 0:
        return testo[4:fine], testo[fine + 5:]
    if testo.endswith("\n---"):
        return testo[4:-4], ""
    return None, testo


_RX_CHIAVE = re.compile(r"^([a-z_][a-z0-9_]*)[ \t]*:[ \t]*(.*)$")


def parse_intestazione(blocco: str):
    """(dict, errori, chiavi_non_json). Ogni riga «chiave: <valore JSON>»; un valore senza virgolette (forma
    vecchia) si legge come testo e finisce in chiavi_non_json."""
    head, errori, grezze = {}, [], []
    for n, riga in enumerate(blocco.split("\n"), 1):
        if not riga.strip():
            continue
        m = _RX_CHIAVE.match(riga)
        if not m:
            errori.append(f"intestazione, riga {n}: non e' «chiave: valore»")
            continue
        k, v = m.group(1), m.group(2).strip()
        if k in head:
            errori.append(f"intestazione: chiave ripetuta «{k}»")
        if v == "":
            head[k] = ""
            continue
        try:
            head[k] = json.loads(v)
        except ValueError:
            if v[:1] in "[{":
                errori.append(f"intestazione: «{k}» non e' JSON valido")
            head[k] = v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v
            grezze.append(k)
    return head, errori, grezze


def scrivi_intestazione(head: dict) -> str:
    """Il blocco `---` … `---` nella forma canonica (una riga per chiave, valori JSON)."""
    chiavi = [k for k in ORDINE if k in head] + sorted(k for k in head if k not in ORDINE and not k.startswith("_"))
    return "---\n" + "".join(f"{k}: {json.dumps(head[k], ensure_ascii=False)}\n" for k in chiavi) + "---\n"


_CACHE_TESTA: dict = {}
_CACHE_CORPO: dict = {}
_CACHE_REG: dict = {}


def _firma(p: Path):
    st = p.stat()
    return (str(p), st.st_mtime_ns, st.st_size)


def leggi_intestazione(p: Path):
    """(intestazione o None, errori) leggendo solo l'inizio del file."""
    p = Path(p)
    try:
        chiave = _firma(p)
    except OSError:
        return None, ["file assente"]
    if chiave in _CACHE_TESTA:
        return _CACHE_TESTA[chiave]
    with p.open("rb") as f:
        inizio = f.read(MAX_INTESTAZIONE + 16)
    testo = inizio.decode("utf-8-sig", errors="ignore").replace("\r\n", "\n").replace("\r", "\n")
    blocco, _ = dividi(testo)
    if blocco is None:
        esito = (None, ["intestazione assente o piu' lunga di 8 KB"])
    else:
        head, errori, _g = parse_intestazione(blocco)
        esito = (head, errori)
    _CACHE_TESTA[chiave] = esito
    return esito


def leggi(p: Path) -> dict:
    """Il file intero: {intestazione, corpo, errori, grezze, bom, crlf}. In cache per (path, mtime, size)."""
    p = Path(p)
    chiave = _firma(p)
    if chiave in _CACHE_CORPO:
        return _CACHE_CORPO[chiave]
    dati = p.read_bytes()
    testo = decodifica(dati)
    blocco, corpo = dividi(testo)
    head, errori, grezze = parse_intestazione(blocco) if blocco is not None else ({}, ["intestazione assente"], [])
    out = {"intestazione": head, "corpo": corpo, "errori": errori, "grezze": grezze,
           "bom": dati[:3] == b"\xef\xbb\xbf", "crlf": b"\r\n" in dati[:65536]}
    if len(_CACHE_CORPO) > 24:
        _CACHE_CORPO.clear()
    _CACHE_CORPO[chiave] = out
    return out


# ---------------------------------------------------------------- articoli

_RX_TITOLO = re.compile(
    rf"^###[ \t]+Art\.?[ \t]*(?P<tok>\d+(?:[ \t]*-?[ \t]*(?:{_SUFFISSI})\b)?(?:\.\d+)?)(?![\w.])(?P<resto>[^\n]*)$",
    re.M | re.I)
_RX_FINE = re.compile(r"^#{1,3}[ \t]", re.M)


def _rubrica(resto: str) -> str:
    r = resto.strip()
    r = re.sub(r"^[—–-]+\s*", "", r)
    if r.startswith("(") and r.endswith(")"):
        r = r[1:-1]
    return r.strip()


def articoli(corpo: str) -> list:
    """[(token, rubrica, inizio, fine)] nell'ordine del testo; l'articolo va dal suo titolo al titolo successivo
    di livello 1-3 (un «## TITOLO II» chiude l'articolo che lo precede)."""
    fini = [m.start() for m in _RX_FINE.finditer(corpo)]
    out = []
    for m in _RX_TITOLO.finditer(corpo):
        i = bisect.bisect_right(fini, m.start())
        fine = fini[i] if i < len(fini) else len(corpo)
        out.append((norm_token(m.group("tok")), _rubrica(m.group("resto")), m.start(), fine))
    return out


# ---------------------------------------------------------------- validazione (chi pubblica, il manifest)

def _data_iso(v) -> bool:
    try:
        _dt.date.fromisoformat(str(v)[:10])
        return len(str(v)) == 10 or bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$", str(v)))
    except ValueError:
        return False


def sinonimo_valido(s: str) -> bool:
    """Un sinonimo deve identificare la fonte: niente parole generiche isolate («ccnl», «disposizioni»)."""
    toks = norm_testo(s).split()
    if not toks or len(" ".join(toks)) < 3:
        return False
    if len(toks) == 1:
        t = toks[0]
        return t not in GENERICHE and (any(c.isdigit() for c in t) or len(t) <= 6)
    return not all(t in GENERICHE for t in toks)


def valida(p: Path, dati: bytes = None) -> dict:
    """Controllo strutturale di un file di secondo livello. {errori, avvisi, intestazione, articoli, sha256, byte}.
    Errori = il file non si pubblica (nel corpus pubblico finisce in quarantena); avvisi = si pubblica e si segnala."""
    p = Path(p)
    errori, avvisi = [], []
    try:
        dati = dati if dati is not None else p.read_bytes()
    except OSError as e:
        return {"errori": [f"illeggibile: {e.__class__.__name__}"], "avvisi": [], "intestazione": {}, "articoli": 0}
    out = {"errori": errori, "avvisi": avvisi, "intestazione": {}, "articoli": 0,
           "sha256": hashlib.sha256(dati).hexdigest(), "byte": len(dati)}
    stem = p.name[:-3] if p.name.endswith(".md") else p.name
    if not p.name.endswith(".md"):
        errori.append("il file deve avere estensione .md")
    if not RX_ALIAS.match(stem) or len(stem) > MAX_ALIAS or stem in _RISERVATI_WINDOWS:
        errori.append(f"nome del file «{p.name}»: solo minuscole ASCII, cifre e trattini, al massimo {MAX_ALIAS} caratteri")
    if len(dati) > MAX_BYTE:
        errori.append(f"file di {len(dati)} byte: oltre il limite di {MAX_BYTE}")
    try:
        testo = decodifica(dati)
    except UnicodeDecodeError:
        errori.append("non e' testo UTF-8")
        return out
    if dati[:3] == b"\xef\xbb\xbf":
        avvisi.append("BOM UTF-8 in testa (lo strumento di pubblicazione lo toglie)")
    if b"\r" in dati:
        avvisi.append("a capo Windows (CRLF): lo strumento di pubblicazione li normalizza")
    blocco, corpo = dividi(testo)
    if blocco is None:
        errori.append("intestazione assente (il file deve iniziare con --- e chiuderla con ---)")
        return out
    if len(blocco.encode("utf-8")) > MAX_INTESTAZIONE:
        errori.append("intestazione oltre 8 KB")
    head, e_int, grezze = parse_intestazione(blocco)
    out["intestazione"] = head
    errori.extend(e_int)
    for k in grezze:
        errori.append(f"intestazione: «{k}» non e' un valore JSON (stringhe fra virgolette doppie)")
    if head.get("alias") != stem:
        errori.append(f"alias «{head.get('alias')}» diverso dal nome del file «{stem}»")
    if head.get("stato") == "ritirato":
        for k in ("famiglia", "ritirato_il", "motivo"):
            if not head.get(k):
                errori.append(f"ritiro senza «{k}»")
        if not head.get("sinonimi"):
            avvisi.append("ritiro senza «sinonimi»: chi cita la fonte non sapra' che e' stata ritirata")
        if corpo.strip():
            errori.append("una fonte ritirata ha il corpo vuoto")
        if head.get("ritirato_il") and not _data_iso(head["ritirato_il"]):
            errori.append("ritirato_il: data non ISO (AAAA-MM-GG)")
        return out
    for k in OBBLIGATORI:
        if head.get(k) in (None, "", []):
            errori.append(f"manca «{k}»")
    for k in head:
        if k in LISTE and not (isinstance(head[k], list) and all(isinstance(x, str) for x in head[k])):
            errori.append(f"«{k}» deve essere una lista di stringhe")
        elif k not in LISTE and isinstance(head[k], (list, dict)) and k not in ("parti",):
            errori.append(f"«{k}» deve essere un valore semplice")
    if head.get("genere") and head["genere"] not in GENERI:
        errori.append(f"genere «{head['genere']}» non fra {', '.join(GENERI)}")
    if head.get("natura") and head["natura"] not in NATURE:
        errori.append(f"natura «{head['natura']}» non fra {', '.join(NATURE)}")
    struttura = head.get("struttura") or "articoli"
    if struttura not in STRUTTURE:
        errori.append(f"struttura «{struttura}» non fra {', '.join(STRUTTURE)}")
    if head.get("fedelta") and head["fedelta"] not in FEDELTA:
        errori.append(f"fedelta «{head['fedelta']}» non fra {', '.join(FEDELTA)}")
    url = str(head.get("url") or "")
    if url and not re.match(r"^https?://[a-z0-9.-]+\.[a-z]{2,}(?::\d+)?(?:/\S*)?$", url, re.I):
        errori.append("url: deve essere un indirizzo http(s) pubblico, senza spazi")
    sha = str(head.get("sha256_fonte") or "")
    if sha and not re.fullmatch(r"[0-9a-f]{64}", sha):
        errori.append("sha256_fonte: 64 cifre esadecimali minuscole")
    if head.get("famiglia") and not RX_ALIAS.match(str(head["famiglia"])):
        errori.append("famiglia: solo minuscole ASCII, cifre e trattini")
    for k in DATE:
        if head.get(k) and not _data_iso(head[k]):
            errori.append(f"{k}: data non ISO (AAAA-MM-GG)")
    if head.get("vigenza_da") and head.get("vigenza_a") and str(head["vigenza_da"])[:10] > str(head["vigenza_a"])[:10]:
        errori.append("vigenza_da successiva a vigenza_a")
    for s in head.get("sinonimi") or []:
        if isinstance(s, str) and not sinonimo_valido(s):
            errori.append(f"sinonimo «{s}» troppo generico: non identifica la fonte")
    if head.get("genere") == "ccnl":
        for k in ("codice_cnel", "data_stipula", "vigenza_da"):
            if not head.get(k):
                avvisi.append(f"CCNL senza «{k}»: la lettura alla data e l'identificazione ne escono piu' deboli")
    if head.get("natura") == "accordo-di-rinnovo":
        if struttura != "sezioni":
            errori.append("un accordo di rinnovo ha struttura «sezioni» (la sua numerazione non e' quella del CCNL)")
        if not head.get("articoli_modificati"):
            errori.append("un accordo di rinnovo elenca gli «articoli_modificati» del CCNL")
    arts = articoli(corpo)
    out["articoli"] = len(arts)
    if struttura == "articoli":
        if not arts:
            errori.append("nessun titolo «### Art. N»: dividi il testo per articoli o dichiara struttura «sezioni»")
        visti = Counter(t for t, *_ in arts)
        doppi = sorted((t for t, n in visti.items() if n > 1), key=lambda x: (len(x), x))
        if doppi:
            errori.append(f"articoli ripetuti ({', '.join(doppi[:8])}): numerazione che riparte per sezione → struttura «sezioni»")
    elif len(corpo.strip()) < 200:
        errori.append("corpo vuoto o quasi")
    return out


# ---------------------------------------------------------------- fedelta' al documento d'origine

_RX_TOKEN = re.compile(r"[a-z0-9]+")
_RX_NUMERO = re.compile(r"\d+(?:[.,]\d+)*")


def _piano(s: str) -> str:
    s = re.sub(r"(\w)-\n\s*(\w)", r"\1\2", s)            # parola spezzata a fine riga nel PDF
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


def _senza_arredo(fonte: str) -> str:
    """Il documento senza le righe che si ripetono (intestazioni e piedi di pagina) ne' quelle dell'indice."""
    righe = [r.strip() for r in fonte.splitlines()]
    forma = [re.sub(r"\d+", "#", r) for r in righe]          # «pag. 12» e «pag. 13» sono la stessa riga
    conta = Counter(f for f in forma if f)
    return "\n".join(r for r, f in zip(righe, forma) if r and conta[f] < 3 and not re.search(r"\.{5,}|…{2,}", r))


def confronta_fonte(corpo_md: str, testo_fonte: str) -> dict:
    """Quanto del Markdown sta nel documento d'origine (precisione), quanto del documento e' nel Markdown
    (copertura, senza intestazioni/piedi/indice), e i numeri del Markdown che il documento non contiene.
    verificata: precisione ≥ 0.98, copertura ≥ 0.90, nessun numero mancante; estratto: come sopra ma copertura
    minore; non_verificata: altrimenti (o documento senza testo, es. PDF scansionato)."""
    # i titoli di livello 1-2 («# nome», «## TITOLO II») sono impaginazione: non fanno parte del testo servito (un
    # articolo si ferma li') e non si confrontano; i titoli degli articoli (### Art. N — rubrica) si', rubrica compresa
    corpo_md = re.sub(r"(?m)^#{1,2}[ \t][^\n]*$", "", corpo_md)
    md = _RX_TOKEN.findall(_piano(corpo_md))
    fo = _RX_TOKEN.findall(_piano(testo_fonte))
    fo_netto = _RX_TOKEN.findall(_piano(_senza_arredo(testo_fonte)))
    cm, cf, cfn = Counter(md), Counter(fo), Counter(fo_netto)
    if len(fo) < max(50, len(md) // 2):
        return {"esito": "non_verificata", "motivo": "documento d'origine senza testo leggibile (scansione?)",
                "precisione": 0.0, "copertura": 0.0, "numeri_mancanti": [], "parole_fuori_fonte": [],
                "token_md": len(md), "token_fonte": len(fo)}
    precisione = sum(min(c, cf[t]) for t, c in cm.items()) / max(1, len(md))
    copertura = sum(min(c, cm[t]) for t, c in cfn.items()) / max(1, len(fo_netto))
    num_fonte = set(_RX_NUMERO.findall(_piano(testo_fonte)))
    num_md = [n for n in _RX_NUMERO.findall(_piano(corpo_md))]
    mancanti = sorted({n for n in num_md if n not in num_fonte}, key=lambda x: (len(x), x))
    fuori = [t for t, _ in (cm - cf).most_common(25)]
    fedele = precisione >= 0.98 and not mancanti
    esito = "verificata" if fedele and copertura >= 0.90 else ("estratto" if fedele else "non_verificata")
    return {"esito": esito, "precisione": round(precisione, 4), "copertura": round(copertura, 4),
            "numeri_mancanti": mancanti[:50], "parole_fuori_fonte": fuori, "token_md": len(md), "token_fonte": len(fo)}


# ---------------------------------------------------------------- registro

def dir_seed() -> Path:
    return WIKI / "normativa" / "testi" / CARTELLA


def dir_runtime() -> Path:
    return stato_root() / "testi" / CARTELLA


def _firma_dir(d: Path):
    try:
        return tuple(sorted((e.name, e.stat().st_mtime_ns, e.stat().st_size) for e in os.scandir(d)
                            if e.name.endswith(".md")))
    except OSError:
        return ()


def scansiona(cartella: Path) -> dict:
    """{alias: voce} dalle intestazioni dei .md di una cartella. Esclusi i file che iniziano con «.» o «_» e i
    segnaposto della forma vecchia (stato «da_scaricare», nessun testo)."""
    out = {}
    cartella = Path(cartella)
    if not cartella.is_dir():
        return out
    for p in sorted(cartella.glob("*.md")):
        if p.name.startswith((".", "_")):
            continue
        head, errori = leggi_intestazione(p)
        if not head or head.get("stato") == "da_scaricare":
            continue
        out[p.stem] = {**head, "_file": str(p), "_errori": errori}
    return out


def _quando(v: dict) -> str:
    return max(str(v.get("scaricato_il") or ""), str(v.get("ritirato_il") or ""))


def _unisci_liste(*liste) -> list:
    out = []
    for lst in liste:
        for x in lst or []:
            if isinstance(x, str) and x not in out:
                out.append(x)
    return out


def registro(bundle: Path = None, seed: Path = None, runtime: Path = None) -> dict:
    """{"_meta", "alias": {alias: voce}}: i puntatori e i segnaposto di secondo-livello.json, piu' le fonti
    descritte dai file (seed e sincronizzate). Fra due copie dello stesso alias vince la piu' recente per data
    d'intestazione; a parita' vince il ritiro, poi la copia sincronizzata."""
    bundle = Path(bundle or REGISTRO_BUNDLE)
    seed = Path(seed or dir_seed())
    runtime = Path(runtime or dir_runtime())
    try:
        firma_b = bundle.stat().st_mtime_ns
    except OSError:
        firma_b = 0
    chiave = (str(bundle), firma_b, str(seed), _firma_dir(seed), str(runtime), _firma_dir(runtime))
    if _CACHE_REG.get("chiave") == chiave:
        return _CACHE_REG["valore"]
    try:
        base = json.loads(bundle.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        base = {"_meta": {}, "alias": {}}
    alias = {k: dict(v) for k, v in (base.get("alias") or {}).items() if isinstance(v, dict)}
    da_seed, da_run = scansiona(seed), scansiona(runtime)
    for a in sorted(set(da_seed) | set(da_run)):
        copie = [("runtime", da_run.get(a)), ("seed", da_seed.get(a))]
        copie = [(o, v) for o, v in copie if v]
        origine, scelta = max(copie, key=lambda c: (_quando(c[1]), c[1].get("stato") == "ritirato", c[0] == "runtime"))
        vecchia = alias.get(a) or {}
        voce = {k: v for k, v in vecchia.items() if k not in ("stato", "file")}
        voce.update({k: v for k, v in scelta.items() if not k.startswith("_")})
        voce["sinonimi"] = _unisci_liste(*(v.get("sinonimi") for _, v in copie), vecchia.get("sinonimi"))
        if not voce.get("citazione"):
            voce["citazione"] = next((v.get("citazione") for _, v in copie if v.get("citazione")), None) or vecchia.get("citazione")
        if not voce.get("citazione"):
            voce.pop("citazione", None)
        voce["stato"] = "ritirato" if scelta.get("stato") == "ritirato" else "scaricato"
        voce["famiglia"] = str(scelta.get("famiglia") or a)
        voce["verificato_il"] = max(str(vecchia.get("verificato_il") or ""), _d(scelta.get("scaricato_il") or scelta.get("ritirato_il"))) or None
        voce.setdefault("host", (re.match(r"^https?://([^/:]+)", str(scelta.get("url") or "")) or [None, None])[1])
        voce.setdefault("formato", "md")
        voce.setdefault("cadenza_giorni", None)
        voce["_file"] = scelta["_file"]
        voce["_origine"] = origine
        voce["_errori"] = scelta.get("_errori") or []
        alias[a] = voce
    out = {"_meta": base.get("_meta") or {}, "alias": alias}
    _CACHE_REG.clear()
    _CACHE_REG.update(chiave=chiave, valore=out)
    return out


# ---------------------------------------------------------------- dal riferimento alla fonte

def _contiene(q: str, s: str) -> bool:
    """s dentro q a confini di parola: entrambi in forma norm_testo (parole [a-z0-9/] separate da uno spazio)."""
    return bool(s) and f" {s} " in f" {q} "


def trova(riferimento: str, reg: dict = None):
    """La fonte nominata dal riferimento, o None.

    {"esito": "OK", "alias", "famiglia", "voce"} | {"esito": "AMBIGUO", "candidati": [famiglie]} |
    {"esito": "RITIRATO", "alias", "famiglia", "voce"}. Severo: un sinonimo vale solo intero e a confini di
    parola; il codice CNEL e' una chiave esatta; se il miglior punteggio lo raggiungono due famiglie diverse la
    risposta e' AMBIGUO (mai una scelta silenziosa fra due contratti)."""
    reg = reg if reg is not None else registro()
    q = norm_testo(riferimento)
    if not q:
        return None
    voci = reg.get("alias") or {}
    if q.replace(" ", "-") in voci:
        a = q.replace(" ", "-")
        return {**_esito(a, voci[a], reg), "esatto": True}
    q_tok = set(q.split())
    punti = _punti(q, q_tok, {a: v for a, v in voci.items() if v.get("stato") != "ritirato"})
    if not punti:
        punti = _punti(q, q_tok, {a: v for a, v in voci.items() if v.get("stato") == "ritirato"})
    if not punti:
        return None
    migliore = max(p for p, _ in punti.values())
    fams = sorted(f for f, (p, _) in punti.items() if p == migliore)
    if len(fams) > 1:
        return {"esito": "AMBIGUO", "candidati": fams, "riferimento": riferimento}
    a = punti[fams[0]][1]
    fuori = _esito(a, voci[a], reg)
    if fuori.get("esito") == "OK" and fuori["voce"].get("natura") != "accordo-di-rinnovo":
        ed = edizione(fuori["famiglia"], "", reg)          # la famiglia, nell'edizione in vigore oggi
        if ed:
            fuori.update(alias=ed["alias"], voce=ed["voce"])
    return fuori


def _punti(q: str, q_tok: set, voci: dict) -> dict:
    """{famiglia: (punteggio, alias)}: sinonimo intero a confini di parola (10 per parola), tutte le parole del
    sinonimo nel riferimento (10 per parola − 5), riferimento con una cifra contenuto nel sinonimo (3 per
    parola), codice CNEL (1000)."""
    punti = {}

    def segna(fam, alias_, p):
        if p > punti.get(fam, (0, ""))[0]:
            punti[fam] = (p, alias_)

    for a, v in voci.items():
        fam = str(v.get("famiglia") or a)
        cnel = norm_testo(v.get("codice_cnel") or "")
        if cnel and cnel in q_tok:
            segna(fam, a, 1000)
            continue
        forme = [s for s in [v.get("citazione"), *(v.get("sinonimi") or [])] if isinstance(s, str) and sinonimo_valido(s)]
        for s in forme:
            sn = norm_testo(s)
            n = len(sn.split())
            if _contiene(q, sn):
                segna(fam, a, 10 * n)
            elif n >= 2 and set(sn.split()) <= q_tok:
                segna(fam, a, 10 * n - 5)
            elif len(q.split()) >= 2 and any(c.isdigit() for c in q) and _contiene(sn, q):
                segna(fam, a, 3 * len(q.split()))
    return punti


def _esito(alias_: str, voce: dict, reg: dict) -> dict:
    fam = str(voce.get("famiglia") or alias_)
    vive = [a for a, v in (reg.get("alias") or {}).items()
            if str(v.get("famiglia") or a) == fam and v.get("stato") != "ritirato"]
    if voce.get("stato") == "ritirato" and not vive:
        return {"esito": "RITIRATO", "alias": alias_, "famiglia": fam, "voce": voce}
    return {"esito": "OK", "alias": alias_ if voce.get("stato") != "ritirato" else vive[0], "famiglia": fam,
            "voce": voce if voce.get("stato") != "ritirato" else reg["alias"][vive[0]]}


def _d(v) -> str:
    return str(v or "")[:10]


def edizioni(famiglia: str, reg: dict = None) -> list:
    """Le edizioni (testi di base, non ritirati, non accordi di rinnovo) di una famiglia: [(alias, voce)]
    in ordine di decorrenza."""
    reg = reg if reg is not None else registro()
    out = [(a, v) for a, v in (reg.get("alias") or {}).items()
           if str(v.get("famiglia") or a) == famiglia and v.get("stato") == "scaricato"
           and v.get("natura") != "accordo-di-rinnovo"]
    return sorted(out, key=lambda x: (_d(x[1].get("vigenza_da")), _d(x[1].get("data_stipula")), str(x[1].get("scaricato_il") or "")))


def edizione(famiglia: str, data: str = "", reg: dict = None):
    """{"alias", "voce", "avvisi", "anteriore", "scaduta"} dell'edizione in vigore alla data (oggi se vuota),
    o None se la famiglia non ha testi."""
    reg = reg if reg is not None else registro()
    eds = edizioni(famiglia, reg)
    if not eds:
        return None
    d = _d(data) or _dt.date.today().isoformat()
    avvisi = []
    in_vigore = [e for e in eds if _d(e[1].get("vigenza_da")) <= d]
    anteriore = False
    if in_vigore:
        a, v = in_vigore[-1]
    else:
        a, v = eds[0]
        anteriore = True
        avvisi.append(f"nessuna edizione in vigore al {d}: la piu' vecchia nel corpus decorre dal {_d(v.get('vigenza_da'))}")
    scaduta = bool(_d(v.get("vigenza_a")) and _d(v.get("vigenza_a")) < d)
    if scaduta:
        avvisi.append(f"edizione scaduta il {_d(v.get('vigenza_a'))}: verificare rinnovo o ultrattivita' alla data {d}")
    if data and _d(v.get("data_stipula")) and d < _d(v.get("data_stipula")):
        avvisi.append(f"edizione stipulata il {_d(v.get('data_stipula'))}, dopo la data {d}: decorrenza retroattiva da verificare")
    return {"alias": a, "voce": v, "avvisi": avvisi, "anteriore": anteriore, "scaduta": scaduta}


def rinnovi(famiglia: str, data: str, dopo: str = "", reg: dict = None) -> list:
    """Accordi di rinnovo della famiglia in vigore alla data e successivi alla decorrenza `dopo`: [(alias, voce)]."""
    reg = reg if reg is not None else registro()
    d = _d(data) or _dt.date.today().isoformat()
    return [(a, v) for a, v in (reg.get("alias") or {}).items()
            if str(v.get("famiglia") or a) == famiglia and v.get("stato") == "scaricato"
            and v.get("natura") == "accordo-di-rinnovo" and _d(v.get("vigenza_da")) <= d
            and _d(v.get("vigenza_da")) > _d(dopo)]


def _file(voce: dict):
    f = voce.get("_file")
    if f:
        return Path(f)
    rel = voce.get("file")
    return (WIKI / "normativa" / rel) if rel else None


def articolo_di(alias_: str, token: str, reg: dict = None) -> dict:
    """L'articolo `token` dell'edizione `alias_` (senza scelta alla data)."""
    reg = reg if reg is not None else registro()
    voce = (reg.get("alias") or {}).get(alias_)
    if not voce:
        return {"esito": "NON_TROVATA", "motivo": f"alias «{alias_}» non nel registro"}
    base = {"alias": alias_, "famiglia": str(voce.get("famiglia") or alias_), "nome": voce.get("nome"),
            "fonte": voce.get("fonte") or voce.get("host"), "url": voce.get("url"), "scaricato_il": voce.get("scaricato_il"),
            "vigente_al": voce.get("vigente_al") or _d(voce.get("scaricato_il")) or None,
            "vigenza_da": voce.get("vigenza_da"), "vigenza_a": voce.get("vigenza_a"),
            "fedelta": voce.get("fedelta") or "non_verificata", "estratto": bool(voce.get("estratto")),
            "struttura": voce.get("struttura") or "articoli", "genere": voce.get("genere"), "origine": voce.get("_origine")}
    if voce.get("stato") == "ritirato":
        return {**base, "esito": "RITIRATO", "motivo": f"fonte ritirata il {voce.get('ritirato_il')}: {voce.get('motivo')}"}
    f = _file(voce)
    if not f or not f.exists():
        return {**base, "esito": "NON_DISPONIBILE", "motivo": f"testo di «{alias_}» non presente in locale"}
    doc = leggi(f)
    corpo = doc["corpo"]
    tok = norm_token(token)
    arts = [x for x in articoli(corpo) if x[0] == tok]
    base["file"] = str(f)
    if base["struttura"] != "articoli" and not arts:
        return {**base, "esito": "NON_ARTICOLATA", "motivo": f"«{voce.get('nome')}» non e' diviso per articoli: chiedi una sezione"}
    if not arts:
        motivo = (f"art. {tok} non presente in {voce.get('nome')} (testo del {base['scaricato_il']}): "
                  "la numerazione puo' essere cambiata — non citarlo a memoria")
        if base["estratto"]:
            motivo += "; il file e' un ESTRATTO del documento: l'articolo puo' stare nella parte non riportata"
        return {**base, "esito": "SEZIONE_NON_TROVATA", "motivo": motivo}
    t, rub, i, j = arts[0]
    blocco = corpo[i:j].strip()
    titolo, _, resto = blocco.partition("\n")
    testo = titolo.lstrip("# ").strip() + "\n" + resto.strip()
    return {**base, "esito": "OK", "articolo": tok, "rubrica": rub, "testo": testo, "caratteri": len(testo)}


def articolo(riferimento: str, token: str, data_evento: str = "", reg: dict = None) -> dict:
    """L'articolo `token` della fonte nominata dal riferimento, nell'edizione in vigore alla data dell'evento."""
    reg = reg if reg is not None else registro()
    hit = trova(riferimento, reg)
    if not hit:
        return {"esito": "NON_TROVATA", "motivo": f"nessuna fonte di secondo livello riconosciuta in «{riferimento}»"}
    if hit["esito"] == "AMBIGUO":
        return {"esito": "AMBIGUO", "candidati": hit["candidati"],
                "motivo": f"«{riferimento}» corrisponde a piu' fonti ({', '.join(hit['candidati'])}): precisa quale"}
    if hit["esito"] == "RITIRATO":
        return articolo_di(hit["alias"], token, reg)
    if hit.get("esatto"):                          # un'edizione nominata per alias: quella, senza scelta alla data
        out = articolo_di(hit["alias"], token, reg)
        if out.get("esito") == "OK" and out.get("fedelta") != "verificata":
            out["avvisi"] = ["testo non confrontato con il documento d'origine (fedelta non verificata): rileggerlo sulla fonte"]
        return out
    fam = hit["famiglia"]
    ed = edizione(fam, data_evento, reg) if hit["voce"].get("natura") != "accordo-di-rinnovo" else None
    alias_ = ed["alias"] if ed else hit["alias"]
    out = articolo_di(alias_, token, reg)
    avvisi = list(ed["avvisi"]) if ed else []
    out["scaduta"] = bool(ed and ed["scaduta"])
    out["anteriore"] = bool(ed and ed["anteriore"])
    if ed:
        mod = [a for a, v in rinnovi(fam, data_evento, ed["voce"].get("vigenza_da"), reg)
               if norm_token(token) in [norm_token(x) for x in v.get("articoli_modificati") or []]]
        if mod:
            out["modificato_da"] = mod
            avvisi.append(f"art. {norm_token(token)} modificato da {', '.join(mod)}: il testo qui sotto e' quello dell'edizione di base")
    if out.get("fedelta") != "verificata":
        avvisi.append("testo non confrontato con il documento d'origine (fedelta non verificata): rileggerlo sulla fonte")
    if avvisi:
        out["avvisi"] = avvisi
    return out


def chiave(riferimento: str, token: str, reg: dict = None):
    """La chiave canonica di un articolo di secondo livello per ledger e gate: «sl:<famiglia>:<token>», o None."""
    hit = trova(riferimento, reg)
    if not hit or hit.get("esito") != "OK":
        return None
    return f"sl:{hit['famiglia']}:{norm_token(token)}"


# ---------------------------------------------------------------- per il manifest del corpus pubblico

def voci_manifest(cartella: Path):
    """({alias: voce del manifest}, {nome file: [errori]}) per i file di una cartella: i file con errori restano
    fuori (quarantena) senza fermare il resto."""
    voci, scartati = {}, {}
    cartella = Path(cartella)
    if not cartella.is_dir():
        return voci, scartati
    for p in sorted(cartella.iterdir()):
        if not p.is_file() or p.name.startswith((".", "_")):
            continue
        v = valida(p)
        if v["errori"]:
            scartati[p.name] = v["errori"][:10]
            continue
        h = v["intestazione"]
        voce = {"file": p.name, "sha256": v["sha256"], "byte": v["byte"],
                "famiglia": h.get("famiglia"), "genere": h.get("genere"), "nome": h.get("nome"),
                "scaricato_il": h.get("scaricato_il"), "articoli": v["articoli"]}
        for k in ("stato", "natura", "vigenza_da", "vigenza_a", "codice_cnel", "fedelta", "ritirato_il"):
            if h.get(k):
                voce[k] = h[k]
        voci[p.stem] = voce
    return voci, scartati


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fonti di secondo livello: validazione, registro, ricerca.")
    ap.add_argument("--valida", nargs="+", metavar="FILE")
    ap.add_argument("--elenco", action="store_true")
    ap.add_argument("--trova", metavar="RIFERIMENTO")
    ap.add_argument("--data", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.valida:
        ko = 0
        esiti = {}
        for f in a.valida:
            v = valida(Path(f))
            esiti[f] = {k: v[k] for k in ("errori", "avvisi", "articoli")}
            ko += bool(v["errori"])
        if a.json:
            print(json.dumps(esiti, ensure_ascii=False, indent=1))
        else:
            for f, v in esiti.items():
                print(f"{'ERRORI' if v['errori'] else 'OK'} {f} · {v['articoli']} articoli")
                for e in v["errori"]:
                    print(f"  ✗ {e}")
                for e in v["avvisi"]:
                    print(f"  ⚠ {e}")
        return 1 if ko else 0
    if a.elenco:
        reg = registro()
        righe = []
        for k, v in sorted((reg.get("alias") or {}).items()):
            righe.append({"alias": k, "famiglia": v.get("famiglia") or k, "stato": v.get("stato"),
                          "vigenza": f"{_d(v.get('vigenza_da')) or '…'} → {_d(v.get('vigenza_a')) or '…'}",
                          "origine": v.get("_origine") or "registro", "fedelta": v.get("fedelta")})
        if a.json:
            print(json.dumps(righe, ensure_ascii=False, indent=1))
        else:
            for r in righe:
                print(f"{r['alias']:<34} {r['famiglia']:<28} {str(r['stato']):<13} {r['vigenza']:<25} {r['origine']:<8} {r['fedelta'] or ''}")
        return 0
    if a.trova:
        hit = trova(a.trova)
        m = re.search(rf"\bart(?:icolo|\.)?\s*(\d+(?:[\s-]*(?:{_SUFFISSI}))?)", a.trova, re.I)
        r = articolo(a.trova, m.group(1), a.data) if (m and hit and hit.get("esito") == "OK") else \
            ({k: v for k, v in hit.items() if k != "voce"} if hit else {"esito": "NON_TROVATA"})
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r.get("esito") == "OK" else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
