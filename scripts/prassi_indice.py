#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""INDICE DELLA PRASSI DEL LAVORO (v0.36): circolari e messaggi INPS, circolari e note dell'Ispettorato nazionale del
lavoro, interpelli del Ministero del lavoro, circolari INAIL — numero, data, oggetto, indirizzo.

PERCHE'
-------
Normattiva non pubblica la prassi amministrativa, e chi assiste un lavoratore la cita di continuo (minimali,
NASpI, dimissioni telematiche, diffida accertativa, appalti). Questo indice non riproduce i documenti: dice che
cosa c'e' e dove, cosi' le schede del memento e gli agenti la trovano subito e la leggono alla fonte. E'
cumulativo (una voce non si cancella mai) e ogni fonte e' indipendente: se un sito non risponde, le sue voci
restano e l'errore si annota.

Fonti (verificate il 02/10/2026 dal Mac e da un runner GitHub):
  INPS     ricerca JSON del sito (`/content/scorporati/search/jcr:content.search.<selettori>.json`, selettori
           esadecimali, 100 risultati per pagina, piu' recenti prima)
  INL      pagine HTML per anno e tipo (`?pag=N&item_anno=AAAA&pt=pt_circolari|pt_note`)
  MINLAV   pagina degli interpelli (`?page=N`, Drupal) e pagina «Normativa» per circolari e lettere circolari
           (`?tip=Circolare&page=N`)
  INAIL    elenco delle circolari (`?page=N`)

Uso:
  python3 scripts/prassi_indice.py --aggiorna [--radice DIR] [--report FILE]        # settimanale: le novita'
  python3 scripts/prassi_indice.py --aggiorna --dal 2012-01-01                       # una tantum: il pregresso
  python3 scripts/prassi_indice.py --cerca "dimissioni telematiche" [--ente inps]
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import hashlib
import html as _html
import json
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

UA = "Mozilla/5.0 (corpus-normativo prassi_indice)"
TIMEOUT = 60
DAL_DEFAULT = "2012-01-01"
INPS = "https://www.inps.it"
INPS_PARENT = "/content/dam/inps-site/it/scorporati/circolari-e-messaggi"
INPS_DETTAGLIO = INPS + "/it/it/inps-comunica/atti/circolari-messaggi-e-normativa/dettaglio.{sel}.html"
INL = "https://www.ispettorato.gov.it/documenti-e-normativa/orientamenti-giuridici-inl/"
INL_SEZIONI = (("circolari", "pt_circolari", "circolare"), ("note-e-pareri", "pt_note", "nota"))
MINLAV = "https://www.lavoro.gov.it/documenti-e-norme/interpelli/Pagine/default"
INAIL = ("https://www.inail.it/portale/it/atti-e-documenti/note-provvedimenti-e-istruzioni-operative/"
         "normativa-circolari-inail.html")
_MESI = {m: i for i, m in enumerate(("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
                                     "settembre", "ottobre", "novembre", "dicembre"), 1)}
_MESI_BREVI = {m[:3]: i for m, i in _MESI.items()} | {"ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12}


# ---------------------------------------------------------------- rete

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import preferisci_ipv4  # noqa: E402

preferisci_ipv4()

def _get(url: str, timeout: float = TIMEOUT, tentativi=(3, 10)) -> str:
    for i in range(len(tentativi) + 1):
        try:
            with urlopen(Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"}), timeout=timeout) as r:
                b = r.read()
                if (r.headers.get("Content-Encoding") or "").lower() == "gzip" or b[:2] == b"\x1f\x8b":
                    b = gzip.decompress(b)
                return b.decode("utf-8", "replace")
        except HTTPError as e:
            if e.code < 500 or i == len(tentativi):
                raise
        except (URLError, OSError):
            if i == len(tentativi):
                raise
        time.sleep(tentativi[i])
    raise RuntimeError("irraggiungibile")  # pragma: no cover


def _testo(h: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()


def _data_it(s: str):
    """«26 febbraio 2026», «11 set 2026», «02-10-2026», «02/10/2026» → AAAA-MM-GG (o None)."""
    s = str(s or "").strip().lower()
    m = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(\d{1,2})(?:°|º)?\s+([a-z]+)\.?\s+(\d{4})\b", re.sub(r"['’]", " ", s.replace("1°", "1")))
    if m:
        mese = _MESI.get(m.group(2)) or _MESI_BREVI.get(m.group(2)[:3])
        if mese:
            return f"{m.group(3)}-{mese:02d}-{int(m.group(1)):02d}"
    return None


def _id(*parti) -> str:
    return ":".join(str(p).lower() for p in parti)


# ---------------------------------------------------------------- INPS

def _hx(s) -> str:
    return "".join("%x" % ord(c) for c in str(s).replace("’", " ").replace("'", " "))


def inps_pagina(pagina: int, limite: int = 100, get=None) -> list:
    sel = ".".join(_hx(x) for x in (INPS_PARENT, pagina, limite, "giorno", "DESC", "circolari-e-messaggi"))
    d = json.loads((get or _get)(f"{INPS}/content/scorporati/search/jcr:content.search.{sel}.json"))
    return ((d.get("data") or {}).get("results")) or []


def voce_inps(r: dict, oggi: str) -> tuple:
    tipo = str(r.get("tipo") or "").strip().lower() or "atto"
    num = str(r.get("numero") or "").strip()
    sel = str(r.get("selectors") or "")
    m = re.search(r"del-(\d{2}-\d{2}-\d{4})", sel)
    data = _data_it(m.group(1)) if m else _data_it(r.get("dataPubblicazione"))
    anno = (data or "")[:4] or (sel.split(".")[1] if sel.count(".") >= 2 else "")
    v = {"ente": "INPS", "tipo": tipo, "numero": num, "anno": anno, "data": data, "titolo": _testo(r.get("oggetto"))[:400],
         "url": INPS_DETTAGLIO.format(sel=sel) if sel else INPS, "pubblicato": _data_it(r.get("dataPubblicazione")),
         "visto_il": oggi}
    if r.get("path"):
        # la pagina del sito carica il testo dopo: il testo integrale (testoCompleto) e gli allegati stanno qui
        v["url_testo"] = INPS + str(r["path"]) + "/jcr:content/data/master.json"
    return _id("inps", tipo, anno, num), v


def inps(indice: dict, dal: str, oggi: str, get=None, max_pagine: int = 400, completo: bool = False) -> int:
    """Dalla piu' recente all'indietro, fino a `dal` o a una pagina tutta gia' nota."""
    nuove = 0
    for p in range(max_pagine):
        righe = inps_pagina(p, get=get)
        if not righe:
            break
        note, vecchie = 0, 0
        for r in righe:
            k, v = voce_inps(r, oggi)
            if (v.get("data") or "9999") < dal:
                vecchie += 1
                continue
            if k in indice:
                note += 1
                if v.get("url_testo") and not indice[k].get("url_testo"):
                    indice[k]["url_testo"] = v["url_testo"]
                continue
            indice[k] = v
            nuove += 1
        if vecchie == len(righe) or (not completo and note + vecchie == len(righe)):
            break
    return nuove


# ---------------------------------------------------------------- INL

_RX_CARD_INL = re.compile(r'<span class="date[^"]*">\s*([^<]+?)\s*</span>.*?<h3 class="inl-card-title[^"]*">\s*<a href="([^"]+)"'
                          r'[^>]*>(.*?)</a>\s*</h3>(?:\s*<p class="inl-card-text[^"]*">(.*?)</p>)?', re.S)


def inl_pagina(sezione: str, pt: str, anno: int, pagina: int, get=None) -> list:
    url = f"{INL}{sezione}/?pag={pagina}&item_anno={anno}&pt={pt}&src="
    h = (get or _get)(url)
    i = h.find('id="Results-2"')
    return _RX_CARD_INL.findall(h[i:] if i >= 0 else h)


def voce_inl(card: tuple, tipo: str, oggi: str) -> tuple:
    data_pub, url, titolo, descr = card
    titolo, descr = _testo(titolo), _testo(descr)
    # «Circolare INL n. 1 del …», «Nota prot. 579 del …», «Nota 7964 dell'11 …»: il numero prima di «del»
    m = (re.search(r"(?i)(?:\bn\.|\bprot\.|\bnota|\bcircolare)[^\d]{0,14}?(\d{1,6})\s+del", titolo)
         or re.search(r"(?i)\bn\.?\s*(?:prot\.?\s*n\.?\s*)?(\d+)", titolo))
    data = _data_it(titolo) or _data_it(data_pub)
    num = m.group(1) if m else hashlib.sha256(url.encode()).hexdigest()[:8]
    anno = (data or "")[:4]
    v = {"ente": "INL", "tipo": tipo, "numero": num, "anno": anno, "data": data,
         "titolo": (titolo + (f" — {descr}" if descr else ""))[:400], "url": url, "pubblicato": _data_it(data_pub), "visto_il": oggi}
    return _id("inl", tipo, anno, num), v


def inl(indice: dict, dal: str, oggi: str, get=None, completo: bool = False) -> int:
    nuove = 0
    anno_oggi = int(oggi[:4])
    for sezione, pt, tipo in INL_SEZIONI:
        for anno in range(anno_oggi, max(2017, int(dal[:4])) - 1, -1):
            for p in range(1, 60):
                cards = inl_pagina(sezione, pt, anno, p, get)
                if not cards:
                    break
                tutte_note = True
                for c in cards:
                    k, v = voce_inl(c, tipo, oggi)
                    if k in indice and indice[k].get("url") != v["url"]:
                        k = f"{k}-{hashlib.sha256(v['url'].encode()).hexdigest()[:6]}"   # allegato, stesso numero
                    if k not in indice:
                        indice[k] = v
                        nuove += 1
                        tutte_note = False
                if tutte_note and anno < anno_oggi and not completo:
                    break
    return nuove


# ---------------------------------------------------------------- Ministero del lavoro (interpelli)

_RX_RIGA_MINLAV = re.compile(r'<div class="views-row">(.*?)(?=<div class="views-row">|</main>|$)', re.S)


def minlav_pagina(pagina: int, get=None) -> list:
    h = (get or _get)(f"{MINLAV}?page={pagina}")
    return _RX_RIGA_MINLAV.findall(h)


def voce_minlav(blocco: str, oggi: str):
    m_url = re.search(r'href="([^"]+)"', blocco)
    m_dt = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})', blocco)
    m_n = re.search(r"n\.\s*(\d+)\s*/\s*(\d{4})", blocco)
    m_ist = re.search(r"Istanza:\s*<strong>(.*?)</strong>", blocco, re.S)
    m_dest = re.search(r"Destinatario:\s*<strong>(.*?)</strong>", blocco, re.S)
    if not (m_url and m_n):
        return None, None
    istanza = _testo(m_ist.group(1)) if m_ist else ""
    serie = "interpello-sicurezza" if re.search(r"(?i)articolo 12 del d\.?\s*lgs\.?\s*n?\.?\s*81/2008|art\.\s*12.*81/2008", istanza) else "interpello"
    url = m_url.group(1)
    url = url if url.startswith("http") else "https://www.lavoro.gov.it" + url
    v = {"ente": "Ministero del lavoro", "tipo": serie, "numero": m_n.group(1), "anno": m_n.group(2),
         "data": m_dt.group(1) if m_dt else None,
         "titolo": (istanza + (f" (destinatario: {_testo(m_dest.group(1))})" if m_dest else ""))[:400], "url": url, "visto_il": oggi}
    return _id("minlav", serie, m_n.group(2), m_n.group(1)), v


def minlav(indice: dict, dal: str, oggi: str, get=None, max_pagine: int = 40, completo: bool = False) -> int:
    nuove = 0
    for p in range(max_pagine):
        blocchi = minlav_pagina(p, get)
        voci = [voce_minlav(b, oggi) for b in blocchi]
        voci = [(k, v) for k, v in voci if k]
        if not voci:
            break
        note = 0
        for k, v in voci:
            if (v.get("data") or "9999") < dal:
                continue
            if k in indice:
                note += 1
                continue
            indice[k] = v
            nuove += 1
        if (note == len(voci) and not completo) or all((v.get("data") or "9999") < dal for _, v in voci):
            break
    return nuove


# ---------------------------------------------------------------- Ministero del lavoro (circolari)

MINLAV_NORMATIVA = "https://www.lavoro.gov.it/documenti-e-norme/normative/Pagine/Normativa"
#: tipi della pagina «Normativa» che sono prassi (le leggi e i decreti stanno nel corpus normattiva)
MINLAV_TIPI = (("Circolare", "circolare"), ("Lettera circolare", "lettera-circolare"),
               ("Circolare congiunta", "circolare-congiunta"), ("Circolare Congiunta", "circolare-congiunta"))
_RX_RIGA_MINNORM = re.compile(r'<div class="views-row">(.*?)(?=<div class="views-row">|</main>|$)', re.S)


def minlav_circolari_pagina(tip: str, pagina: int, get=None) -> list:
    from urllib.parse import quote
    return _RX_RIGA_MINNORM.findall((get or _get)(f"{MINLAV_NORMATIVA}?tip={quote(tip)}&page={pagina}"))


_RX_ALTRO_ENTE = re.compile(r"(?i)circolar[ea]\s+(inps|inl)\b")


def voce_minlav_circolare(blocco: str, tipo: str, oggi: str):
    m_url = re.search(r'href="([^"]+)"', blocco)
    m_t = re.search(r"<h2>(.*?)</h2>", blocco, re.S)
    if not (m_url and m_t):
        return None, None
    titolo = _testo(m_t.group(1))
    m_n = re.search(r"(?i)\bn\.?\s*(\d{1,6})", titolo)
    data = _data_it(titolo)
    if not (m_n and data):
        return None, None
    m_d = re.search(r"<p>(.*?)</p>", blocco, re.S)
    url = m_url.group(1)
    url = url if url.startswith("http") else "https://www.lavoro.gov.it" + url
    v = {"ente": "Ministero del lavoro", "tipo": tipo, "numero": m_n.group(1), "anno": data[:4], "data": data,
         "titolo": (titolo + (f" — {_testo(m_d.group(1))}" if m_d else ""))[:400], "url": url, "visto_il": oggi}
    # l'elenco del Ministero ripubblica anche circolari di altri enti: quelle INPS stanno gia' nell'indice INPS,
    # quelle dell'INL (2016-2017, prima del sito dell'Ispettorato) prendono l'id dell'INL
    altro = _RX_ALTRO_ENTE.match(titolo)
    if altro and altro.group(1).lower() == "inps":
        return None, None
    if altro:
        return _id("inl", tipo, data[:4], m_n.group(1)), {**v, "ente": "INL"}
    return _id("minlav", tipo, data[:4], m_n.group(1)), v


def minlav_circolari(indice: dict, dal: str, oggi: str, get=None, max_pagine: int = 80, completo: bool = False) -> int:
    nuove = 0
    for tip, tipo in MINLAV_TIPI:
        for p in range(max_pagine):
            voci = [voce_minlav_circolare(b, tipo, oggi) for b in minlav_circolari_pagina(tip, p, get)]
            voci = [(k, v) for k, v in voci if k]
            if not voci:
                break
            note = 0
            for k, v in voci:
                if (v.get("data") or "9999") < dal:
                    continue
                if k in indice:
                    note += 1
                    continue
                indice[k] = v
                nuove += 1
            if (note == len(voci) and not completo) or all((v.get("data") or "9999") < dal for _, v in voci):
                break
    return nuove


# ---------------------------------------------------------------- INAIL

_RX_CARD_INAIL = re.compile(r'<h2 class="card-title[^"]*">\s*<a href="([^"]+)"[^>]*>(.*?)</a>\s*</h2>\s*'
                            r'(?:<p class="card-text">(.*?)</p>)?', re.S)


def inail_pagina(pagina: int, get=None) -> list:
    return _RX_CARD_INAIL.findall((get or _get)(f"{INAIL}?page={pagina}"))


def voce_inail(card: tuple, oggi: str):
    url, titolo, descr = card
    titolo, descr = _testo(titolo), _testo(descr)
    m = re.search(r"(?i)\bn\.?\s*(\d+)", titolo)
    data = _data_it(titolo)
    if not m:
        return None, None
    anno = (data or "")[:4]
    v = {"ente": "INAIL", "tipo": "circolare", "numero": m.group(1), "anno": anno, "data": data,
         "titolo": (titolo + (f" — {descr}" if descr else ""))[:400], "url": url, "visto_il": oggi}
    return _id("inail", "circolare", anno, m.group(1)), v


def inail(indice: dict, dal: str, oggi: str, get=None, max_pagine: int = 250, completo: bool = False) -> int:
    nuove = 0
    for p in range(1, max_pagine + 1):
        voci = [voce_inail(c, oggi) for c in inail_pagina(p, get)]
        voci = [(k, v) for k, v in voci if k]
        if not voci:
            break
        note = 0
        for k, v in voci:
            if (v.get("data") or "9999") < dal:
                continue
            if k in indice:
                note += 1
                continue
            indice[k] = v
            nuove += 1
        if (note == len(voci) and not completo) or all((v.get("data") or "9999") < dal for _, v in voci):
            break
    return nuove


FONTI = (("inps", inps), ("inl", inl), ("minlav", minlav), ("minlav_circolari", minlav_circolari), ("inail", inail))


# ---------------------------------------------------------------- indice

def percorso(radice: Path) -> Path:
    return Path(radice) / "wiki-studio" / "lavoro" / "prassi" / "indice.json"


def carica(radice: Path) -> dict:
    try:
        d = json.loads(percorso(radice).read_text(encoding="utf-8"))
        if isinstance(d.get("voci"), dict):
            return d
    except (OSError, ValueError):
        pass
    return {"_meta": {}, "voci": {}}


def con_curata(indice: dict, curata: dict) -> dict:
    """L'indice con le voci aggiunte a mano o dal modello (`curata.json`): la ricerca le trova come le altre."""
    voci = dict((curata or {}).get("voci") or {})
    voci.update((indice or {}).get("voci") or {})
    return {"_meta": (indice or {}).get("_meta") or {}, "voci": voci}


def carica_tutto(radice: Path) -> dict:
    try:
        curata = json.loads((percorso(radice).parent / "curata.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        curata = {}
    return con_curata(carica(radice), curata if isinstance(curata, dict) else {})


def aggiorna(radice: Path, dal: str = "", quali=None, get=None, oggi: str = "") -> dict:
    """Le novita' di ogni fonte (dal `dal` se dato: il pregresso). Una fonte che fallisce non tocca le sue voci."""
    oggi = oggi or _dt.date.today().isoformat()
    d = carica(radice)
    voci = d["voci"]
    meta = d.get("_meta") or {}
    stato_fonti = dict(meta.get("fonti") or {})
    esiti = {}
    for nome, f in FONTI:
        if quali and nome not in quali:
            continue
        inizio = dal or DAL_DEFAULT
        try:
            n = f(voci, inizio, oggi, get, completo=bool(dal))
            stato_fonti[nome] = {"esito": "ok", "quando": oggi, "nuove": n,
                                 "dal": min(inizio, (stato_fonti.get(nome) or {}).get("dal") or inizio)}
            esiti[nome] = n
        except Exception as e:
            stato_fonti[nome] = {**(stato_fonti.get(nome) or {}), "esito": "errore", "quando": oggi,
                                 "dettaglio": f"{e.__class__.__name__}: {str(e)[:160]}"}
            esiti[nome] = f"errore ({e.__class__.__name__})"
    d["_meta"] = {"descrizione": "indice della prassi del lavoro: numero, data, oggetto e indirizzo (nessun testo)",
                  "aggiornato_il": oggi, "voci": len(voci), "fonti": stato_fonti, "schema": 1}
    d["voci"] = dict(sorted(voci.items(), key=lambda kv: (kv[1].get("data") or "", kv[0]), reverse=True))
    p = percorso(radice)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    tmp.replace(p)
    return {"voci": len(voci), "nuove": esiti}


def nuove_dal(indice: dict, data: str) -> list:
    """Le voci viste per la prima volta dal giorno `data` in poi (per il triage del memento)."""
    return [(k, v) for k, v in (indice.get("voci") or {}).items() if str(v.get("visto_il") or "") >= data]


def _norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s or ""))
    return " ".join(re.sub(r"[^a-z0-9/ ]", " ", "".join(c for c in s if not unicodedata.combining(c)).lower()).split())


def cerca(indice: dict, testo: str, ente: str = "", n: int = 15) -> list:
    """Le voci il cui oggetto contiene le parole del testo (tutte, o quasi), le piu' recenti prima."""
    parole = [p for p in _norm(testo).split() if len(p) > 2]
    if not parole:
        return []
    out = []
    for k, v in (indice.get("voci") or {}).items():
        if ente and v.get("ente", "").lower() != ente.lower() and not k.startswith(ente.lower()):
            continue
        t = _norm(v.get("titolo"))
        presi = sum(1 for p in parole if p in t)
        if presi >= max(1, len(parole) - (1 if len(parole) > 2 else 0)):
            out.append((presi, v.get("data") or "", k, v))
    out.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [{"id": k, **v} for _, _, k, v in out[:n]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Indice della prassi del lavoro (INPS, INL, Ministero, INAIL).")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--dal", default="", help="AAAA-MM-GG: riprende il pregresso da questa data")
    ap.add_argument("--fonte", action="append", choices=[n for n, _ in FONTI])
    ap.add_argument("--radice", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--report", default="")
    ap.add_argument("--cerca", default="")
    ap.add_argument("--ente", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.aggiorna:
        r = aggiorna(Path(a.radice), a.dal, a.fonte)
        testo = "### Prassi del lavoro\n\n" + f"- voci nell'indice: {r['voci']}\n" + "".join(
            f"- {k}: {v}\n" for k, v in r["nuove"].items())
        print(testo)
        if a.report:
            with open(a.report, "a", encoding="utf-8") as f:
                f.write(testo + "\n")
        return 0
    if a.cerca:
        r = cerca(carica_tutto(Path(a.radice)), a.cerca, a.ente)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            for v in r:
                print(f"{v['id']}  {v.get('data') or '?'}  {v['titolo'][:140]}\n    {v['url']}")
        return 0 if r else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
