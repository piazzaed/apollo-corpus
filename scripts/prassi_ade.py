#!/usr/bin/env python3
"""INDICE DELLA PRASSI AdE SULLE SUCCESSIONI (v0.53): circolari, risoluzioni e risposte a interpello — numero, data,
oggetto, indirizzo (solo stdlib).

PERCHE'
-------
La prassi dell'Agenzia (la circolare 3/E del 16/4/2025 sul D.Lgs. 139/2024, le risoluzioni sui codici tributo, le risposte
a interpello su trust, prima casa, beni esteri…) e' la meta' del sapere sulle successioni, e normattiva non la pubblica. Qui
un indice cumulativo, dagli archivi del sito AdE (anno → mese → documento), filtrato per oggetto (successione, eredita',
donazione, de cuius, TUS, 139/2024…): dice CHE COSA c'e' e DOVE, cosi' la consulenza la trova subito e la legge alla fonte.
Non riproduce i documenti. Se un mese non risponde, le sue voci restano e l'errore si annota; esce solo una voce che non
passa piu' il filtro (`rilevante`: un termine forte, o uno debole nel contesto delle imposte indirette).

Uso:
  python3 scripts/prassi_ade.py --aggiorna [--dal 2014] [--out FILE]     # la sentinella: gli ultimi due anni
  python3 scripts/prassi_ade.py --cerca "prima casa"                     # dall'indice locale
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

ROOT = Path(__file__).resolve().parents[1]
INDICE = ROOT / "wiki-studio" / "successioni" / "prassi-ade.json"
SITO = "https://www.agenziaentrate.gov.it"
ARCHIVI = {
    "circolare": "/portale/web/guest/normativa-e-prassi/circolari/archivio-circolari",
    "risoluzione": "/portale/normativa-e-prassi/risoluzioni/archivio-risoluzioni",
    "risposta": "/portale/normativa-e-prassi/risposte-agli-interpelli/interpelli/archivio-interpelli",
}
#: l'oggetto che rende un documento rilevante per la corsia successioni: un termine FORTE basta; un termine DEBOLE (trust,
#: usufrutto, eredi, 347/1990…: compaiono anche nella prassi su redditi e compravendite) solo insieme a uno forte o a un
#: contesto di imposte indirette sui trasferimenti
RX_FORTE = re.compile(
    r"\bsuccession[ei]\b|\beredit[aà]\b|\bereditari[oa]?\b|\bdonazion[ei]\b|\bde cuius\b|\bdefunt[oa]\b|"
    r"\b346\b|139/2024|123/2025|imposta (?:sulle|di) successione|\bcoacervo\b|\bvoltur[ae]\b", re.I)
RX_DEBOLE = re.compile(r"\btrust\b|\busufrutto\b|\bnuda propriet|\beredi\b|\b347\b|\blegittim[ao]\b", re.I)
RX_CONTESTO = re.compile(r"impost[ae] (?:ipotecari|catastal|di registro|sulle donazioni|di donazione)|liberalit", re.I)
RX_SUCCESSIONI = re.compile(RX_FORTE.pattern + "|" + RX_DEBOLE.pattern, re.I)   # per evidenziare, non per filtrare


def rilevante(oggetto: str) -> bool:
    o = oggetto or ""
    return bool(RX_FORTE.search(o) or (RX_DEBOLE.search(o) and RX_CONTESTO.search(o)))
_RX_VOCE = re.compile(r"\b(Circolare|Risoluzione|Risposta|Principio di diritto)\s+n\.?\s*([0-9]+(?:/[A-Z])?)\s+del\s+"
                      r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+[a-zA-Z]+\s+\d{4})\s+(.*?)(?=\b(?:Circolare|Risoluzione|Risposta|"
                      r"Principio di diritto)\s+n\.?\s*[0-9]|L'Agenzia Chi siamo|$)", re.S)
MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre",
        "dicembre")


def _scarica(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (studio; prassi successioni)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def _testo(raw: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", t)))


def _data_iso(s: str) -> str:
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.match(r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})", s)
    if m and m.group(2).lower() in MESI:
        return f"{m.group(3)}-{MESI.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}"
    return ""


def voci_del_mese(raw: str, url_mese: str) -> list:
    """Le voci di una pagina mensile; il PDF si lega alla voce quando il nome del file porta il numero."""
    t = _testo(raw)
    pdf = [_html.unescape(h) for h in re.findall(r'href="([^"]+\.pdf[^"]*)"', raw)]
    out = []
    for tipo, num, data, oggetto in _RX_VOCE.findall(t):
        oggetto = re.sub(r"\s+", " ", oggetto).strip(" -–")[:400]
        n = num.split("/")[0]
        legato = next((h for h in pdf if re.search(r"(?:n\.?\+?|n_|N\.?\+?|numero\+?)" + re.escape(n) + r"(?!\d)", h)), "")
        out.append({"tipo": tipo.lower().replace("principio di diritto", "principio"), "numero": num,
                    "data": _data_iso(data), "oggetto": oggetto,
                    "url": (legato if legato.startswith("http") else SITO + legato) if legato else url_mese})
    return out


def _anni(tipo: str, dal: int) -> list:
    raw = _scarica(SITO + ARCHIVI[tipo])
    out = set()
    for h in re.findall(r'href="([^"]+)"', raw):
        m = re.search(r"(20\d{2})(?:/|$|\?)", h + "/")
        if m and int(m.group(1)) >= dal and "documents" not in h and "combo" not in h:
            out.add((int(m.group(1)), h if h.startswith("http") else SITO + h))
    corrente = _dt.date.today().year
    nomi = {"circolare": "circolari", "risoluzione": "risoluzioni", "risposta": "interpelli"}
    for a in range(max(dal, 2021), corrente + 1):        # le annate recenti stanno su /portale/<tipo>-<anno>
        out.add((a, f"{SITO}/portale/{nomi[tipo]}-{a}"))
    return sorted(out)


def _mesi(url_anno: str, anno: int) -> list:
    raw = _scarica(url_anno)
    hrefs = {h if h.startswith("http") else SITO + h for h in re.findall(r'href="([^"]+)"', raw)}
    # «/aprile-2025-circolari» (dal 2021) e «/circolari-2016/aprile-2016» (fino al 2020)
    return sorted(h for h in hrefs if re.search(r"/(?:" + "|".join(MESI) + r")-" + str(anno) + r"(?:-|/?$|\?)", h))


def carica() -> dict:
    try:
        return json.loads(INDICE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"_meta": {}, "documenti": []}


def aggiorna(dal: int, out: Path = INDICE, pausa: float = 0.1) -> dict:
    dati = carica() if out == INDICE else (json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"documenti": []})
    # il filtro e' un criterio, non una storia: una voce che non lo passa piu' (criterio ristretto) esce dall'indice
    dati["documenti"] = [d for d in dati.get("documenti") or [] if rilevante(d.get("oggetto"))]
    visti = {(d["tipo"], d["numero"], d["data"]) for d in dati["documenti"]}
    errori, nuovi, pagine = [], 0, 0
    for tipo in ARCHIVI:
        try:
            anni = _anni(tipo, dal)
        except Exception as e:  # noqa: BLE001
            errori.append(f"{tipo}: archivio non letto ({type(e).__name__})")
            continue
        fatti = set()
        for anno, url in anni:
            if anno in fatti:
                continue
            try:
                mesi = _mesi(url, anno)
            except Exception as e:  # noqa: BLE001
                errori.append(f"{tipo} {anno}: {type(e).__name__}")
                continue
            if mesi:
                fatti.add(anno)
            for um in mesi:
                try:
                    voci = voci_del_mese(_scarica(um), um)
                    pagine += 1
                except Exception as e:  # noqa: BLE001
                    errori.append(f"{um.rsplit('/', 1)[-1]}: {type(e).__name__}")
                    continue
                for v in voci:
                    chiave = (v["tipo"], v["numero"], v["data"])
                    if chiave in visti or not rilevante(v["oggetto"]):
                        continue
                    visti.add(chiave)
                    dati.setdefault("documenti", []).append(v)
                    nuovi += 1
                time.sleep(pausa)
    dati["documenti"] = sorted(dati.get("documenti") or [], key=lambda d: (d.get("data") or "", d.get("tipo")), reverse=True)
    dati["_meta"] = {"descrizione": "Prassi AdE su successioni e donazioni (circolari, risoluzioni, risposte a interpello): "
                                    "indice dagli archivi del sito AdE, filtrato per oggetto. Non riproduce i documenti.",
                     "verificato_il": _dt.date.today().isoformat(), "dal": dal, "pagine_lette": pagine,
                     "documenti": len(dati["documenti"]), "errori": errori[:50]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"nuovi": nuovi, "totale": len(dati["documenti"]), "pagine": pagine, "errori": errori}


def cerca(query: str, dati: dict = None, limite: int = 15) -> list:
    """Voci dell'indice per parole (tutte presenti nell'oggetto, senza accenti), le piu' recenti prima."""
    import unicodedata
    def n(s):
        s = unicodedata.normalize("NFKD", str(s or "")).lower()
        return "".join(c for c in s if not unicodedata.combining(c))
    parole = [p for p in re.split(r"\W+", n(query)) if len(p) > 2]
    dati = dati or carica()
    out = [d for d in dati.get("documenti") or [] if all(p in n(d.get("oggetto")) for p in parole)]
    return out[:limite]


def main() -> int:
    ap = argparse.ArgumentParser(description="Indice della prassi AdE sulle successioni")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--dal", type=int, default=_dt.date.today().year - 1)
    ap.add_argument("--out", default=str(INDICE))
    ap.add_argument("--cerca")
    a = ap.parse_args()
    if a.aggiorna:
        r = aggiorna(a.dal, Path(a.out))
        print(f"📚 prassi AdE: {r['nuovi']} nuovi, {r['totale']} in indice, {r['pagine']} pagine lette, {len(r['errori'])} errori")
        return 0
    if a.cerca:
        for d in cerca(a.cerca):
            print(f"{d['tipo']} n. {d['numero']} del {d['data']} — {d['oggetto'][:150]}\n   {d['url']}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
