#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IL CONTROLLO MECCANICO DELLE SCHEDE DEL MEMENTO LAVORO (v0.36).

PERCHE'
-------
Le schede del memento (`wiki-studio/lavoro/memento/<id>.md`) sono mappe per istituto: quali norme leggere alla
data, cosa cercare nel contratto collettivo, quale prassi, quali termini, quali insidie per il lavoratore. Le
scrive e le aggiorna un modello; questo script decide, senza modello, se una scheda si puo' pubblicare:

  - intestazione completa, riga del Principio Zero, sezioni al loro posto;
  - ogni norma dichiarata (`norme: ["l-604-1966:6", …]`) esiste nel corpus e non e' abrogata, e la sua impronta
    e' quella del testo di oggi (se il testo cambia, la scheda torna «da ricontrollare»);
  - ogni norma citata nel testo («art. 6 L. 604/1966») e' fra quelle dichiarate, cioe' verificate;
  - ogni numero con un'unita' (giorni, mesi, anni, dipendenti, mensilita', %) sta su una riga che cita una norma e
    compare nel testo di quella norma: un termine sbagliato non passa;
  - la prassi citata e' nell'indice della prassi (o in quella curata, con l'indirizzo), i numeri annuali sono chiavi
    di dati-lavoro.json con la loro fonte;
  - niente estremi di pronunce, niente importi in euro, niente comandi di script.

Dopo il passo del modello nel workflow (`--dopo-claude`) rimette com'erano i file fuori dall'area ammessa, sigilla le
schede che passano, rimette com'erano quelle che non passano (marcandole «da ricontrollare») e scrive la issue.

Uso:
  python3 scripts/memento_verifica.py --valida wiki-studio/lavoro/memento/licenziamento-gmo.md [...]
  python3 scripts/memento_verifica.py --sigilla wiki-studio/lavoro/memento/licenziamento-gmo.md [...]
  python3 scripts/memento_verifica.py --indice
  python3 scripts/memento_verifica.py --leggi l-604-1966:6          (il testo dell'articolo, per chi scrive)
  python3 scripts/memento_verifica.py --dopo-claude --triage T.json --esiti E.json [--github-output F] [--issue F]
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codice_locale as cl  # noqa: E402
import secondo_livello as sl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
AREE = ("qualificazione", "tipologie", "retribuzione", "tempo-e-assenze", "rapporto", "cessazione", "previdenza", "tutela")
SEZIONI = ("Norme da leggere alla data", "Cosa cercare nel CCNL", "Prassi amministrativa", "Numeri",
           "Termini e decadenze", "Temi di giurisprudenza", "Insidie lato lavoratore", "Documenti e domande al cliente")
OBBLIGATORI = ("id", "titolo", "area", "istituti", "parole_chiave", "norme", "prassi", "numeri", "stato")
STATI = ("verificata", "da_ricontrollare", "bozza")
PRINCIPIO_ZERO = "> **Uso di questo file (Principio Zero)**"
#: i soli file che il passo del modello puo' toccare (il resto si rimette com'era)
AMMESSI = ("wiki-studio/lavoro/memento/", "wiki-studio/lavoro/dati/dati-lavoro.json", "wiki-studio/lavoro/prassi/curata.json")
#: parole (o coppie di parole) che nel repo pubblico non devono comparire: solo le impronte (come in corpus_contribuisci)
VIETATI_SHA = frozenset({
    "1a60c5f2167e15c29a9be3496b45e8839c7021896e616e5a6529ab10382ab116",
    "f1817f7333892539d54f0bc58653999a31d6c7274f806e45080c6255c63a6333",
    "ffe138c1680e8e3c824daa5c3eeba673825b9a0092866608b1f4f3e3212378d1",
    "13cbfd2790348c84875ada40c7a7ada348e74d7766b49d03aa4d69c779fc0581",
})

# ---------------------------------------------------------------- forme vietate

#: estremi di pronunce: le schede indicano i TEMI, la giurisprudenza la trova e la verifica la pipeline
RX_DECISIONI = re.compile(
    r"\bCass(?:azione)?\b\.?\s*(?:civ\.?|lav\.?|pen\.?|sez\.?|s\.?\s*u\.?|ss\.?\s*uu\.?|n\.|ord|sent|,|\d)"
    r"|\bSez\.\s*(?:L|lav|lavoro|U|Un|I{1,3}|IV|V|VI)\b"
    r"|\bSS\.?\s*UU\b|\bS\.U\.(?=\s|,|$)"
    r"|\bC\.\s*[Cc]ost\.|\bCorte\s+cost(?:ituzionale)?\.?,?\s*(?:[^.\n]{0,40}?)\b(?:n\.|sent|ord)"
    r"|\bTrib(?:unale)?\.\s+[A-Z]|\bApp(?:ello)?\.\s+[A-Z]|\bC\.\s*App\."
    r"|\bCons(?:iglio)?\.?\s*(?:di\s+)?Stato\b[^.\n]{0,20}\bn\."
    r"|\bT\.?A\.?R\.?\s+[A-Z][a-z]"
    r"|\bCGUE\b|\bC-\d{1,4}/\d{2}\b|\bECLI\b"
    r"|\b(?:sent(?:enza)?|ord(?:inanza)?)\.?\s+n\.\s*\d"
    r"|\bn\.\s*\d{3,6}\s*/\s*(?:19|20)\d{2}\b[^\n]{0,15}\b(?:Cass|sez\.|sent\.|sentenza|ord\.|ordinanza)", re.I)
RX_EURO = re.compile(r"€|\bEUR\b|\beuro\b|\d[\d.]*,\d{2}\b", re.I)
RX_COMANDO = re.compile(r"python3|scripts/|\.py\b|```")

# ---------------------------------------------------------------- citazioni nel testo

#: le forme lunghe prima (altrimenti «ter» si prende l'inizio di «terdecies»)
_SUFF = (r"(?:undecies|duodecies|terdecies|quaterdecies|quinquiesdecies|sexiesdecies|septiesdecies|"
         r"bis|ter|quater|quinquies|sexies|septies|octies|novies|nonies|decies)")
_ATTO = (r"(?P<atto>c\.\s?c\.(?!n)|c\.\s?p\.\s?c\.|c\.\s?p\.(?!\s?c\.)|Cost\.|disp\.\s*att\.\s*c\.\s?p\.\s?c\.|St(?:at)?\.\s*lav\.|"
         r"(?:L\.|l\.|legge|D\.\s?Lgs\.|d\.\s?lgs\.|D\.\s?L\.|d\.\s?l\.|D\.\s?P\.\s?R\.|d\.\s?p\.\s?r\.)\s*(?:n\.\s*)?\d{1,4}/\d{4})")
RX_CITAZIONE = re.compile(
    r"\bart(?:t)?\.\s*(?P<arts>\d{1,4}(?:[-\s]?" + _SUFF + r")?(?:\s*(?:,|e|ed|-)\s*\d{1,4}(?:[-\s]?" + _SUFF + r")?)*)"
    r"(?P<mezzo>[^;()\n]{0,45}?)\b" + _ATTO, re.I)
_FORME_ATTO = {"c.c.": "cc", "c.p.c.": "cpc", "c.p.": "cp", "cost.": "cost", "disp. att. c.p.c.": "disp-att-cpc", "st. lav.": "l-300-1970",
               "stat. lav.": "l-300-1970"}
RX_UNITA = re.compile(
    r"(?<![\w/.,])(?P<num>\d{1,4}(?:[.,]\d+)?)\s*(?P<unita>(?:giorni|giorno|mesi|mese|anni|anno|ore|settimane|"
    r"dipendenti|lavoratori|mensilit[àa]|per\s+cento)\b|%)", re.I)
RX_PRASSI_TESTO = re.compile(
    r"(?i)\b(?P<tipo>circ(?:olare)?|mess(?:aggio)?|nota|interpello)\.?\s+(?:(?:in\s+materia\s+di|sulla)\s+sicurezza\s+)?"
    r"(?P<ente>INPS|INL|INAIL|Ministero(?:\s+del)?\s+lavoro|MLPS)?"
    r"\s*n\.\s*(?P<num>\d{1,5})\s*(?:/|del(?:l')?\s+(?:\d{1,2}\s+\w+\s+)?)(?P<anno>(?:19|20)\d{2})")
_NUMERI_PAROLE = {}


def _parole_numero(n: int) -> list:
    """Le scritture in lettere di un numero da 1 a 999 («sessanta», «centottanta», «duecentosettanta»)."""
    if n in _NUMERI_PAROLE:
        return _NUMERI_PAROLE[n]
    u = ["", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci", "undici", "dodici",
         "tredici", "quattordici", "quindici", "sedici", "diciassette", "diciotto", "diciannove"]
    d = ["", "", "venti", "trenta", "quaranta", "cinquanta", "sessanta", "settanta", "ottanta", "novanta"]

    def due_cifre(x):
        if x < 20:
            return u[x]
        dec, un = divmod(x, 10)
        base = d[dec]
        if un in (1, 8):
            base = base[:-1]
        return base + ("tré" if un == 3 else u[un])

    if n < 100:
        s = due_cifre(n)
    else:
        c, r = divmod(n, 100)
        cento = "cento" if c == 1 else u[c] + "cento"
        if r and r // 10 == 8:
            cento = cento[:-1]
        s = cento + due_cifre(r)
    forme = {s, s.replace("tré", "tre"), s.replace("tré", "tre'")}
    if n == 1:
        forme |= {"un", "una"}
    _NUMERI_PAROLE[n] = sorted(f for f in forme if f)
    return _NUMERI_PAROLE[n]


def _piano(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).lower().replace("’", "'").split())


def slug_atto(atto: str) -> str:
    """Lo slug del corpus per la forma dell'atto nel testo («L. 604/1966», «D.Lgs. 23/2015», «c.c.»), o ''."""
    a = re.sub(r"\s+", " ", atto.strip().lower())
    a = re.sub(r"\bn\.\s*", "", a)
    a = re.sub(r"^legge\s+", "l. ", a)
    a = a.replace("d. lgs.", "d.lgs.").replace("d. l.", "d.l.").replace("d. p. r.", "d.p.r.").replace("c. c.", "c.c.")
    a = a.replace("c. p. c.", "c.p.c.").replace("c.p. c.", "c.p.c.")
    if a in _FORME_ATTO:
        return _FORME_ATTO[a]
    return cl.ALIAS.get(a) or cl.ALIAS.get(a.replace(" ", "")) or ""


def righe_logiche(testo: str) -> list:
    """Le righe come le legge chi scrive: una voce d'elenco o un paragrafo che va a capo e' una riga sola (una citazione
    spezzata fra due righe fisiche resta una citazione)."""
    unito = re.sub(r"\n(?![ \t]*(?:[-*>#]|\d+[.)]\s|\n|$))[ \t]*", " ", testo)
    return unito.split("\n")


def citazioni(testo: str) -> list:
    """[(slug, articolo, forma)] delle citazioni «art. N <atto>» nel testo (anche «artt. 2118 e 2119 c.c.»)."""
    out = []
    for m in RX_CITAZIONE.finditer(testo):
        slug = slug_atto(m.group("atto"))
        for a in re.split(r"\s*(?:,|\be\b|\bed\b)\s*", m.group("arts")):
            a = a.strip(" -")
            if a:
                out.append((slug, cl._norm_token(a), m.group(0)))
    return out


# ---------------------------------------------------------------- lettura

def leggi_scheda(p: Path) -> dict:
    testo = sl.decodifica(Path(p).read_bytes())
    blocco, corpo = sl.dividi(testo)
    head, errori, grezze = sl.parse_intestazione(blocco) if blocco is not None else ({}, ["intestazione assente"], [])
    for k in grezze:
        errori.append(f"intestazione: «{k}» non e' un valore JSON")
    return {"intestazione": head, "corpo": corpo, "errori": errori}


def scrivi_scheda(p: Path, head: dict, corpo: str) -> None:
    chiavi = list(OBBLIGATORI) + [k for k in ("motivi", "verificato_il", "corpus_al", "impronte", "calcoli") if k in head]
    chiavi += sorted(k for k in head if k not in chiavi)
    testa = "---\n" + "".join(f"{k}: {json.dumps(head[k], ensure_ascii=False)}\n" for k in chiavi if k in head) + "---\n"
    Path(p).write_text(testa + corpo.lstrip("\n"), encoding="utf-8")


def _sezioni(corpo: str) -> dict:
    """{titolo della sezione (## …): testo}."""
    out, cur = {}, None
    for riga in corpo.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", riga)
        if m:
            cur = m.group(1)
            out[cur] = ""
        elif cur is not None:
            out[cur] += riga + "\n"
    return out


def norma(chiave: str) -> dict:
    """«slug:art» → {esito, testo, abrogato, impronta, rubrica} dal corpus locale."""
    slug, _, art = str(chiave).partition(":")
    if slug not in cl.CODICI:
        return {"esito": "ATTO_NON_NEL_CORPUS", "chiave": chiave}
    r = cl.articolo(art, slug)
    if r.get("verdetto") != "OK":
        return {"esito": "ARTICOLO_NON_TROVATO", "chiave": chiave, "motivo": r.get("motivo")}
    testo = r.get("testo") or ""
    try:                      # l'impronta guarda la norma, non le note di redazione (che cambiano spesso)
        import corpus_diff as cd
        impronta = cl.hash_testo(cd.solo_norma(testo))
    except Exception:
        impronta = cl.hash_testo(testo)
    return {"esito": "OK", "chiave": chiave, "testo": testo, "abrogato": bool(r.get("abrogato")),
            "impronta": impronta, "rubrica": r.get("rubrica")}


def _solo_norma(testo: str) -> str:
    """Il testo senza le note di redazione di normattiva (date, numeri di note e di leggi che non sono la regola)."""
    try:
        import corpus_diff as cd
        return cd.solo_norma(testo)
    except Exception:
        return testo


def _leggi_json(p: Path, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def area_lavoro(radice: Path = ROOT) -> Path:
    """Nel repo pubblico: <radice>/wiki-studio/lavoro. Nel plugin: la copia sincronizzata se c'e', altrimenti il seme."""
    return Path(radice) / "wiki-studio" / "lavoro"


def prassi_note(radice: Path = ROOT) -> set:
    base = area_lavoro(radice) / "prassi"
    ids = set(((_leggi_json(base / "indice.json", {}) or {}).get("voci") or {}).keys())
    for v in ((_leggi_json(base / "curata.json", {}) or {}).get("voci") or {}).items():
        if str((v[1] or {}).get("url") or "").startswith("https://"):
            ids.add(v[0])
    return ids


def numeri_noti(radice: Path = ROOT) -> dict:
    return ((_leggi_json(area_lavoro(radice) / "dati" / "dati-lavoro.json", {}) or {}).get("voci")) or {}


def _vietati(testo: str) -> list:
    ws = re.findall(r"[a-z0-9]+", _piano(testo))
    out = []
    for i, w in enumerate(ws):
        for forma in (w, f"{w} {ws[i + 1]}" if i + 1 < len(ws) else None):
            if forma and hashlib.sha256(forma.encode("utf-8")).hexdigest() in VIETATI_SHA:
                out.append("(nome vietato)")
    return out


def _id_prassi(m) -> list:
    """Gli id possibili della prassi citata nel testo (gli interpelli del Ministero hanno due serie: generale e
    sicurezza, art. 12 D.Lgs. 81/2008, con numerazioni proprie)."""
    tipo = m.group("tipo").lower()
    ente = (m.group("ente") or "").lower()
    if tipo.startswith("interpello"):
        return [f"minlav:interpello:{m.group('anno')}:{m.group('num')}",
                f"minlav:interpello-sicurezza:{m.group('anno')}:{m.group('num')}"]
    tipo = "circolare" if tipo.startswith("circ") else ("messaggio" if tipo.startswith("mess") else "nota")
    ente = "minlav" if ente.startswith(("ministero", "mlps")) else ente
    return [f"{ente}:{tipo}:{m.group('anno')}:{m.group('num')}"] if ente else []


# ---------------------------------------------------------------- validazione

def valida(p: Path, radice: Path = ROOT, cache_norme: dict = None) -> dict:
    """{errori, avvisi, impronte}: errori = la scheda non si pubblica."""
    p = Path(p)
    cache_norme = cache_norme if cache_norme is not None else {}
    try:
        s = leggi_scheda(p)
    except (OSError, UnicodeDecodeError) as e:
        return {"errori": [f"illeggibile: {e.__class__.__name__}"], "avvisi": [], "impronte": {}}
    h, corpo = s["intestazione"], s["corpo"]
    errori, avvisi = list(s["errori"]), []
    for k in OBBLIGATORI:
        if k not in h:
            errori.append(f"intestazione: manca «{k}»")
    if h.get("id") != p.stem:
        errori.append(f"id «{h.get('id')}» diverso dal nome del file «{p.stem}»")
    if h.get("area") and h["area"] not in AREE:
        errori.append(f"area «{h.get('area')}» non fra {', '.join(AREE)}")
    if h.get("stato") and h["stato"] not in STATI:
        errori.append(f"stato «{h.get('stato')}» non fra {', '.join(STATI)}")
    for k in ("istituti", "parole_chiave", "norme", "prassi", "numeri"):
        if k in h and not (isinstance(h[k], list) and all(isinstance(x, str) for x in h[k])):
            errori.append(f"«{k}» deve essere una lista di stringhe")
    if PRINCIPIO_ZERO not in corpo:
        errori.append("manca la riga del Principio Zero in testa alla scheda")
    sez = _sezioni(corpo)
    for t in SEZIONI:
        if not any(x.startswith(t) for x in sez):
            errori.append(f"manca la sezione «## {t}»")
    # norme dichiarate
    impronte = {}
    dichiarate = set()
    for chiave in h.get("norme") or []:
        if chiave not in cache_norme:
            cache_norme[chiave] = norma(chiave)
        n = cache_norme[chiave]
        if n["esito"] != "OK":
            errori.append(f"norma {chiave}: {n['esito']}" + (f" ({n.get('motivo')})" if n.get("motivo") else ""))
            continue
        if n["abrogato"]:
            errori.append(f"norma {chiave}: articolo abrogato")
        impronte[chiave] = n["impronta"]
        slug, _, art = chiave.partition(":")
        dichiarate.add((slug, cl._norm_token(art)))
    # norme citate nel testo (righe logiche: una citazione che va a capo conta)
    for slug, art, forma in citazioni("\n".join(righe_logiche(corpo))):
        if not slug:
            errori.append(f"atto non riconosciuto in «{forma.strip()}» (forme: «L. 604/1966», «D.Lgs. 23/2015», «c.c.»)")
        elif (slug, art) not in dichiarate:
            errori.append(f"«{forma.strip()}» citato nel testo ma non dichiarato in «norme» ({slug}:{art})")
    # numeri con unita': sulla riga di una norma dichiarata, e nel suo testo
    for riga in righe_logiche(corpo):
        unita = list(RX_UNITA.finditer(riga))
        if not unita:
            continue
        citate = [f"{s_}:{a_}" for s_, a_, _f in citazioni(riga) if s_]
        testi = " ".join(_piano(_solo_norma(cache_norme.get(c, {}).get("testo", ""))) for c in citate if c in cache_norme)
        for m in unita:
            num = m.group("num").replace(",", ".")
            if not citate:
                errori.append(f"«{m.group(0)}» senza la norma che lo stabilisce sulla stessa riga: «{riga.strip()[:90]}»")
                continue
            forme = {m.group("num"), num}
            try:
                n = int(float(num))
                if float(num) == n and 0 < n < 1000:
                    forme |= set(_parole_numero(n))
            except ValueError:
                pass
            if not any(re.search(r"(?<![\d.,])" + re.escape(_piano(f)) + r"(?![\d])", testi) for f in forme):
                errori.append(f"«{m.group(0)}» non compare nel testo di {', '.join(citate)}: «{riga.strip()[:90]}»")
    # prassi e numeri
    note = prassi_note(radice)
    for pid in h.get("prassi") or []:
        if pid not in note:
            errori.append(f"prassi «{pid}» non nell'indice della prassi (ne' in quella curata con l'indirizzo)")
    for m in RX_PRASSI_TESTO.finditer(corpo):
        ids = _id_prassi(m)
        if ids and not any(i in (h.get("prassi") or []) for i in ids):
            errori.append(f"«{m.group(0).strip()}» citata nel testo ma non dichiarata in «prassi» ({' o '.join(ids)})")
    nn = numeri_noti(radice)
    for k in h.get("numeri") or []:
        v = nn.get(k)
        if not v:
            errori.append(f"numero «{k}» non fra le voci di dati-lavoro.json")
        elif not (v.get("serie") or {}):
            avvisi.append(f"numero «{k}»: nessun valore ancora verificato")
    # forme vietate
    for m in RX_DECISIONI.finditer(corpo):
        errori.append(f"estremi di una pronuncia («{m.group(0).strip()}»): nelle schede solo i temi")
    for m in RX_EURO.finditer(corpo):
        errori.append(f"importo («{m.group(0)}»): i numeri annuali stanno in dati-lavoro.json, qui solo la chiave")
    if RX_COMANDO.search(corpo):
        errori.append("comandi o blocchi di codice nella scheda: le istruzioni le genera memento.py")
    if _vietati(json.dumps(h, ensure_ascii=False) + corpo):
        errori.append("nome che il repo pubblico non deve contenere")
    return {"errori": errori, "avvisi": avvisi, "impronte": impronte}


def _manifest_generato(radice: Path) -> str:
    m = _leggi_json(Path(radice) / "manifest.json", {}) or _leggi_json(ROOT / "wiki-studio" / "normativa" / "corpus-manifest.json", {}) or {}
    return str(m.get("generato_il") or "")


def sigilla(p: Path, radice: Path = ROOT, oggi: str = "", cache_norme: dict = None) -> dict:
    """Valida e, se passa, scrive impronte, data, stato «verificata»."""
    v = valida(p, radice, cache_norme)
    if v["errori"]:
        return {"esito": "RESPINTA", **v}
    s = leggi_scheda(p)
    h = s["intestazione"]
    h.update(stato="verificata", impronte=v["impronte"], verificato_il=oggi or _dt.date.today().isoformat(),
             corpus_al=_manifest_generato(radice) or None)
    h.pop("motivi", None)
    if not h.get("corpus_al"):
        h.pop("corpus_al", None)
    scrivi_scheda(p, h, s["corpo"])
    return {"esito": "SIGILLATA", **v}


def marca(p: Path, motivi: list) -> None:
    """Stato «da_ricontrollare» con i motivi (senza toccare il resto)."""
    s = leggi_scheda(p)
    h = s["intestazione"]
    vecchi = [m for m in (h.get("motivi") or []) if isinstance(m, str)]
    h.update(stato="da_ricontrollare", motivi=list(dict.fromkeys(vecchi + [str(m)[:300] for m in motivi]))[:20])
    scrivi_scheda(p, h, s["corpo"])


def indice(radice: Path = ROOT) -> dict:
    """memento/indice.json: le intestazioni di tutte le schede (per la ricerca e il triage)."""
    d = area_lavoro(radice) / "memento"
    voci = {}
    for p in sorted(d.glob("*.md")) if d.is_dir() else []:
        try:
            h = leggi_scheda(p)["intestazione"]
        except (OSError, UnicodeDecodeError):
            continue
        voci[p.stem] = {k: h.get(k) for k in ("titolo", "area", "istituti", "parole_chiave", "norme", "prassi", "numeri",
                                                "stato", "motivi", "verificato_il") if h.get(k) not in (None, [], "")}
    out = {"_meta": {"descrizione": "schede del memento lavoro: mappe, non fonti", "schede": len(voci),
                     "aggiornato_il": _dt.date.today().isoformat()}, "schede": voci}
    if d.is_dir():
        (d / "indice.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- dopo il passo del modello (workflow)

def _git(radice: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(radice), *args], capture_output=True, text=True, encoding="utf-8")


def toccati(radice: Path) -> list:
    """[(stato git, percorso)] dei file modificati o nuovi rispetto all'ultimo commit."""
    r = _git(radice, "status", "--porcelain", "--untracked-files=all")
    out = []
    for riga in r.stdout.splitlines():
        if len(riga) > 3:
            out.append((riga[:2], riga[3:].strip().strip('"')))
    return out


def _ripristina(radice: Path, stato: str, rel: str) -> None:
    if "?" in stato:
        try:
            (Path(radice) / rel).unlink()
        except OSError:
            pass
    else:
        _git(radice, "checkout", "--", rel)


def dopo_claude(radice: Path, triage: dict, esiti: dict, oggi: str = "", verifica_numero=None) -> dict:
    """Il cancello dopo il passo del modello. {respinte, sigillate, ripristinati, issue}."""
    radice = Path(radice)
    oggi = oggi or _dt.date.today().isoformat()
    out = {"respinte": [], "sigillate": [], "ripristinati": [], "numeri": [], "issue": []}
    cache = {}
    stato_git = toccati(radice)
    # 1) tutto cio' che sta fuori dall'area ammessa torna com'era
    for st, rel in stato_git:
        if not rel.startswith(AMMESSI):
            _ripristina(radice, st, rel)
            out["ripristinati"].append(rel)
    memento = area_lavoro(radice) / "memento"
    # 2) le schede toccate: sigillo o ripristino
    toccate = {Path(rel).stem: (st, rel) for st, rel in stato_git
               if rel.startswith("wiki-studio/lavoro/memento/") and rel.endswith(".md")}
    for sid, (st, rel) in sorted(toccate.items()):
        r = sigilla(radice / rel, radice, oggi, cache)
        if r["esito"] == "SIGILLATA":
            out["sigillate"].append(sid)
            continue
        out["respinte"].append(sid)
        out["issue"].append(f"- **{sid}** respinta dal controllo: " + "; ".join(r["errori"][:6]))
        _ripristina(radice, st, rel)
        if (radice / rel).exists():
            marca(radice / rel, [f"riscrittura del {oggi} respinta: {e}" for e in r["errori"][:3]])
    # 3) le schede del triage che il modello dichiara invariate: si risigillano se passano
    for sid, motivi in sorted((triage.get("schede") or {}).items()):
        if sid in toccate:
            continue
        p = memento / f"{sid}.md"
        e = (esiti or {}).get(sid) or {}
        if p.exists() and str(e.get("esito") or "") == "invariata":
            r = sigilla(p, radice, oggi, cache)
            if r["esito"] == "SIGILLATA":
                out["sigillate"].append(sid)
                continue
            out["respinte"].append(sid)
            out["issue"].append(f"- **{sid}** dichiarata invariata ma non passa il controllo: " + "; ".join(r["errori"][:6]))
            marca(p, [f"controllo del {oggi}: {x}" for x in r["errori"][:3]])
        elif p.exists():
            marca(p, motivi)
            out["issue"].append(f"- **{sid}** non rivista: " + "; ".join(str(m) for m in motivi[:3]))
    # 4) i numeri annuali: struttura e valori nuovi sulla fonte, altrimenti il file torna com'era
    rel_dati = "wiki-studio/lavoro/dati/dati-lavoro.json"
    if any(rel == rel_dati for _, rel in stato_git):
        import dati_lavoro as dl
        nuovo = _leggi_json(radice / rel_dati, {}) or {}
        prima = json.loads(_git(radice, "show", f"HEAD:{rel_dati}").stdout or "{}") if _git(radice, "cat-file", "-e", f"HEAD:{rel_dati}").returncode == 0 else {}
        errori = dl.controlla(nuovo)
        for k, v in (nuovo.get("voci") or {}).items():
            for anno, s_ in (v.get("serie") or {}).items():
                vecchio = ((((prima.get("voci") or {}).get(k) or {}).get("serie")) or {}).get(anno)
                if vecchio == s_ or s_.get("metodo") != "estratto":
                    continue
                r = (verifica_numero or dl.verifica_voce)(s_)
                out["numeri"].append(f"{k} {anno}: {r['esito']}")
                if r["esito"] != "OK":
                    errori.append(f"{k} {anno}: valore non trovato sulla fonte ({r['esito']})")
        if errori:
            _ripristina(radice, "M" if prima else "??", rel_dati)
            out["issue"].append("- **dati-lavoro.json** ripristinato: " + "; ".join(errori[:6]))
            out["respinte"].append("dati-lavoro")
    # 5) la prassi curata: solo voci con id, titolo e indirizzo https
    rel_cur = "wiki-studio/lavoro/prassi/curata.json"
    if any(rel == rel_cur for _, rel in stato_git):
        cur = _leggi_json(radice / rel_cur, {}) or {}
        cattive = [k for k, v in (cur.get("voci") or {}).items()
                   if not re.match(r"^[a-z]+:[a-z-]+:\d{4}:[\w-]+$", k) or not str((v or {}).get("url") or "").startswith("https://")
                   or not (v or {}).get("titolo")]
        if cattive:
            _ripristina(radice, "M", rel_cur)
            out["issue"].append(f"- **prassi curata** ripristinata: voci non valide {', '.join(cattive[:5])}")
    # 6) richiesta evasa, indice delle schede
    rich = area_lavoro(radice) / "richiesta.json"
    if rich.exists() and triage.get("richiesta"):
        rich.write_text(json.dumps({"crea": [], "schede": [], "evasa_il": oggi}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    indice(radice)
    return out


def dopo_claude_sicuro(radice: Path, triage_path: str, esiti_path: str) -> dict:
    """dopo_claude, ma un errore imprevisto rimette com'erano memento e dati: mai pubblicare cio' che non si e'
    controllato."""
    try:
        triage = _leggi_json(Path(triage_path), {}) or {}
        esiti = _leggi_json(Path(esiti_path), {}) or {}
        return dopo_claude(radice, triage, esiti)
    except Exception as e:  # noqa: BLE001
        for rel in ("wiki-studio/lavoro/memento", "wiki-studio/lavoro/dati", "wiki-studio/lavoro/prassi/curata.json"):
            _git(radice, "checkout", "--", rel)
            _git(radice, "clean", "-fdq", "--", rel)
        return {"respinte": ["(errore del controllo)"], "sigillate": [], "ripristinati": ["memento", "dati"],
                "issue": [f"- controllo meccanico interrotto ({e.__class__.__name__}: {str(e)[:200]}): nulla pubblicato del memento"]}


# ---------------------------------------------------------------- regole per il modello

REGOLE_SCHEDE = """# Memento lavoro — istruzioni per l'aggiornamento automatico delle schede

Sei nel repository pubblico del corpus normativo. Il lavoro da fare e' nel file di triage indicato nel prompt:
`schede` (id → motivi: una norma citata e' cambiata, e' uscita prassi nuova, la scheda e' «da ricontrollare»),
`crea` (schede nuove, con titolo e area), `numeri` (valori annuali da aggiornare in
`wiki-studio/lavoro/dati/dati-lavoro.json`). Fai solo quello: non toccare altri file (verrebbero ripristinati).

## Cos'e' una scheda
Una MAPPA per istituto del diritto del lavoro, letta da chi assiste un lavoratore: quali norme leggere alla data dei
fatti, cosa cercare nel contratto collettivo, quale prassi amministrativa, quali numeri annuali, quali termini e
decadenze, quali temi di giurisprudenza cercare, quali insidie, quali documenti chiedere. Non e' una fonte e non
spiega la legge: la indica. Frasi brevi, elenchi, niente dottrina.

## Formato (obbligatorio)
Intestazione fra `---`, una riga per chiave, valori JSON:
`id` (= nome del file), `titolo`, `area` (qualificazione | tipologie | retribuzione | tempo-e-assenze | rapporto |
cessazione | previdenza | tutela), `istituti` (lista), `parole_chiave` (lista: le parole con cui l'istituto compare
nell'oggetto delle circolari), `norme` (lista «slug:articolo», es. "l-604-1966:6", "cc:2103", "dlgs-23-2015:3"),
`prassi` (lista di id dell'indice della prassi, es. "inps:circolare:2026:104"), `numeri` (lista di chiavi di
dati-lavoro.json), `stato` ("bozza": lo sigilla il controllo). Poi:

    # <titolo> — mappa
    > **Uso di questo file (Principio Zero)**: trampolino, non gabbia; mappa, non fonte. Ogni norma si legge alla
    > data dei fatti, ogni pronuncia si cerca e si verifica; i numeri dell'anno stanno in dati-lavoro.json.
    ## Norme da leggere alla data
    ## Cosa cercare nel CCNL
    ## Prassi amministrativa
    ## Numeri
    ## Termini e decadenze
    ## Temi di giurisprudenza (da cercare e leggere, senza estremi)
    ## Insidie lato lavoratore
    ## Documenti e domande al cliente

## Regole che il controllo meccanico applica (una scheda che le viola resta com'era)
1. Ogni norma citata nel testo («art. 6 L. 604/1966», «artt. 2118 e 2119 c.c.», «art. 18 L. 300/1970») deve stare in
   `norme`, e ogni voce di `norme` deve esistere nel corpus e non essere abrogata. Leggi SEMPRE il testo prima di
   citarlo: `python3 scripts/memento_verifica.py --leggi l-604-1966:6` (o `python3 scripts/codice_locale.py --art 6
   --codice l-604-1966`). Forme degli atti: «c.c.», «c.p.c.», «Cost.», «L. 604/1966», «D.Lgs. 23/2015», «D.L. 87/2018»,
   «D.P.R. 1124/1965».
2. Ogni numero con un'unita' (giorni, mesi, anni, ore, settimane, dipendenti, lavoratori, mensilita', %) deve stare
   sulla STESSA riga della norma che lo stabilisce, e comparire nel testo di quella norma (in cifre o in lettere). Se la
   norma non lo dice, non scriverlo.
3. Niente estremi di pronunce (Cassazione, Corte costituzionale, tribunali, CGUE, numeri di sentenza): nella sezione
   dei temi scrivi COSA cercare («onere della prova del repechage», «comporto e disabilita'»), non chi l'ha deciso.
4. Niente importi in euro e niente cifre decimali: i valori annuali stanno in `dati-lavoro.json`; nella scheda va la
   chiave (sezione «Numeri»).
5. La prassi citata nel testo («circolare INPS n. 104/2026», «nota INL n. 6261/2025», «interpello n. 3/2026») deve
   stare in `prassi` ed essere nell'indice `wiki-studio/lavoro/prassi/indice.json` (cerca con
   `python3 scripts/prassi_indice.py --cerca "parole" --ente inps`) e va letta alla fonte (WebFetch dell'url). Se un
   documento utile non e' nell'indice, aggiungilo a `wiki-studio/lavoro/prassi/curata.json` (`voci`: id →
   {ente, tipo, numero, anno, data, titolo, url https}).
6. Niente comandi, niente blocchi di codice, niente nomi di studi o di persone.

## Numeri annuali
Per ogni chiave in `numeri` del triage trova l'atto dell'anno (di solito una circolare INPS di gennaio-febbraio: cerca
nell'indice della prassi), leggilo alla fonte, e scrivi in `serie["AAAA"]`: `valore` (numero), `metodo: "estratto"`,
`fonte` {ente, atto, url, prassi_id}, `verificato_il`. Poi `python3 scripts/dati_lavoro.py --verifica --chiave K
--anno AAAA` deve dare OK (il valore deve comparire nel testo della fonte). Le voci derivate (es. ticket di
licenziamento) le calcola lo script: non scriverle.

## Prima di finire
- `python3 scripts/memento_verifica.py --valida <file>` su ogni scheda toccata: zero errori.
- Scrivi il file degli esiti indicato nel prompt: JSON {id: {"esito": "aggiornata" | "invariata" | "creata" |
  "non_riuscita", "nota": "una riga"}}. «invariata» = hai riletto norme e prassi e la scheda resta giusta cosi'.
- Se non riesci a rendere una scheda conforme, lasciala com'era e scrivi «non_riuscita» con il motivo.
"""


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Controllo meccanico delle schede del memento lavoro.")
    ap.add_argument("--valida", nargs="+", metavar="FILE")
    ap.add_argument("--sigilla", nargs="+", metavar="FILE")
    ap.add_argument("--indice", action="store_true")
    ap.add_argument("--leggi", metavar="SLUG:ART")
    ap.add_argument("--dopo-claude", action="store_true")
    ap.add_argument("--triage", default="")
    ap.add_argument("--esiti", default="")
    ap.add_argument("--github-output", default="")
    ap.add_argument("--issue", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--radice", default=str(ROOT))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    radice = Path(a.radice)
    if a.leggi:
        n = norma(a.leggi)
        print(json.dumps(n, ensure_ascii=False, indent=1) if a.json or n["esito"] != "OK" else
              f"{a.leggi} — {n.get('rubrica') or ''}{' (ABROGATO)' if n['abrogato'] else ''}\n{n['testo']}")
        return 0 if n["esito"] == "OK" else 1
    if a.valida or a.sigilla:
        ko = 0
        cache = {}
        for f in a.valida or a.sigilla:
            r = sigilla(Path(f), radice, cache_norme=cache) if a.sigilla else {**valida(Path(f), radice, cache), "esito": None}
            errori = r["errori"]
            ko += bool(errori)
            print(f"{'ERRORI' if errori else ('SIGILLATA' if a.sigilla else 'OK')} {f}")
            for e in errori:
                print(f"  ✗ {e}")
            for e in r.get("avvisi") or []:
                print(f"  ⚠ {e}")
        return 1 if ko else 0
    if a.indice:
        r = indice(radice)
        print(f"indice del memento: {r['_meta']['schede']} schede")
        return 0
    if a.dopo_claude:
        r = dopo_claude_sicuro(radice, a.triage, a.esiti)
        testo = ("### Memento\n\n" + f"- sigillate: {', '.join(r['sigillate']) or 'nessuna'}\n"
                 + f"- respinte: {', '.join(r['respinte']) or 'nessuna'}\n"
                 + (f"- file ripristinati (fuori dall'area ammessa): {', '.join(r['ripristinati'])}\n" if r["ripristinati"] else "")
                 + "".join(f"- numeri: {x}\n" for x in r.get("numeri") or []))
        print(testo)
        if a.report:
            with open(a.report, "a", encoding="utf-8") as f:
                f.write(testo + "\n")
        if a.issue and r["issue"]:
            Path(a.issue).write_text("Il controllo meccanico del memento ha trovato:\n\n" + "\n".join(r["issue"]) + "\n",
                                     encoding="utf-8")
        if a.github_output:
            with open(a.github_output, "a", encoding="utf-8") as f:
                f.write(f"respinte={len(r['respinte'])}\n")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
