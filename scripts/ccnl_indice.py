#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARCHIVIO CNEL DEI CONTRATTI COLLETTIVI (v0.36): il client dell'API pubblica e l'indice compatto del corpus.

PERCHE'
-------
I CCNL non si scaricano in blocco: il 72% dei PDF recenti dell'archivio e' una scansione e 332 contratti sono un
testo di base piu' una pila di rinnovi. Il plugin impara invece DOVE sta il contratto giusto e lo scarica quando
serve (`ccnl.py`). Questo modulo e' la parte comune: parla con l'API dell'archivio (la stessa che usa il sito del
CNEL, pubblica e senza autenticazione) e costruisce, una volta a settimana nel corpus pubblico, un indice di soli
metadati — codici, titoli, firmatari, accordi con le loro date, dipendenti INPS — che il plugin consulta anche
quando l'API non risponde. Nessun testo di contratto entra nell'indice.

L'API (verificata il 02/10/2026; base `API`):
  POST /ricerca/pubblica/ccnl                                   elenco dei contratti (pageSize fino a 1000)
  GET  /ricerca/pubblica/accordi/cerca/accordi/codice-ccnl/{c}  accordi di un contratto (vigenti=true|false)
  GET  /ricerca/pubblica/accordi/scarica/accordi/{idAccordo}    il documento, in base64 dentro un JSON
  GET  /ricerca/pubblica/open-data?type=ARCHIVIO_CORRENTE|ARCHIVIO_STORICO   tutti gli accordi (IODL 2.0)
Le risposte paginate stanno in `pagedList.content`. Il sito www.cnel.it e' dietro Cloudflare, che respinge lo
user agent predefinito di Python: si usa sempre `UA`.

FILE PRODOTTI (in `<radice>/wiki-studio/lavoro/ccnl/`)
  indice.json   {"_meta", "ccnl": {codice: {t, s, tipo, dir, sez, ateco, fd, fs, conf, dst, scad, dip, id}}}
  accordi.json  {"_meta", "accordi": {codice: [{id, tip, tit, st, dec, sc, se, pub, ult, ar}]}}
  novita.json   {"_meta", "eventi": [{visto_il, codice, id, tip, evento}]}   (ultime 26 settimane)

Uso:
  python3 scripts/ccnl_indice.py --aggiorna [--radice DIR] [--dipendenti FILE.xlsx|URL] [--report FILE]
  python3 scripts/ccnl_indice.py --sonda
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import gzip
import json
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import preferisci_ipv4  # noqa: E402

preferisci_ipv4()

API = "https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api"
UA = "Mozilla/5.0 (corpus-normativo ccnl_indice)"
SITO = "https://www.cnel.it/archivio-contratti/entra-nell-archivio/contratti-collettivi-del-settore-privato/"
SITO_CESSATI = "https://www.cnel.it/archivio-contratti/entra-nell-archivio/ccnl-e-aec-cessati-e-confluiti"
SITO_RICERCA = "https://www.cnel.it/archivio-contratti/entra-nell-archivio/interroga-l-archivio"
URL_DIPENDENTI = ("https://www.cnel.it/media/docs/default-source/archivio-contratti---cartelle-excel/"
                  "dati-sull%27applicazione-dei-ccnl-dal-2018.xlsx")
#: le cinque sezioni del contratti del settore privato nell'archivio (valore dell'API → (sigla, pagina del sito))
SEZIONI = {
    "CCNL_SETTORE_VIGENTI_O_ULTRATTATTIVI": ("settore", "contratti-nazionali-di-settore-vigenti-o-ultrattivi"),
    "CCNL_DIRIGENTI_SETTORE_PRIVATO": ("dirigenti", "contratti-nazionali-per-i-dirigenti"),
    "CONTRATTI_AZIENDALI_LIVELLO_NAZIONALE": ("aziendali", "contratti-aziendali-di-livello-nazionale"),
    "CCNL_DI_NUOVO_DEPOSITO": ("nuovo", "contratti-di-nuovo-deposito"),
    "ALTRI_CCNL": ("altri", "altri-contratti"),
}
PAGINA_SEZIONE = {sigla: pagina for sigla, pagina in SEZIONI.values()}
#: tipologie degli accordi → sigla breve dell'indice
TIPOLOGIE = {"Testo definitivo": "TD", "Accordo di rinnovo": "AR", "Verbale Integrativo": "VI",
             "Accordo economico": "AE", "Economico secondo biennio": "E2"}
NOMI_TIPOLOGIE = {v: k for k, v in TIPOLOGIE.items()}
RX_CODICE = re.compile(r"^[A-Z][A-Z0-9]{3}$")
RX_CONFEDERALI = re.compile(r"\b(CGIL|CISL|UIL)\b")
SETTIMANE_NOVITA = 26
TIMEOUT = 60


# ---------------------------------------------------------------- trasporto

def _richiesta(url: str, corpo=None, timeout: float = TIMEOUT, tentativi=(2, 6)) -> bytes:
    """GET (o POST JSON se `corpo`) con gzip e due tentativi in piu'; solleva l'ultima eccezione."""
    dati = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    h = {"User-Agent": UA, "Accept": "application/json, */*;q=0.5", "Accept-Encoding": "gzip"}
    if dati is not None:
        h["Content-Type"] = "application/json"
    for i in range(len(tentativi) + 1):
        try:
            with urlopen(Request(url, data=dati, headers=h), timeout=timeout) as r:
                b = r.read()
                if (r.headers.get("Content-Encoding") or "").lower() == "gzip" or b[:2] == b"\x1f\x8b":
                    b = gzip.decompress(b)
                return b
        except HTTPError as e:
            if e.code < 500 or i == len(tentativi):
                raise
        except (URLError, OSError):
            if i == len(tentativi):
                raise
        time.sleep(tentativi[i])
    raise RuntimeError("irraggiungibile")  # pragma: no cover


def _json(url: str, corpo=None, get=None, timeout: float = TIMEOUT):
    b = (get or _richiesta)(url, corpo, timeout)
    return json.loads(b.decode("utf-8") if isinstance(b, bytes) else b)


def ccnl_pagina(filtri: dict = None, pagina: int = 0, get=None) -> dict:
    corpo = {"pageNumber": pagina, "pageSize": 1000, **(filtri or {})}
    return (_json(API + "/ricerca/pubblica/ccnl", corpo, get) or {}).get("pagedList") or {}


def ccnl_tutti(filtri: dict = None, get=None) -> list:
    """Tutti i contratti che rispondono ai filtri (l'API pagina a 1000)."""
    out, p = [], 0
    while True:
        pl = ccnl_pagina(filtri, p, get)
        out.extend(pl.get("content") or [])
        p += 1
        if p >= int(pl.get("totalPages") or 0) or not pl.get("content"):
            return out


def accordi_open_data(tipo: str = "ARCHIVIO_CORRENTE", get=None) -> list:
    return (_json(API + f"/ricerca/pubblica/open-data?type={tipo}", None, get, timeout=180) or {}).get("data") or []


def accordi_codice(codice: str, vigenti: bool = True, get=None) -> list:
    """Gli accordi di un contratto, dall'API (sempre aggiornati: l'indice e' settimanale)."""
    out, p = [], 0
    while True:
        url = (API + f"/ricerca/pubblica/accordi/cerca/accordi/codice-ccnl/{codice}"
               f"?vigenti={'true' if vigenti else 'false'}&pageSize=50&pageIndex={p}")
        pl = (_json(url, None, get) or {}).get("pagedList") or {}
        out.extend(pl.get("content") or [])
        p += 1
        if p >= int(pl.get("totalPages") or 0) or not pl.get("content"):
            return out


def url_documento(id_accordo) -> str:
    return API + f"/ricerca/pubblica/accordi/scarica/accordi/{int(id_accordo)}"


def scarica_accordo(id_accordo, get=None, timeout: float = 300) -> tuple:
    """(nome del file, byte, mimetype) del documento di un accordo. Il JSON porta il file in base64
    (`model.fileContent`); l'indirizzo del blob che contiene risponde 403, quindi non si usa."""
    d = _json(url_documento(id_accordo), None, get, timeout=timeout) or {}
    m = d.get("model") or {}
    contenuto = m.get("fileContent")
    if not contenuto:
        raise ValueError(f"accordo {id_accordo}: risposta senza documento")
    return str(m.get("simpleFileName") or f"{id_accordo}"), base64.b64decode(contenuto), m.get("mimetype")


def tipo_file(dati: bytes) -> str:
    """'pdf' | 'rtf' | 'testo-cp1252' (gli .rtf del 2008-2009 sono testo con 5 byte 0xFB in testa) | 'doc' |
    'docx' | 'sconosciuto'."""
    if dati[:5] == b"%PDF-":
        return "pdf"
    if dati[:5] == b"{\\rtf":
        return "rtf"
    if dati[:5] == b"\xfb" * 5:
        return "testo-cp1252"
    if dati[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "doc"
    if dati[:4] == b"PK\x03\x04":
        return "docx"
    return "sconosciuto"


def url_browser(codice: str, sezione: str = "", cessato: bool = False) -> str:
    """La pagina del sito del CNEL che apre la scheda del contratto (il collegamento vive solo nel frammento
    «#ccnl/<codice>», gestito dal sito nel browser)."""
    if cessato:
        return f"{SITO_CESSATI}#ccnl/{codice}"
    pagina = PAGINA_SEZIONE.get(sezione)
    return f"{SITO}{pagina}#ccnl/{codice}" if pagina else f"{SITO_RICERCA}#ccnl/{codice}"


# ---------------------------------------------------------------- dipendenti INPS (Excel del CNEL)

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _righe_xlsx(dati: bytes, nome_foglio_rx: str) -> list:
    """Le righe (liste di stringhe, colonne per lettera) del primo foglio il cui nome corrisponde."""
    z = zipfile.ZipFile(BytesIO(dati))
    condivise = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            condivise.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels}
    foglio = None
    for s in wb.find("m:sheets", _NS):
        if re.search(nome_foglio_rx, s.get("name") or "", re.I):
            t = target.get(s.get(_NS_R)) or ""
            foglio = "xl/" + t.lstrip("/").replace("xl/", "", 1) if not t.startswith("xl/") else t
            break
    if not foglio:
        return []
    out = []
    for row in ET.fromstring(z.read(foglio)).iter(f"{{{_NS['m']}}}row"):
        celle = {}
        for c in row.findall("m:c", _NS):
            col = re.match(r"[A-Z]+", c.get("r") or "A").group(0)
            v = c.find("m:v", _NS)
            if c.get("t") == "s" and v is not None:
                celle[col] = condivise[int(v.text)]
            elif c.get("t") == "inlineStr":
                celle[col] = "".join(x.text or "" for x in c.iter(f"{{{_NS['m']}}}t"))
            else:
                celle[col] = v.text if v is not None else ""
        out.append(celle)
    return out


def dipendenti_da_xlsx(dati: bytes) -> tuple:
    """({codice: dipendenti}, anno) dall'ultimo anno pieno del foglio «dati quantitativi» dell'Excel del CNEL."""
    righe = _righe_xlsx(dati, r"dati quantitativi")
    testa = next((r for r in righe if any(re.match(r"(?i)ccnl id", str(v or "")) for v in r.values())), None)
    if not testa:
        return {}, None
    col_codice = next(k for k, v in testa.items() if re.match(r"(?i)ccnl id", str(v or "")))
    anni = {}
    for k, v in testa.items():
        m = re.search(r"(?i)dipendenti\s+(\d{4})", str(v or ""))
        if m:
            anni[int(m.group(1))] = k
    if not anni:
        return {}, None
    for anno in sorted(anni, reverse=True):
        col = anni[anno]
        valori = {}
        for r in righe:
            cod = str(r.get(col_codice) or "").strip().upper()
            if RX_CODICE.match(cod):
                try:
                    valori[cod] = int(float(r.get(col) or 0))
                except ValueError:
                    continue
        if sum(valori.values()) > 0:
            return valori, anno
    return {}, None


# ---------------------------------------------------------------- indice

def _d(v) -> str:
    return str(v or "")[:10]


def voce_ccnl(r: dict, sezione: str = "", dip: dict = None) -> dict:
    fs = [str(x) for x in r.get("firmatariSindacali") or []]
    v = {"t": str(r.get("titolo") or "").strip(), "s": "V" if str(r.get("stato") or "").upper() == "VIGENTE" else "C",
         "tipo": str(r.get("tipo") or ""), "dir": bool(r.get("dirigenti")), "sez": sezione,
         "ateco": sorted({str(x) for x in r.get("settoriAteco") or []}),
         "fd": [str(x) for x in r.get("firmatariDatoriali") or []], "fs": fs,
         "conf": bool(any(RX_CONFEDERALI.search(x.upper()) for x in fs)),
         "dst": [str(x) for x in r.get("ccnlDst") or []], "scad": _d(r.get("dataScadenzaUltimoAccordo")) or None,
         "id": r.get("idCcnl")}
    cod = str(r.get("codice") or "")
    if dip is not None and cod in dip:
        v["dip"] = dip[cod]
    if r.get("settorePubblico"):
        v["pub"] = True
    return {k: x for k, x in v.items() if x not in (None, "", [])} | {"s": v["s"], "conf": v["conf"], "dir": v["dir"]}


def voce_accordo(r: dict, archivio: str) -> dict:
    v = {"id": r.get("idAccordo"), "tip": TIPOLOGIE.get(str(r.get("tipologiaAccordo") or ""), str(r.get("tipologiaAccordo") or "")),
         "tit": str(r.get("titolo") or "").strip()[:160], "st": _d(r.get("dataStipula")), "dec": _d(r.get("dataDecorrenza")),
         "sc": _d(r.get("dataScadenzaContrattuale")), "se": _d(r.get("dataScadenzaEconomica")),
         "pub": _d(r.get("dataPubblicazione")), "ult": bool(r.get("ultimoAccordoVigente")), "ar": archivio}
    if r.get("visibileOnline") is False:
        v["vis"] = False
    return {k: x for k, x in v.items() if x not in ("", None)}


def costruisci(ccnl: list, sezioni: dict, corrente: list, storico: list, dipendenti: dict = None,
               anno_dipendenti=None, oggi: _dt.date = None) -> tuple:
    """(indice, accordi) dai dati grezzi dell'API. `sezioni` = {codice: sigla della sezione}."""
    oggi = oggi or _dt.date.today()
    voci = {}
    for r in ccnl:
        cod = str(r.get("codice") or "").strip().upper()
        if RX_CODICE.match(cod):
            voci[cod] = voce_ccnl(r, sezioni.get(cod, ""), dipendenti)
    acc = {}
    visti = set()
    for archivio, righe in (("C", corrente), ("S", storico)):
        for r in righe:
            cod = str(r.get("codiceCcnl") or "").strip().upper()
            if not RX_CODICE.match(cod) or not r.get("idAccordo"):
                continue
            chiave_ = (cod, r["idAccordo"])
            if chiave_ in visti:            # lo stesso accordo nei due archivi: vale il corrente
                continue
            visti.add(chiave_)
            acc.setdefault(cod, []).append(voce_accordo(r, archivio))
    for cod in acc:
        acc[cod].sort(key=lambda a: (a.get("dec") or "", a.get("st") or "", a.get("id") or 0))
    meta = {"fonte": "CNEL — Archivio nazionale dei contratti e degli accordi collettivi di lavoro (API pubblica)",
            "licenza": "IODL 2.0 (metadati); nessun testo di contratto in questo file",
            "aggiornato_il": oggi.isoformat(), "schema": 1}
    indice = {"_meta": {**meta, "n_ccnl": len(voci), "n_vigenti": sum(1 for v in voci.values() if v["s"] == "V"),
                        "dipendenti_anno": anno_dipendenti,
                        "dipendenti_fonte": "CNEL, «Dati sull'applicazione dei CCNL» (fonte INPS, UniEmens)" if anno_dipendenti else None},
              "ccnl": dict(sorted(voci.items()))}
    accordi = {"_meta": {**meta, "n_accordi": sum(len(v) for v in acc.values()),
                         "tipologie": NOMI_TIPOLOGIE, "archivi": {"C": "corrente (in vigore)", "S": "storico (superati)"}},
               "accordi": dict(sorted(acc.items()))}
    return indice, accordi


def novita(vecchio: dict, nuovo: dict, eventi_prec: list, oggi: _dt.date = None) -> list:
    """Gli accordi comparsi, passati allo storico o spariti fra due indici, piu' gli eventi delle ultime 26
    settimane. Le date dell'API non sono monotone: si confrontano gli id."""
    oggi = oggi or _dt.date.today()
    prima = {(c, a["id"]): a for c, lst in ((vecchio or {}).get("accordi") or {}).items() for a in lst}
    dopo = {(c, a["id"]): a for c, lst in ((nuovo or {}).get("accordi") or {}).items() for a in lst}
    eventi = []
    if prima:                                              # al primo giro non c'e' niente da confrontare
        for k, a in dopo.items():
            if k not in prima:
                eventi.append({"visto_il": oggi.isoformat(), "codice": k[0], "id": k[1], "tip": a.get("tip"),
                               "evento": "nuovo", "st": a.get("st"), "dec": a.get("dec")})
            elif prima[k].get("ar") == "C" and a.get("ar") == "S":
                eventi.append({"visto_il": oggi.isoformat(), "codice": k[0], "id": k[1], "tip": a.get("tip"),
                               "evento": "superato"})
        for k, a in prima.items():
            if k not in dopo:
                eventi.append({"visto_il": oggi.isoformat(), "codice": k[0], "id": k[1], "tip": a.get("tip"),
                               "evento": "rimosso"})
    soglia = (oggi - _dt.timedelta(weeks=SETTIMANE_NOVITA)).isoformat()
    return sorted([e for e in (eventi_prec or []) if str(e.get("visto_il") or "") >= soglia] + eventi,
                  key=lambda e: (e["visto_il"], e["codice"], e["id"]))


def _scrivi(p: Path, dati) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(dati, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(p)


def _leggi(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def aggiorna(radice: Path, dipendenti_da: str = "", get=None, oggi: _dt.date = None) -> dict:
    """Scarica elenco, sezioni, archivi e (se possibile) dipendenti; scrive i tre file. Un dato che non arriva
    lascia quello vecchio (i dipendenti si tengono dall'indice precedente)."""
    oggi = oggi or _dt.date.today()
    dest = Path(radice) / "wiki-studio" / "lavoro" / "ccnl"
    vecchio_i, vecchio_a, vecchie_n = _leggi(dest / "indice.json"), _leggi(dest / "accordi.json"), _leggi(dest / "novita.json")
    ccnl = ccnl_tutti(None, get)
    sezioni = {}
    for valore, (sigla, _p) in SEZIONI.items():
        for r in ccnl_tutti({"nuovaOrganizzazioneCCNL": valore}, get):
            sezioni.setdefault(str(r.get("codice") or "").upper(), sigla)
    corrente = accordi_open_data("ARCHIVIO_CORRENTE", get)
    storico = accordi_open_data("ARCHIVIO_STORICO", get)
    if len(ccnl) < 500 or len(corrente) < 1000:
        raise SystemExit(f"[ccnl_indice] risposta sospetta: {len(ccnl)} contratti, {len(corrente)} accordi correnti — "
                         "l'indice resta quello di prima")
    dip, anno, nota_dip = None, None, ""
    try:
        src = dipendenti_da or URL_DIPENDENTI
        dati = Path(src).read_bytes() if Path(src).exists() else _richiesta(src, timeout=120)
        dip, anno = dipendenti_da_xlsx(dati)
        nota_dip = f"dipendenti {anno}: {len(dip)} contratti"
    except Exception as e:  # i dipendenti sono un di piu': senza, si tengono quelli di prima
        nota_dip = f"dipendenti non aggiornati ({e.__class__.__name__})"
    if not dip and vecchio_i:
        dip = {c: v["dip"] for c, v in (vecchio_i.get("ccnl") or {}).items() if "dip" in v}
        anno = (vecchio_i.get("_meta") or {}).get("dipendenti_anno")
    indice, accordi = costruisci(ccnl, sezioni, corrente, storico, dip, anno, oggi)
    eventi = novita(vecchio_a, accordi, (vecchie_n or {}).get("eventi"), oggi)
    _scrivi(dest / "indice.json", indice)
    _scrivi(dest / "accordi.json", accordi)
    _scrivi(dest / "novita.json", {"_meta": {"descrizione": "accordi comparsi, superati o spariti nell'archivio CNEL",
                                             "aggiornato_il": oggi.isoformat(), "settimane": SETTIMANE_NOVITA},
                                   "eventi": eventi})
    nuovi = [e for e in eventi if e["visto_il"] == oggi.isoformat()]
    return {"ccnl": len(indice["ccnl"]), "vigenti": indice["_meta"]["n_vigenti"], "accordi": accordi["_meta"]["n_accordi"],
            "sezioni": len(sezioni), "dipendenti": nota_dip, "eventi_oggi": len(nuovi),
            "nuovi_oggi": [f"{e['codice']} {e['tip']} {e.get('st') or ''}".strip() for e in nuovi if e["evento"] == "nuovo"][:40]}


def sonda(get=None) -> dict:
    t = time.time()
    try:
        pl = ccnl_pagina({"codice": "H011"}, 0, get)
        return {"esito": "OK", "ms": int((time.time() - t) * 1000), "trovati": len(pl.get("content") or [])}
    except Exception as e:
        return {"esito": "ERRORE", "ms": int((time.time() - t) * 1000), "dettaglio": repr(e)[:200]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Indice dei contratti collettivi dall'archivio CNEL (solo metadati).")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--radice", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--dipendenti", default="", help="Excel del CNEL sui dati di applicazione (file o URL)")
    ap.add_argument("--report", default="")
    ap.add_argument("--sonda", action="store_true")
    a = ap.parse_args(argv)
    if a.sonda:
        r = sonda()
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r["esito"] == "OK" else 1
    if a.aggiorna:
        r = aggiorna(Path(a.radice), a.dipendenti)
        testo = (f"### Contratti collettivi (archivio CNEL)\n\n- {r['ccnl']} contratti ({r['vigenti']} vigenti), "
                 f"{r['accordi']} accordi, sezioni per {r['sezioni']} codici\n- {r['dipendenti']}\n"
                 f"- novita' di oggi: {r['eventi_oggi']}" + ("".join(f"\n  - {x}" for x in r["nuovi_oggi"])) + "\n")
        print(testo)
        if a.report:
            with open(a.report, "a", encoding="utf-8") as f:
                f.write(testo + "\n")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
