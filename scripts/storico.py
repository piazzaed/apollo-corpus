#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testo STORICO di un articolo alla data — cache permanente per versione (piano v0.25, D5.4).

IL BUCO CHE CHIUDE
------------------
Il corpus locale (`codice_locale.py`) porta UNA versione per articolo: la vigente allo snapshot.
Per una claim con data-evento anteriore alla versione vigente (tempus regit actum) il locale tace,
e fino alla Fase 3 si andava su normattiva live a ogni round: misurato sulla pratica di riferimento,
9 claim su 22 (art. 5 D.Lgs. 28/2010 al 2015, TUB al 2018, …) — sempre le stesse, sempre di nuovo.

Un testo storico NON cambia: l'art. 5 D.Lgs. 28/2010 in vigore il 30/06/2015 e' quello per sempre.
Quindi si scarica UNA volta il permalink datato di normattiva
    https://www.normattiva.it/uri-res/N2Ls?<urn>~art<N>!vig=AAAA-MM-GG
e lo si salva in `<stato_root>/fonti-cache/storico/<slug>/<art>/<data-versione>.md`, senza scadenza.

LA CHIAVE E' LA VERSIONE, NON LA DATA
-------------------------------------
L'indice locale porta (dalla Fase 4) `_meta.versioni`: le date in cui l'atto e' cambiato (lifecycle
dell'AKN: originale + ogni atto modificante). Dentro una versione il testo di un articolo e' uno:
tutte le date fra il 21/06/2013 e il 28/12/2022 dell'art. 5 D.Lgs. 28/2010 servono lo stesso file
`2013-06-21.md`. Confini a livello di ATTO, prudenti per costruzione (un articolo non toccato ha lo
stesso testo prima e dopo). Per gli atti FUORI corpus la chiave e' la data richiesta, dichiarata.

QUANDO NON RISPONDE (e lo dice)
-------------------------------
* data >= oggi: non e' storico, e' il vigente (corpus locale / live);
* data anteriore all'atto;
* data posteriore al consolidato dello snapshot: i confini di versione potrebbero non essere
  aggiornati (una modifica entrata in vigore ieri non e' nell'indice di sette giorni fa);
* pagina che non supera la validazione (articolo assente, atto diverso): niente in cache;
* `--offline` senza cache.

Uso:
  python3 scripts/storico.py --riferimento "art. 5 D.Lgs. 28/2010" --data 2015-06-30 [--json] [--offline]
  python3 scripts/storico.py --prewarm cpc --art 163 --dal 2023-01-01      # un testo per confine di versione
  python3 scripts/storico.py --stato
`fonti_fetch.py --riferimento … --data-evento …` passa di qui da solo, prima del live.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codice_locale as cl   # noqa: E402
import fonti_fetch as ff     # noqa: E402
from paths import stato_root_persistente as stato_root  # noqa: E402  (v0.30: versioni storiche = dati immutabili, cache persistente)

#: Attese di retry sul download storico: un solo retry breve. Il chiamante (Livello 0) ha un budget
#: di 30 s per tutto il mazzo; se normattiva non risponde si degrada a VAI_LIVE come sempre.
ATTESE = (1,)


def _oggi() -> _dt.date:
    return _dt.date.today()


def dir_storico() -> Path:
    return stato_root() / "fonti-cache" / "storico"


# ---------------------------------------------------------------- rete (sostituibile nei test)

def _scarica(url: str) -> str:
    """HTML del permalink datato. `STUDIO_STORICO_STUB` (test/CLI offline-simulata) = file da servire."""
    stub = os.environ.get("STUDIO_STORICO_STUB")
    if stub and Path(stub).exists():
        return Path(stub).read_text(encoding="utf-8", errors="replace")
    html, _n = ff.fetch_con_retry(url, ATTESE)
    return html


def _data_iso(s: str) -> str:
    s = str(s or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return ""


def _slug_fuori_corpus(urn_base: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", urn_base.lower().replace("urn:nir:", "")).strip("-")[:120]


def _no(motivo: str, **extra) -> dict:
    return {"verdetto": "NON_DISPONIBILE", "motivo": motivo, **extra}


# ---------------------------------------------------------------- cache

def _leggi_file(f: Path):
    """(header, testo) di un file della cache storica; None se illeggibile."""
    try:
        raw = f.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.match(r"<!-- storico (\{.*?\}) -->\n", raw, re.S)
    if not m:
        return None
    try:
        header = json.loads(m.group(1))
    except ValueError:
        return None
    corpo = raw[m.end():]
    corpo = re.sub(r"^(?:<!--.*?-->\s*)+", "", corpo, flags=re.S)   # eventuali commenti di servizio
    return header, corpo.strip()


def _scrivi_file(f: Path, header: dict, testo: str) -> None:
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("<!-- storico " + json.dumps(header, ensure_ascii=False) + " -->\n"
                 "<!-- Testo storico normattiva (scripts/storico.py): permalink URN datato, salvato una volta, senza\n"
                 "     scadenza (un testo storico non cambia). File di DATI: non si modifica a mano. -->\n\n" + testo + "\n",
                 encoding="utf-8")


# ---------------------------------------------------------------- cuore

def recupera(riferimento: str, data: str, *, offline: bool = False, slug: str = None, urn: str = None,
             oggi: _dt.date = None) -> dict:
    """Il testo dell'articolo in vigore a `data`, dalla cache storica o (una volta) da normattiva.

    Ritorna sempre un dict: verdetto OK (testo, url, versione, da_cache, file, fonte…) oppure
    NON_DISPONIBILE con `motivo`. Non stampa, non esce: e' il cuore riusato da fonti_fetch."""
    oggi = oggi or _oggi()
    data_iso = _data_iso(data)
    if not data_iso:
        return _no(f"data non riconosciuta: {data!r} (attesa AAAA-MM-GG)")
    if data_iso >= oggi.isoformat():
        return _no(f"data {data_iso} non anteriore a oggi: non e' un testo storico (vale il vigente: corpus locale o live)")
    parsed = ff.parse_riferimento(riferimento)
    if not parsed:
        return _no(f"riferimento non riconosciuto: {riferimento!r}")
    urn_base, varianti, art, descr = parsed
    if not art:
        return _no("lo storico serve singoli articoli: indica l'art.")
    art_token = cl._norm_token("art. " + str(art))
    slug = slug or cl.slug_da_riferimento(descr, urn_base)
    if urn:
        urn_base, varianti = urn, []
    elif slug and cl.urn_permalink(slug):
        # l'URN del corpus porta la data completa e l'eventuale suffisso di allegato (':1' dei codici):
        # e' il permalink piu' preciso; quello dedotto dal riferimento resta come variante. Per le preleggi
        # vale `urn_permalink` (';262:1'): l'URN del download AKN (';262:2') e' quello del c.c.
        urn_base, varianti = cl.urn_permalink(slug), []
    _, indice = (cl._indice(slug) if slug else (None, None))

    versione = None
    if indice:
        meta = indice.get("_meta") or {}
        versione = cl.versione_alla_data(slug, data_iso, indice)
        versioni = meta.get("versioni") or []
        if versioni and data_iso < versioni[0]["data"]:
            return _no(f"data {data_iso} anteriore all'atto (prima versione {versioni[0]['data']})")
        consolidato = str(meta.get("consolidato_normattiva") or "")
        if versioni and consolidato and data_iso > consolidato:
            return _no(f"data {data_iso} posteriore al consolidato dello snapshot ({consolidato}): i confini di versione "
                       "potrebbero non essere aggiornati — vale il corpus locale o il live")
    if versione:
        chiave = versione["inizio"]
        versione_txt = f"versione dal {versione['inizio']} al {versione['fine'] or 'vigente'}" + (
            f" (mod. {versione['atto_modificante']})" if versione.get("atto_modificante") else " (testo originario)")
        versione_da, versione_a = versione["inizio"], versione["fine"]
    else:
        chiave = data_iso
        versione_txt = f"data richiesta {data_iso} (atto fuori corpus o senza versioni nell'indice: confini di versione ignoti)"
        versione_da, versione_a = None, None
    cartella = dir_storico() / (slug or _slug_fuori_corpus(urn_base)) / art_token
    f = cartella / f"{chiave}.md"

    letto = _leggi_file(f) if f.exists() else None
    if letto:
        header, testo = letto
        return {"verdetto": "OK", "da_storico": True, "da_cache": True, "riferimento": riferimento,
                "descrizione": descr, "codice_locale": slug, "url": header.get("url"), "vig": data_iso,
                "versione": header.get("versione") or versione_txt, "versione_da": header.get("versione_da", versione_da),
                "versione_a": header.get("versione_a", versione_a), "atto_titolo": header.get("atto_titolo"),
                "fetched_at": header.get("scaricato_il"), "atto_validato": True, "testo": testo, "file": str(f),
                "fonte": (f"testo storico normattiva (permalink URN datato, scaricato il {str(header.get('scaricato_il', ''))[:10]}, "
                          f"cache permanente) — {header.get('versione') or versione_txt}")}
    if offline:
        return _no(f"testo storico non in cache ({f.name} per {slug or descr} art. {art_token}) e modalita' offline")

    ultimo = "pagina non scaricata"
    for suff in [""] + list(varianti):
        url = ff.costruisci_url(urn_base, suff, art, data_iso)
        try:
            html = _scarica(url)
        except Exception as e:
            ultimo = f"fetch fallito ({e.__class__.__name__})"
            continue
        testo = ff.estrai_testo_norma(html)
        if not testo:
            ultimo = "pagina scaricata ma testo non estraibile"
            continue
        if not ff._valida_articolo(testo, art):
            ultimo = f"la pagina risolta non contiene l'art. {art}"
            continue
        if not ff._valida_atto(html, urn_base):
            ultimo = f"la pagina risolta e' un ALTRO atto («{ff.titolo_atto(html)}»)"
            continue
        adesso = _dt.datetime.now().isoformat(timespec="seconds")
        header = {"riferimento": riferimento, "urn": urn_base, "url": url, "vig_richiesta": data_iso,
                  "versione": versione_txt, "versione_da": versione_da, "versione_a": versione_a,
                  "atto_titolo": ff.titolo_atto(html), "scaricato_il": adesso, "slug": slug}
        _scrivi_file(f, header, testo)
        return {"verdetto": "OK", "da_storico": True, "da_cache": False, "riferimento": riferimento,
                "descrizione": descr, "codice_locale": slug, "url": url, "vig": data_iso,
                "versione": versione_txt, "versione_da": versione_da, "versione_a": versione_a,
                "atto_titolo": header["atto_titolo"], "fetched_at": adesso, "atto_validato": True,
                "testo": testo, "file": str(f),
                "fonte": f"testo storico normattiva (permalink URN datato, scaricato ora, cache permanente) — {versione_txt}"}
    return _no(f"{ultimo} — {ff.costruisci_url(urn_base, '', art, data_iso)}")


def e_storico(data: str, oggi: _dt.date = None) -> bool:
    """True se `data` e' una data passata: il caso in cui lo storico ha voce in capitolo."""
    d = _data_iso(data)
    return bool(d) and d < (oggi or _oggi()).isoformat()


# ---------------------------------------------------------------- pre-warm e stato

def prewarm(slug: str, art: str, dal: str = "", oggi: _dt.date = None) -> list:
    """Un testo per ogni confine di versione dell'atto da `dal` in poi (job notturno, opzionale)."""
    _, indice = cl._indice(slug)
    if not indice:
        return [{"verdetto": "NON_DISPONIBILE", "motivo": f"nessuno snapshot locale per {slug}"}]
    cfg = cl.CODICI.get(slug) or {}
    rif = f"art. {art} {cfg.get('nome', slug)}"
    esiti = []
    for v in (indice.get("_meta") or {}).get("versioni") or []:
        if dal and v["data"] < dal:
            continue
        r = recupera(rif, v["data"], slug=slug, urn=cl.urn_permalink(slug) or cfg.get("urn"), oggi=oggi)
        esiti.append({"data": v["data"], "verdetto": r.get("verdetto"), "da_cache": r.get("da_cache"),
                      "motivo": r.get("motivo"), "file": r.get("file")})
    return esiti


def stato() -> dict:
    base = dir_storico()
    if not base.exists():
        return {"dir": str(base), "atti": 0, "testi": 0, "byte": 0}
    testi = [p for p in base.rglob("*.md")]
    return {"dir": str(base), "atti": len([d for d in base.iterdir() if d.is_dir()]),
            "testi": len(testi), "byte": sum(p.stat().st_size for p in testi)}


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Testo storico di un articolo alla data (normattiva URN datato, cache permanente).")
    ap.add_argument("--riferimento", help='es. "art. 5 D.Lgs. 28/2010"')
    ap.add_argument("--data", help="data ISO AAAA-MM-GG (anteriore a oggi)")
    ap.add_argument("--offline", action="store_true", help="solo cache: niente rete")
    ap.add_argument("--slug", help="forza lo slug del corpus (di norma dedotto dal riferimento)")
    ap.add_argument("--urn", help="forza l'URN base (test)")
    ap.add_argument("--prewarm", metavar="SLUG", help="scarica un testo per confine di versione (con --art)")
    ap.add_argument("--art", help="articolo per --prewarm")
    ap.add_argument("--dal", default="", help="per --prewarm: solo i confini da questa data")
    ap.add_argument("--stato", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.stato:
        s = stato()
        print(json.dumps(s, ensure_ascii=False, indent=1) if a.json else
              f"storico: {s['testi']} testi per {s['atti']} atti ({s['byte'] // 1024} KB) in {s['dir']}")
        return 0
    if a.prewarm:
        if not a.art:
            ap.error("--prewarm richiede --art")
        esiti = prewarm(a.prewarm, a.art, a.dal)
        if a.json:
            print(json.dumps(esiti, ensure_ascii=False, indent=1))
        else:
            for e in esiti:
                print(f"{e.get('data', '')} {e['verdetto']} {'(cache)' if e.get('da_cache') else ''} {e.get('motivo') or ''}".rstrip())
        return 0
    if not (a.riferimento and a.data):
        ap.error("servono --riferimento e --data (oppure --stato / --prewarm)")
    r = recupera(a.riferimento, a.data, offline=a.offline, slug=a.slug, urn=a.urn)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["verdetto"] == "OK" else 1
    if r["verdetto"] != "OK":
        print(f"NON_DISPONIBILE {r['motivo']}")
        return 1
    print(f"OK {a.riferimento} al {r['vig']}")
    print(f"FONTE: {r['url']}")
    print(f"FONTE-TIPO: {r['fonte']}")
    print(f"VERSIONE: {r['versione']}")
    print(f"SCARICATO: {r['fetched_at']}" + ("  (dalla cache storica permanente)" if r.get("da_cache") else ""))
    print(f"FILE: {r['file']}")
    print("TESTO:")
    print(r["testo"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
