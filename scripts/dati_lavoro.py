#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I NUMERI DEL LAVORO CHE CAMBIANO OGNI ANNO (v0.36): massimale NASpI, minimale e massimale contributivo,
assegno sociale, massimale della cassa integrazione, contributo di licenziamento — ciascuno con l'atto da cui e'
preso — e i coefficienti di rivalutazione del TFR calcolati dall'indice FOI.

PERCHE'
-------
Questi numeri non stanno su normattiva: li fissa ogni anno una circolare INPS (o un decreto). Una cifra dell'anno
sbagliato in una diffida o in un conteggio e' un errore che l'avversario vede subito. Qui ogni valore porta
anno, fonte (ente, atto, indirizzo, voce dell'indice della prassi) e data di verifica; un valore ESTRATTO deve
comparire nel testo della fonte (verifica_voce), uno CALCOLATO deve tornare identico rifacendo il conto.
Nessun numero a memoria: cio' che non e' verificato non entra.

FILE: `wiki-studio/lavoro/dati/dati-lavoro.json`
  {"_meta", "voci": {chiave: {descrizione, unita, cadenza, norma, watch: [parole delle circolari che lo
   cambiano], derivata?: {da, formula}, serie: {"AAAA": {valore, metodo: estratto|calcolato, fonte: {ente,
   atto, url, prassi_id}, verificato_il, formula?}}}}}

Coefficiente di rivalutazione del TFR (art. 2120, co. 4, c.c.): 1,5% annuo fisso, in proporzione ai mesi, piu' il
75% dell'aumento dell'indice FOI rispetto a dicembre dell'anno precedente (un aumento negativo non riduce la parte
fissa). Si calcola sul FOI della tabella del plugin (dati/tassi.json), coi raccordi fra basi del metodo ISTAT.

Uso:
  python3 scripts/dati_lavoro.py --calcola [--radice DIR] [--report FILE]     # voci derivate (es. ticket)
  python3 scripts/dati_lavoro.py --controlla [--radice DIR]                   # struttura, senza rete
  python3 scripts/dati_lavoro.py --verifica [--chiave K] [--anno AAAA]        # i numeri estratti sulla fonte
  python3 scripts/dati_lavoro.py --valore naspi_massimale_mensile --anno 2026
  python3 scripts/dati_lavoro.py --tfr 2026-08                                # coefficiente TFR del mese
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import preferisci_ipv4  # noqa: E402

preferisci_ipv4()

REL = "dati/dati-lavoro.json"
UA = "Mozilla/5.0 (corpus-normativo dati_lavoro)"
METODI = ("estratto", "calcolato")
OBBLIGATORI_VOCE = ("descrizione", "unita", "cadenza", "serie")


# ---------------------------------------------------------------- file

def percorso(radice: Path) -> Path:
    return Path(radice) / "wiki-studio" / "lavoro" / REL


def carica(radice: Path = None) -> dict:
    """Il file dalla radice data, oppure (nel plugin) dall'area lavoro sincronizzata o dal seme."""
    if radice is not None:
        try:
            return json.loads(percorso(radice).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"_meta": {}, "voci": {}}
    import lavoro as lv
    return lv.leggi_json(REL) or {"_meta": {}, "voci": {}}


def salva(radice: Path, dati: dict) -> None:
    p = percorso(radice)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(p)


# ---------------------------------------------------------------- numeri

def formato_it(x, decimali: int = 2) -> str:
    """1562.82 → «1.562,82» (la forma in cui le circolari scrivono gli importi)."""
    q = Decimal(str(x)).quantize(Decimal(1).scaleb(-decimali), rounding=ROUND_HALF_UP)
    intero, _, dec = f"{q:,.{decimali}f}".partition(".")
    return intero.replace(",", ".") + ("," + dec if decimali else "")


def forme_numero(x) -> list:
    """Le scritture con cui un importo puo' comparire nella fonte: «1.562,82», «1562,82», «1.562,8», «1.563»."""
    d = Decimal(str(x))
    out = {formato_it(d, 2), formato_it(d, 2).replace(".", "")}
    if d == d.to_integral_value():
        out |= {formato_it(d, 0), formato_it(d, 0).replace(".", "")}
    return sorted(out, key=len, reverse=True)


def _testo_fonte(url: str, get=None) -> str:
    if get:
        dati = get(url)
    else:
        from urllib.request import Request, urlopen
        with urlopen(Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            dati = r.read()
    if isinstance(dati, str):
        dati = dati.encode("utf-8")
    if dati[:5] == b"%PDF-":
        try:
            import corpus_contribuisci as cc
            return cc.testi_documento(dati)[0]
        except Exception:
            return ""
    t = dati.decode("utf-8", "replace")
    if t.lstrip().startswith("{"):          # frammento di contenuto (INPS: testoCompleto in HTML dentro il JSON)
        try:
            t = " ".join(v for v in json.loads(t).values() if isinstance(v, str))
        except ValueError:
            pass
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(t))


def verifica_voce(voce_serie: dict, get=None) -> dict:
    """Un valore ESTRATTO deve comparire nel testo della fonte in una forma italiana; uno CALCOLATO si rifa' con
    calcola()."""
    if voce_serie.get("metodo") != "estratto":
        return {"esito": "NON_APPLICABILE"}
    f = voce_serie.get("fonte") or {}
    url = f.get("url_testo") or f.get("url") or ""
    if not url:
        return {"esito": "SENZA_FONTE"}
    try:
        testo = _testo_fonte(url, get)
    except Exception as e:
        return {"esito": "FONTE_IRRAGGIUNGIBILE", "dettaglio": f"{e.__class__.__name__}"}
    for f in forme_numero(voce_serie.get("valore")):
        if re.search(r"(?<![\d.,])" + re.escape(f) + r"(?![\d]|,\d)", testo):
            return {"esito": "OK", "forma": f}
    return {"esito": "NON_TROVATO", "cercato": forme_numero(voce_serie.get("valore"))}


def valore(chiave: str, anno: int, dati: dict = None) -> dict:
    """{esito, valore, anno, fonte, avviso}: il valore dell'anno chiesto, o NON_DISPONIBILE (mai quello di un altro
    anno spacciato per buono)."""
    dati = dati if dati is not None else carica()
    v = (dati.get("voci") or {}).get(chiave)
    if not v:
        return {"esito": "CHIAVE_IGNOTA", "chiave": chiave, "chiavi": sorted(dati.get("voci") or {})}
    s = (v.get("serie") or {}).get(str(anno))
    if not s:
        anni = sorted(v.get("serie") or {})
        return {"esito": "NON_DISPONIBILE", "chiave": chiave, "anno": anno, "anni_disponibili": anni,
                "avviso": f"nessun valore {anno} verificato per «{v.get('descrizione')}»: leggerlo sulla fonte dell'anno"}
    return {"esito": "OK", "chiave": chiave, "anno": anno, "descrizione": v.get("descrizione"), "unita": v.get("unita"),
            **s}


# ---------------------------------------------------------------- voci derivate

def _arrot(x: Decimal, dec: int = 2) -> float:
    return float(x.quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP))


DERIVATE = {
    # art. 2, co. 31, L. 92/2012: per ogni 12 mesi di anzianita' (fino a 3 anni) il 41% del massimale mensile NASpI
    "ticket_licenziamento": ("naspi_massimale_mensile", lambda base: _arrot(Decimal(str(base)) * Decimal("0.41")),
                             "41% del massimale mensile NASpI dell'anno, per ogni 12 mesi di anzianita' aziendale (max 3)"),
}


def calcola(dati: dict, oggi: str = "") -> list:
    """Aggiorna le voci derivate dalle serie da cui dipendono. Ritorna le modifiche fatte."""
    oggi = oggi or _dt.date.today().isoformat()
    voci = dati.setdefault("voci", {})
    fatte = []
    for chiave, (da, f, formula) in DERIVATE.items():
        base = voci.get(da) or {}
        dest = voci.setdefault(chiave, {"descrizione": "contributo di licenziamento (ticket NASpI) per 12 mesi di anzianita'",
                                        "unita": "euro", "cadenza": "annuale", "norma": "art. 2, co. 31, L. 92/2012",
                                        "derivata": {"da": da, "formula": formula}, "serie": {}})
        for anno, s in (base.get("serie") or {}).items():
            nuovo = f(s["valore"])
            prec = (dest.get("serie") or {}).get(anno) or {}
            if prec.get("valore") != nuovo or prec.get("metodo") != "calcolato":
                dest.setdefault("serie", {})[anno] = {"valore": nuovo, "metodo": "calcolato", "formula": formula,
                                                      "fonte": {"da": da, **(s.get("fonte") or {})}, "verificato_il": oggi}
                fatte.append(f"{chiave} {anno} = {formato_it(nuovo)}")
    return fatte


def controlla(dati: dict) -> list:
    """Errori di struttura (senza rete): ogni voce completa, ogni valore con metodo, fonte e data; le derivate
    tornano col calcolo."""
    errori = []
    for k, v in (dati.get("voci") or {}).items():
        if not re.match(r"^[a-z0-9_]+$", k):
            errori.append(f"{k}: chiave non valida")
        for c in OBBLIGATORI_VOCE:
            if c not in v:
                errori.append(f"{k}: manca «{c}»")
        for anno, s in (v.get("serie") or {}).items():
            if not re.match(r"^\d{4}$", str(anno)):
                errori.append(f"{k} {anno}: anno non valido")
            if s.get("metodo") not in METODI:
                errori.append(f"{k} {anno}: metodo non fra {METODI}")
            if not isinstance(s.get("valore"), (int, float)):
                errori.append(f"{k} {anno}: valore non numerico")
            if not s.get("verificato_il"):
                errori.append(f"{k} {anno}: manca la data di verifica")
            f = s.get("fonte") or {}
            if s.get("metodo") == "estratto" and not (f.get("url") and f.get("atto")):
                errori.append(f"{k} {anno}: valore estratto senza atto e indirizzo della fonte")
    copia = json.loads(json.dumps(dati))
    for m in calcola(copia, oggi="0000-00-00"):
        errori.append(f"voce derivata non allineata al calcolo: {m}")
    return errori


# ---------------------------------------------------------------- TFR

def coefficiente_tfr(mese: str, tab: dict = None) -> dict:
    """Coefficiente di rivalutazione del TFR per il mese AAAA-MM (art. 2120, co. 4, c.c.): 1,5% × mesi/12 + 75%
    dell'aumento del FOI rispetto al dicembre precedente (zero se l'indice e' sceso), in percentuale a 6 decimali."""
    import tassi
    tab = tab if tab is not None else tassi.carica()
    a, m = int(mese[:4]), int(mese[5:7])
    dic = f"{a - 1}-12"
    r = tassi.coefficiente_foi(dic, f"{a}-{m:02d}", tab)
    if r.get("esito") != "OK":
        return {"esito": r.get("esito"), "motivo": r.get("motivo"), "mese": mese}
    aumento = (Decimal(str(r["coefficiente_esatto"])) - 1) * 100
    variabile = max(Decimal(0), aumento) * Decimal("0.75")
    fisso = Decimal("1.5") * m / 12
    coeff = (fisso + variabile).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return {"esito": "OK", "mese": f"{a}-{m:02d}", "coefficiente_pct": float(coeff), "parte_fissa_pct": float(fisso),
            "aumento_foi_pct": float(aumento.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
            "indice_dicembre": r["indice_da"], "indice_mese": r["indice_a"], "raccordi": r.get("raccordi"),
            "formula": "1,5% × mesi/12 + 75% × max(0, FOI mese / FOI dicembre precedente − 1), art. 2120 co. 4 c.c.",
            "fonte": r.get("fonte")}


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Numeri annuali del lavoro, con la fonte; coefficienti TFR.")
    ap.add_argument("--radice", default=None)
    ap.add_argument("--calcola", action="store_true")
    ap.add_argument("--controlla", action="store_true")
    ap.add_argument("--verifica", action="store_true")
    ap.add_argument("--chiave", default="")
    ap.add_argument("--valore", default="")
    ap.add_argument("--anno", type=int, default=_dt.date.today().year)
    ap.add_argument("--tfr", default="", metavar="AAAA-MM")
    ap.add_argument("--report", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    radice = Path(a.radice) if a.radice else None
    if a.tfr:
        r = coefficiente_tfr(a.tfr)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["esito"] == "OK" else 1
    if a.valore:
        r = valore(a.valore, a.anno, carica(radice))
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["esito"] == "OK" else 1
    rad = radice or Path(__file__).resolve().parents[1]
    dati = carica(rad)
    if a.calcola:
        fatte = calcola(dati)
        if fatte:
            dati.setdefault("_meta", {})["aggiornato_il"] = _dt.date.today().isoformat()
            salva(rad, dati)
        testo = "### Numeri annuali del lavoro\n\n" + ("".join(f"- {x}\n" for x in fatte) or "- nessuna voce derivata da aggiornare\n")
        print(testo)
        if a.report:
            with open(a.report, "a", encoding="utf-8") as f:
                f.write(testo + "\n")
        return 0
    if a.controlla:
        e = controlla(dati)
        print("dati-lavoro: " + ("OK" if not e else f"{len(e)} errori\n  " + "\n  ".join(e)))
        return 0 if not e else 1
    if a.verifica:
        esiti = {}
        for k, v in (dati.get("voci") or {}).items():
            if a.chiave and k != a.chiave:
                continue
            for anno, s in (v.get("serie") or {}).items():
                if a.chiave and str(a.anno) != anno:
                    continue
                esiti[f"{k} {anno}"] = verifica_voce(s)
        print(json.dumps(esiti, ensure_ascii=False, indent=1))
        return 0 if all(e["esito"] in ("OK", "NON_APPLICABILE") for e in esiti.values()) else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
