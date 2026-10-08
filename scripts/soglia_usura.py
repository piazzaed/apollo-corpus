#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASSI SOGLIA ANTIUSURA da tabella locale, in meno di un secondo (solo stdlib).

PERCHE' (Piano v3 §11, replay 18-19/09/2026)
--------------------------------------------
Nel replay la soglia del trimestre e' stata cercata A MANO da un agente (WebSearch, pagine
secondarie, 3-4 turni) e la claim e' finita nel round come «residua» solo perche' la fonte non
era su normattiva. I tassi soglia sono un DATO, non un giudizio: Banca d'Italia pubblica la serie
storica completa (TEGM e soglie per trimestre, categoria e classe d'importo) in un CSV dentro
`TEGM_serie_storica.zip`, host in allowlist. Qui la serie vive in `dati/tassi-soglia.json` e la
risposta e' locale: TEGM, soglia, trimestre, formula, fonte — in millisecondi.

LA FORMULA (art. 2, co. 4, L. 108/1996, come sostituito dall'art. 8, co. 5, lett. d), D.L. 70/2011
conv. L. 106/2011 — in vigore dal 14/05/2011: la serie Banca d'Italia spezza il trimestre 2/2011 al 13/05):
    soglia = TEGM × 1,25 + 4 punti, con il tetto di TEGM + 8 punti  →  min(TEGM·1,25 + 4, TEGM + 8)
Prima (testo originario, fino al 13/05/2011): soglia = TEGM × 1,5. La tabella porta,
per ogni trimestre, il regime riconosciuto confrontando la soglia del CSV con le due formule.

COSA NON FA. Non sceglie la categoria al posto dell'avvocato: se la categoria chiesta ha piu'
classi d'importo e non si passa --classe/--importo, le mostra tutte. Non decide se il TEG del
contratto supera la soglia: quello lo fa scripts/calcoli/teg_taeg.py. Non inventa: fuori tabella
risponde FUORI_TABELLA con l'URL da cui aggiornare (`--aggiorna`) o il decreto da inserire.

NOTA SUI «NUMERI ATTESI» DEL PIANO (§17): TEGM 11,07% → soglia 17,8375% (trimestre 1/7-30/9/2024,
D.M. 24/06/2024, G.U. 151 del 29/06/2024) nella serie Banca d'Italia corrisponde alla categoria
«CREDITO FINALIZZATO ALL'ACQUISTO RATEALE» (classe unica), non ad «altri finanziamenti alle
famiglie e alle imprese» (che in quel trimestre ha TEGM 15,47 → soglia 23,34). Il finanziamento
auto del replay e' un credito finalizzato: i numeri tornano, l'etichetta del piano no.

DUE FONTI, UNA TABELLA (v0.29, 23/09/2026). La serie storica di Banca d'Italia (zip) e' ferma al
trimestre 1/7-30/9/2025 (pubblicata il 18/06/2025): i trimestri successivi si leggono dall'Allegato A del
decreto MEF (PDF sul sito del Dipartimento del Tesoro, lo stesso testo della G.U.) con `--da-decreto`.
Il parser riconosce le 24 righe della classificazione (D.M. MEF di classificazione annuale; ultima 23/09/2025),
controlla ogni soglia con la formula di legge e salva la categoria col NOME DELLA SERIE Banca d'Italia
(la stessa query trova la stessa categoria prima e dopo; il nome del decreto resta in `categoria_decreto`).
`--aggiorna` dallo zip conserva i trimestri letti dai decreti successivi all'ultimo trimestre del CSV.

Uso:
  python3 scripts/soglia_usura.py --data 2024-03-10 --categoria "credito finalizzato" [--json]
  python3 scripts/soglia_usura.py --data 2024-08-01 --categoria "altri finanziamenti" [--classe "intera"] [--importo 12000]
  python3 scripts/soglia_usura.py --categorie --data 2025-07-01        # le categorie del trimestre
  python3 scripts/soglia_usura.py --aggiorna [--da-zip FILE.zip]         # rilegge la serie Banca d'Italia
  python3 scripts/soglia_usura.py --da-decreto Decreto-tassi-usura-luglio-settembre-2026.pdf|.txt \\
          --decreto "D.M. MEF 23 giugno 2026" --gu "G.U. Serie Generale n. 149 del 30/06/2026" --codice 26A03259
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import os
import re
import sys
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8 (accenti, frecce, emoji)
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT  # noqa: E402

TABELLA = ROOT / "dati" / "tassi-soglia.json"
URL_ZIP = "https://www.bancaditalia.it/compiti/vigilanza/compiti-vigilanza/tegm/TEGM_serie_storica.zip"
URL_PAGINA = "https://www.bancaditalia.it/compiti/vigilanza/compiti-vigilanza/tegm/index.html"
UA = "Mozilla/5.0 (corpus-normativo soglia_usura)"
TIMEOUT = float(os.environ.get("FONTI_TIMEOUT") or 30)
#: Trimestri anteriori a questa data restano nel CSV ma non in tabella (regime TEGM×1,5, lire): si
#: caricano con --aggiorna --dal 1997-04-02 se una pratica lo richiede.
DAL_DEFAULT = "2010-01-01"
#: Oltre questi giorni dall'ultima verifica lo script lo dice (i decreti sono trimestrali).
CADENZA_GIORNI = 95

URL_DECRETI_MEF = "https://www.dt.mef.gov.it/it/attivita_istituzionali/sistema_bancario_finanziario/anti_usura/categorie_creditizie/"

#: Decreti di cui gli ESTREMI sono stati letti su fonte primaria (sommario G.U.). Il CSV di Banca
#: d'Italia non li porta: per gli altri trimestri il decreto e' «da_verificare» con l'URL del sommario.
#: Gli estremi letti restano anche nella tabella (trimestre.decreto) e sopravvivono a --aggiorna.
DECRETI_VERIFICATI = {
    "2024-07-01": {"decreto": "D.M. MEF 24 giugno 2024", "gu": "G.U. Serie Generale n. 151 del 29/06/2024",
                   "codice_redazionale": "24A03347",
                   "url": "https://www.gazzettaufficiale.it/eli/id/2024/06/29/24A03347/sg",
                   "verificato_il": "2026-09-19", "verificato_su": "sommario G.U. 151/2024 e testo dell'atto (art. 1)"},
}

#: Errori materiali della serie storica Banca d'Italia riscontrati sulla fonte primaria (G.U.) e corretti in costruzione.
CORREZIONI_CSV = {
    "2020-07-01": {"fine": "2020-09-30",
                   "fonte": "titolo del D.M. MEF 25 giugno 2020, G.U. Serie Generale n. 163 del 30/06/2020 (20A03453): «Applicazione dal "
                            "1° luglio al 30 settembre 2020»; il CSV Banca d'Italia riporta come fine trimestre 01/09/2020 "
                            "(senza la correzione le date dal 2 al 30 settembre 2020 risultavano FUORI_TABELLA)"},
}

#: Allegato A dei decreti trimestrali (classificazione MEF annuale, invariata nella sostanza dal 2017; D.M. 23/09/2025):
#: (nome nel decreto, parola chiave nel testo, numero di classi, nome della serie Banca d'Italia). L'ordine e' quello
#: della tabella; 24 righe in tutto. Se il MEF cambia la classificazione il parser si ferma (PARSER_FALLITO).
CATEGORIE_DECRETO = (
    ("APERTURE DI CREDITO IN CONTO CORRENTE", r"APERTURE\s+DI\s+CREDITO", 2, "APERTURE DI CREDITO IN CONTO CORRENTE"),
    ("SCOPERTI SENZA AFFIDAMENTO", r"SCOPERTI\s+SENZA\s+AFFIDAMENTO", 2, "SCOPERTI SENZA AFFIDAMENTO (dal 1° gennaio 2010)"),
    ("FINANZIAMENTI PER ANTICIPI SU CREDITI E DOCUMENTI E SCONTO DI PORTAFOGLIO COMMERCIALE, FINANZIAMENTI ALL'IMPORTAZIONE E ANTICIPO FORNITORI",
     r"ANTICIPI\s+SU\s+CREDITI", 3, "ANTICIPI, SCONTI COMMERCIALI E FINANZIAMENTI ALL'IMPORTAZIONE"),
    ("CREDITO PERSONALE", r"CREDITO\s+PERSONALE", 1, "CREDITO PERSONALE (dal 1° gennaio 2010)"),
    ("CREDITO FINALIZZATO", r"CREDITO\s+FINALIZZATO", 1, "CREDITO FINALIZZATO ALL'ACQUISTO RATEALE"),
    ("FACTORING", r"FACTORING", 2, "FACTORING"),
    ("LEASING IMMOBILIARE A TASSO FISSO", r"LEASING\s+IMMOBILIARE", 1, "LEASING IMMOBILIARE A TASSO FISSO (dal 1° aprile 2011)"),
    ("LEASING IMMOBILIARE A TASSO VARIABILE", r"TASSO\s+VARIABILE", 1, "LEASING IMMOBILIARE A TASSO VARIABILE (dal 1° aprile 2011)"),
    ("LEASING AERONAVALE E SU AUTOVEICOLI", r"LEASING\s+AERONAVALE", 2, "LEASING AUTOVEICOLI E AERONAVALI (dal 1° gennaio 2010)"),
    ("LEASING STRUMENTALE", r"LEASING\s+STRUMENTALE", 2, "LEASING STRUMENTALE (dal 1° gennaio 2010)"),
    ("MUTUI CON GARANZIA IPOTECARIA A TASSO FISSO", r"MUTUI\s+CON\s+GARANZIA", 1, "MUTUI IPOTECARI A TASSO FISSO (dal 1° luglio 2004)"),
    ("MUTUI CON GARANZIA IPOTECARIA A TASSO VARIABILE", r"TASSO\s+VARIABILE", 1, "MUTUI IPOTECARI A TASSO VARIABILE (dal 1° luglio 2004)"),
    ("PRESTITI CONTRO CESSIONE DEL QUINTO DELLO STIPENDIO E DELLA PENSIONE", r"CESSIONE\s+DEL\s+QUINTO", 2,
     "PRESTITI CONTRO CESSIONE DEL QUINTO STIPENDIO E PENSIONE (dal 1° gennaio 2010)"),
    ("CREDITO REVOLVING", r"CREDITO\s+REVOLVING", 1, "CREDITO REVOLVING (dal 1° gennaio 2010)"),
    ("FINANZIAMENTI CON UTILIZZO DI CARTE DI CREDITO", r"CARTE\s+DI\s+CREDITO", 1, "FINANZIAMENTI RATEALI CON CARTE DI CREDITO (dal 1° aprile 2017)"),
    ("ALTRI FINANZIAMENTI", r"ALTRI\s+FINANZIAMENTI", 1, "ALTRI FINANZIAMENTI ALLE FAMIGLIE E ALLE IMPRESE (dal 1° aprile 2010)"),
)
_MESI_IT = {"GENNAIO": 1, "FEBBRAIO": 2, "MARZO": 3, "APRILE": 4, "MAGGIO": 5, "GIUGNO": 6, "LUGLIO": 7, "AGOSTO": 8,
            "SETTEMBRE": 9, "OTTOBRE": 10, "NOVEMBRE": 11, "DICEMBRE": 12}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"\([^)]*\)", " ", s)          # «(dal 1° gennaio 2010)»
    s = s.replace("'", " ").replace("’", " ")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def _num(s: str):
    try:
        return float(str(s).strip().replace(".", "").replace(",", "."))
    except ValueError:
        return None


def _iso(ggmmaaaa: str) -> str:
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", str(ggmmaaaa).strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def soglia_formula(tegm: float, regime: str = "dl70-2011") -> float:
    """La soglia dal TEGM. `dl70-2011`: min(TEGM·1,25+4, TEGM+8); `originario`: TEGM·1,5."""
    if regime == "originario":
        return round(tegm * 1.5, 4)
    return round(min(tegm * 1.25 + 4.0, tegm + 8.0), 4)


def _regime(tegm: float, soglia_csv) -> str:
    """Riconosce la formula dal valore pubblicato (tolleranza di arrotondamento a 2 decimali)."""
    if soglia_csv is None:
        return "ignoto"
    if abs(soglia_formula(tegm, "dl70-2011") - soglia_csv) <= 0.0051:
        return "dl70-2011"
    if abs(soglia_formula(tegm, "originario") - soglia_csv) <= 0.0051:
        return "originario"
    return "non_riconosciuto"


# ---------------------------------------------------------------- costruzione della tabella

def _leggi_csv_zip(dati_zip: bytes) -> list:
    with zipfile.ZipFile(io.BytesIO(dati_zip)) as z:
        nomi = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not nomi:
            raise ValueError("nessun CSV nello zip")
        grezzo = z.read(nomi[0])
    for enc in ("utf-8-sig", "latin-1"):
        try:
            testo = grezzo.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    righe = list(csv.reader(io.StringIO(testo), delimiter=";"))
    if not righe or len(righe[0]) < 6:
        raise ValueError("CSV con intestazione inattesa: " + ";".join(righe[0] if righe else []))
    return righe


def _prossima_verifica(trimestri: list, oggi: _dt.date) -> str:
    """Il decreto del trimestre successivo esce negli ultimi giorni del trimestre coperto: si riverifica allora
    (al piu' tardi dopo CADENZA_GIORNI). Se la tabella e' gia' scaduta la data e' nel passato e l'avviso scatta."""
    limite = oggi + _dt.timedelta(days=CADENZA_GIORNI)
    try:
        fine = _dt.date.fromisoformat(trimestri[-1]["fine"]) - _dt.timedelta(days=2)
        return min(limite, fine).isoformat()
    except (IndexError, KeyError, TypeError, ValueError):
        return limite.isoformat()


def _decreto_verificato(ini: str, precedente: dict = None):
    """Estremi del decreto del trimestre gia' letti (tabella precedente o DECRETI_VERIFICATI), altrimenti None."""
    for t in (precedente or {}).get("trimestri") or []:
        d = t.get("decreto") or {}
        if t.get("inizio") == ini and d.get("da_verificare") is False:
            return d
    dec = DECRETI_VERIFICATI.get(ini)
    return {**dec, "da_verificare": False} if dec else None


def costruisci_tabella(righe: list, dal: str = DAL_DEFAULT, oggi: _dt.date = None, origine: str = URL_ZIP, precedente: dict = None) -> dict:
    """La tabella JSON dalle righe del CSV Banca d'Italia (INIZIO;FINE;CATEGORIA;CLASSE;TEGM;SOGLIA).

    `precedente` (la tabella in uso): se ne conservano gli estremi verificati dei decreti e i trimestri letti dai
    decreti MEF (`origine: decreto MEF`) successivi all'ultimo trimestre del CSV."""
    oggi = oggi or _dt.date.today()
    trimestri: dict = {}
    scartate = 0
    for r in righe[1:]:
        if len(r) < 6:
            continue
        ini, fine = _iso(r[0]), _iso(r[1])
        tegm, sog = _num(r[4]), _num(r[5])
        if not ini or tegm is None or ini < dal:
            scartate += 1
            continue
        corr = CORREZIONI_CSV.get(ini)
        if corr and fine != corr["fine"]:
            fine = corr["fine"]
        t = trimestri.setdefault(ini, {"inizio": ini, "fine": fine, "voci": []})
        if corr:
            t["correzione"] = corr["fonte"]
        regime = _regime(tegm, sog)
        t["voci"].append({"categoria": r[2].strip(), "classe": r[3].strip(), "tegm": tegm, "soglia_pubblicata": sog,
                          "soglia_calcolata": soglia_formula(tegm, "originario" if regime == "originario" else "dl70-2011"),
                          "regime": regime})
    out_trim = []
    for ini in sorted(trimestri):
        t = trimestri[ini]
        regimi = {v["regime"] for v in t["voci"]}
        t["regime"] = "dl70-2011" if regimi == {"dl70-2011"} else ("originario" if regimi == {"originario"} else "misto/da_verificare")
        t["origine"] = "csv Banca d'Italia"
        dec = _decreto_verificato(ini, precedente)
        if dec:
            t["decreto"] = dec
        else:
            t["decreto"] = {"decreto": None, "gu": None, "da_verificare": True,
                            "come_verificare": ("sommario G.U. del decreto MEF «Rilevazione dei tassi di interesse effettivi globali medi ai fini "
                                                f"della legge sull'usura … Applicazione dal {ini}» — "
                                                "https://www.gazzettaufficiale.it/ (archivio della Serie Generale) oppure la pagina TEGM " + URL_PAGINA)}
        out_trim.append(t)
    ultimo_csv = out_trim[-1]["inizio"] if out_trim else ""
    decreti_prec = {t["inizio"]: t for t in (precedente or {}).get("trimestri") or [] if t.get("origine") == "decreto MEF"}
    # il decreto e' l'atto legale: dove un trimestre e' stato letto dal decreto (es. 1/1-31/3/2018, TEGM a 4 decimali
    # che il CSV arrotonda a 2) prevale sul CSV anche dentro il periodo coperto dalla serie storica
    out_trim = [decreti_prec.get(t["inizio"], t) for t in out_trim]
    da_decreti = [t for ini, t in sorted(decreti_prec.items()) if ini > ultimo_csv]
    out_trim += da_decreti
    return {
        "_meta": {
            "descrizione": "Tassi effettivi globali medi (TEGM) e tassi soglia antiusura per trimestre, categoria e classe d'importo. "
                           "Costruita da scripts/soglia_usura.py --aggiorna dalla serie storica di Banca d'Italia (CSV ufficiale): "
                           "nessun valore scritto a mano.",
            "fonte": "Banca d'Italia — Tassi Effettivi Globali Medi (TEGM) ex L. 108/96, serie storica (TEGM_serie_storica.zip)",
            "url": origine, "url_pagina": URL_PAGINA,
            "verificato_il": oggi.isoformat(),
            "prossima_verifica": _prossima_verifica(out_trim, oggi),
            "cadenza": "trimestrale: il D.M. MEF esce a fine marzo/giugno/settembre/dicembre; --aggiorna riscarica la serie",
            "formula": {"dl70-2011": "soglia = min(TEGM × 1,25 + 4, TEGM + 8) — art. 2 co. 4 L. 108/1996 come sostituito dall'art. 8 co. 5 lett. d) D.L. 70/2011 conv. L. 106/2011 (in vigore dal 14/05/2011)",
                        "originario": "soglia = TEGM × 1,5 — art. 2 co. 4 L. 108/1996, testo originario (fino al 13/05/2011)",
                        "nota": "soglia_calcolata = formula applicata al TEGM con 4 decimali; soglia_pubblicata = valore del CSV (2 decimali). "
                                "Vale la formula di legge: 11,07 → 17,8375 (il CSV arrotonda a 17,84)."},
            "decreti": "gli estremi del D.M. e della G.U. sono in tabella solo per i trimestri verificati su fonte primaria (decreto.da_verificare=false); "
                       "per gli altri il valore e' comunque quello ufficiale di Banca d'Italia, ma l'estremo va letto dal sommario G.U.",
            "dal": dal, "trimestri": len(out_trim), "righe_csv_scartate": scartate, "origine_dati": "csv Banca d'Italia",
            "ultimo_trimestre_csv": ultimo_csv,
            "trimestri_da_decreto": [t["inizio"] for t in out_trim if t.get("origine") == "decreto MEF"],
            "correzioni_csv": {t["inizio"]: t["correzione"] for t in out_trim if t.get("correzione")},
            "nota_fonti": ("serie Banca d'Italia (CSV) fino all'ultimo trimestre pubblicato; i trimestri successivi e quelli in cui il decreto "
                           "porta il TEGM con piu' decimali del CSV (1/1-31/3/2018) sono letti dall'Allegato A del decreto MEF; il decreto prevale"),
            "url_decreti": URL_DECRETI_MEF,
            "copertura": {"dal": out_trim[0]["inizio"] if out_trim else None, "al": out_trim[-1].get("fine") if out_trim else None},
        },
        "trimestri": out_trim,
    }


# ---------------------------------------------------------------- trimestri dai decreti MEF (Allegato A)

def _classe_csv(classe_decreto: str) -> str:
    c = " ".join(str(classe_decreto or "").split())
    return f"{c} euro" if c else "intera distribuzione"


def _data_it(giorno: str, mese: str, anno: str) -> str:
    return f"{int(anno):04d}-{_MESI_IT[mese.upper()]:02d}-{int(giorno):02d}"


def parse_decreto(testo: str) -> dict:
    """L'Allegato A di un decreto trimestrale MEF (testo di `pdftotext -layout` o testo della G.U.).

    Ritorna {esito: OK, inizio, fine, rilevazione, voci:[{categoria, categoria_decreto, classe, tegm, soglia_pubblicata}]}
    oppure {esito: PARSER_FALLITO, motivo}. Nessuna riga e' accettata se la soglia pubblicata non torna con la formula."""
    t = testo.replace(" ", " ")
    m = re.search(r"APPLICAZIONE\s+DAL\s+1\s*[°º]?\s*([A-Z]+)\s*(\d{4})?\s+(?:FINO\s+)?AL\s+(\d{1,2})\s+([A-Z]+)\s+(\d{4})", t, re.I)
    if not m:
        return {"esito": "PARSER_FALLITO", "motivo": "manca l'intestazione «APPLICAZIONE DAL 1° … AL …» dell'Allegato A"}
    anno_fine = m.group(5)
    inizio = _data_it("1", m.group(1), m.group(2) or anno_fine)
    fine = _data_it(m.group(3), m.group(4), anno_fine)
    r = re.search(r"RILEVAZIONE:\s*1\s*[°º]?\s*([A-Z]+)\s*(\d{4})?\s*[-–]\s*(\d{1,2})\s+([A-Z]+)\s+(\d{4})", t, re.I)
    rilevazione = f"{_data_it('1', r.group(1), r.group(2) or r.group(5))} → {_data_it(r.group(3), r.group(4), r.group(5))}" if r else None
    i0 = t.upper().find("CATEGORIE DI OPERAZIONI", m.end())
    i1 = t.upper().find("AVVERTENZA", i0 if i0 >= 0 else m.end())
    if i0 < 0 or i1 < 0:
        return {"esito": "PARSER_FALLITO", "motivo": "non trovo la tabella (da «CATEGORIE DI OPERAZIONI» ad «AVVERTENZA»)"}
    blocco = t[i0:i1]
    righe = []
    for riga in blocco.splitlines():
        q = re.search(r"(fino a [\d.]+|oltre [\d.]+|da [\d.]+ a [\d.]+)?\s*(\d{1,2},\d{2,4})\s+(\d{1,2},\d{4})\s*$", riga.strip(), re.I)
        if q:
            righe.append({"classe": q.group(1) or "", "tegm": _num(q.group(2)), "soglia": _num(q.group(3)),
                          "decimali_tegm": len(q.group(2).split(",")[1])})
    attese = sum(c[2] for c in CATEGORIE_DECRETO)
    if len(righe) != attese:
        return {"esito": "PARSER_FALLITO", "motivo": f"righe riconosciute {len(righe)}, attese {attese}: la classificazione o l'impaginazione sono cambiate"}
    pos = 0
    for nome, chiave, _n, _csv in CATEGORIE_DECRETO:
        mm = re.compile(chiave, re.I).search(blocco, pos)
        if not mm:
            return {"esito": "PARSER_FALLITO", "motivo": f"categoria «{nome}» non trovata nell'ordine atteso"}
        pos = mm.end()
    voci, k = [], 0
    for nome, _chiave, n, nome_csv in CATEGORIE_DECRETO:
        for _ in range(n):
            rr = righe[k]
            k += 1
            if (n > 1) != bool(rr["classe"]):
                return {"esito": "PARSER_FALLITO", "motivo": f"«{nome}»: classi d'importo non coerenti ({rr['classe'] or 'nessuna'})"}
            calcolata = soglia_formula(rr["tegm"], "dl70-2011")
            # TEGM a 2 decimali: la soglia a 4 decimali e' esatta; TEGM a 4 decimali (es. decreto per 1/1-31/3/2018):
            # il MEF arrotonda/tronca la soglia al quarto decimale partendo dal tasso non arrotondato (scarto ≤ 0,0001)
            tolleranza = 0.00005 if rr["decimali_tegm"] <= 2 else 0.00011
            if abs(calcolata - rr["soglia"]) > tolleranza:
                return {"esito": "PARSER_FALLITO", "motivo": f"«{nome}» {rr['classe']}: soglia pubblicata {rr['soglia']} ≠ formula {calcolata} (TEGM {rr['tegm']})"}
            voci.append({"categoria": nome_csv, "categoria_decreto": nome, "classe": _classe_csv(rr["classe"]), "tegm": rr["tegm"],
                         "soglia_pubblicata": rr["soglia"], "soglia_calcolata": calcolata, "regime": "dl70-2011"})
    return {"esito": "OK", "inizio": inizio, "fine": fine, "rilevazione": rilevazione, "voci": voci}


def testo_da_file(percorso: str) -> str:
    """Testo del decreto: .txt/.html letti come sono; .pdf via `pdftotext -layout` se disponibile."""
    p = Path(percorso)
    if p.suffix.lower() == ".pdf":
        import shutil
        import subprocess
        if not shutil.which("pdftotext"):
            raise RuntimeError("pdftotext non disponibile: estrarre il testo (pdftotext -layout) e passare il .txt")
        return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    return p.read_text(encoding="utf-8", errors="replace")


def aggiungi_decreto(testo: str, decreto: str = None, gu: str = None, codice: str = None, url: str = None,
                     dest: Path = None, oggi: _dt.date = None) -> dict:
    """Aggiunge (o sostituisce) il trimestre letto dall'Allegato A di un decreto MEF."""
    oggi = oggi or _dt.date.today()
    dest = Path(dest or TABELLA)
    p = parse_decreto(testo)
    if p["esito"] != "OK":
        return p
    tab = json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {"_meta": {}, "trimestri": []}
    trimestre = {"inizio": p["inizio"], "fine": p["fine"], "voci": p["voci"], "regime": "dl70-2011", "origine": "decreto MEF",
                 "rilevazione": p["rilevazione"],
                 "decreto": {"decreto": decreto, "gu": gu, "codice_redazionale": codice,
                             "url": url or (f"https://www.gazzettaufficiale.it/eli/id/{codice}" if codice else URL_DECRETI_MEF),
                             "testo_letto": "Allegato A del decreto (PDF del Dipartimento del Tesoro)", "verificato_il": oggi.isoformat(),
                             "da_verificare": not (decreto and gu)}}
    tab["trimestri"] = sorted([t for t in tab.get("trimestri") or [] if t.get("inizio") != p["inizio"]] + [trimestre], key=lambda t: t["inizio"])
    meta = tab.setdefault("_meta", {})
    meta["trimestri"] = len(tab["trimestri"])
    meta["trimestri_da_decreto"] = [t["inizio"] for t in tab["trimestri"] if t.get("origine") == "decreto MEF"]
    meta["copertura"] = {"dal": tab["trimestri"][0]["inizio"], "al": tab["trimestri"][-1].get("fine")}
    meta["verificato_il"] = oggi.isoformat()
    meta["prossima_verifica"] = _prossima_verifica(tab["trimestri"], oggi)
    meta["url_decreti"] = URL_DECRETI_MEF
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(tab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"esito": "AGGIUNTO", "trimestre": f"{p['inizio']} → {p['fine']}", "voci": len(p["voci"]), "file": str(dest)}


def aggiorna(da_zip: str = None, dal: str = DAL_DEFAULT, dest: Path = None, oggi: _dt.date = None) -> dict:
    """Riscarica la serie (o la legge da uno zip locale) e riscrive la tabella. Scrive SOLO cio' che legge."""
    dest = Path(dest or TABELLA)
    if da_zip:
        dati = Path(da_zip).read_bytes()
        origine = f"file locale {Path(da_zip).name} (copia di {URL_ZIP})"
    else:
        try:
            import ambiente as _amb
            hc = _amb.host_consentito(URL_ZIP)
            if hc["consentito"] is False:
                return {"esito": "HOST_BLOCCATO", "motivo": hc["motivo"], "istruzione": hc["istruzione"], "url": URL_ZIP}
        except Exception:
            pass
        from urllib.request import Request, urlopen
        try:
            with urlopen(Request(URL_ZIP, headers={"User-Agent": UA}), timeout=TIMEOUT) as r:
                dati = r.read()
        except Exception as e:
            codice = getattr(e, "code", None)
            return {"esito": "HOST_BLOCCATO" if codice in (403, 407, 451) else "HOST_NON_RAGGIUNGIBILE",
                    "motivo": f"{e.__class__.__name__}: {e}", "url": URL_ZIP,
                    "istruzione": "scaricare TEGM_serie_storica.zip dalla pagina Banca d'Italia e rilanciare con --da-zip FILE"}
        origine = URL_ZIP
    try:
        righe = _leggi_csv_zip(dati)
    except Exception as e:
        return {"esito": "PARSER_FALLITO", "motivo": f"{e.__class__.__name__}: {e}", "url": URL_ZIP}
    precedente = {}
    if dest.exists():
        try:
            precedente = json.loads(dest.read_text(encoding="utf-8"))
        except ValueError:
            precedente = {}
    tab = costruisci_tabella(righe, dal=dal, oggi=oggi, origine=origine, precedente=precedente)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(tab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ultimo = tab["trimestri"][-1]["inizio"] if tab["trimestri"] else None
    return {"esito": "AGGIORNATA", "file": str(dest), "trimestri": len(tab["trimestri"]), "ultimo_trimestre": ultimo,
            "verificato_il": tab["_meta"]["verificato_il"]}


# ---------------------------------------------------------------- interrogazione

def _tabella() -> Path:
    """v0.36: la tabella aggiornata dalle sentinelle automatiche (copia del corpus pubblico) se vale, o quella del bundle."""
    try:
        import aree as _ar
        return _ar.file("dati/tassi-soglia.json") or TABELLA
    except Exception:
        return TABELLA


def carica(path: Path = None) -> dict:
    p = Path(path) if path else _tabella()
    if not p.exists():
        return {}
    try:
        tab = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    for t in tab.get("trimestri") or []:
        for v in t.get("voci") or []:
            v.setdefault("categoria_norm", _norm(v.get("categoria")))
            v.setdefault("classe_norm", _norm(v.get("classe")))
    return tab


def trimestre_per(tab: dict, data_iso: str):
    for t in tab.get("trimestri") or []:
        if t["inizio"] <= data_iso <= (t.get("fine") or "9999-12-31"):
            return t
    return None


def _classe_per_importo(voci: list, importo: float):
    """La classe d'importo che contiene `importo` («fino a 5.000 euro», «da 50.000 a 200.000 euro», «oltre 5.000 euro»)."""
    for v in voci:
        c = re.sub(r"(\d)[ .](?=\d{3}\b)", r"\1", v["classe_norm"])   # «5 000» / «5.000» → 5000
        c = re.sub(r"(\d)[ .](?=\d{3}\b)", r"\1", c)
        m = re.search(r"fino a (\d+)", c)
        if m and importo <= float(m.group(1)):
            return v
        m = re.search(r"da (\d+) a (\d+)", c)
        if m and float(m.group(1)) < importo <= float(m.group(2)):
            return v
        m = re.search(r"oltre (\d+)", c)
        if m and importo > float(m.group(1)):
            return v
    return None


def cerca(data_iso: str, categoria: str, classe: str = None, importo: float = None, tab: dict = None, oggi: _dt.date = None) -> dict:
    """TEGM e soglia della categoria alla data. Esiti: OK | PIU_CLASSI | CATEGORIA_NON_TROVATA | FUORI_TABELLA | TABELLA_ASSENTE."""
    tab = tab if tab is not None else carica()
    oggi = oggi or _dt.date.today()
    base = {"data": data_iso, "categoria_richiesta": categoria, "fonte": (tab.get("_meta") or {}).get("fonte"),
            "url": (tab.get("_meta") or {}).get("url_pagina", URL_PAGINA)}
    if not tab.get("trimestri"):
        return {**base, "esito": "TABELLA_ASSENTE", "motivo": f"tabella {TABELLA} mancante o vuota: python3 scripts/soglia_usura.py --aggiorna ({URL_ZIP})"}
    meta = tab["_meta"]
    avvisi = []
    try:
        pv = _dt.date.fromisoformat(meta.get("prossima_verifica"))
        if oggi > pv:
            avvisi.append(f"tabella verificata il {meta.get('verificato_il')}: prossima verifica prevista il {pv.isoformat()} — python3 scripts/soglia_usura.py --aggiorna")
    except (TypeError, ValueError):
        pass
    t = trimestre_per(tab, data_iso)
    if not t:
        ultimo = tab["trimestri"][-1]
        return {**base, "esito": "FUORI_TABELLA", "avvisi": avvisi,
                "motivo": (f"nessun trimestre per il {data_iso} (tabella dal {tab['trimestri'][0]['inizio']} al {ultimo.get('fine')}): "
                           f"aggiorna con --aggiorna ({URL_ZIP}) o --da-decreto con l'Allegato A del decreto MEF del trimestre ({URL_DECRETI_MEF})")}
    q = _norm(categoria)
    parole = q.split()
    cand = [v for v in t["voci"] if all(p in v["categoria_norm"].split() or p in v["categoria_norm"] for p in parole)]
    if not cand:
        return {**base, "esito": "CATEGORIA_NON_TROVATA", "trimestre": {"inizio": t["inizio"], "fine": t["fine"]},
                "categorie_disponibili": sorted({v["categoria"] for v in t["voci"]}),
                "motivo": f"nessuna categoria del trimestre contiene «{categoria}»"}
    categorie = sorted({v["categoria"] for v in cand})
    if len(categorie) > 1:
        # «finanziamenti» prende tutto: si tiene la categoria piu' corta che contiene tutte le parole
        cand = [v for v in cand if v["categoria"] == min(categorie, key=len)]
        avvisi.append("piu' categorie compatibili: " + " | ".join(categorie) + f" → scelta «{cand[0]['categoria']}» (restringi la richiesta se non e' quella)")
    voci = cand
    if classe:
        cq = _norm(classe)
        voci = [v for v in cand if cq in v["classe_norm"]] or cand
    elif importo is not None and len(cand) > 1:
        v = _classe_per_importo(cand, float(importo))
        voci = [v] if v else cand
    dec = t.get("decreto") or {}
    comune = {**base, "trimestre": {"inizio": t["inizio"], "fine": t["fine"]}, "regime": t.get("regime"),
              "formula": (meta.get("formula") or {}).get(t.get("regime"), ""),
              "decreto": dec, "categoria": voci[0]["categoria"], "avvisi": avvisi,
              "fonte_tipo": ("primaria (decreto MEF, Allegato A letto e riscontrato con la formula)" if t.get("origine") == "decreto MEF"
                             else "primaria (Banca d'Italia, serie storica TEGM)" if meta.get("origine_dati") == "csv Banca d'Italia" else "tabella locale"),
              "origine_trimestre": t.get("origine"),
              "verificato_il": meta.get("verificato_il")}
    if len(voci) > 1:
        return {**comune, "esito": "PIU_CLASSI", "classi": [{"classe": v["classe"], "tegm": v["tegm"], "soglia": v["soglia_calcolata"],
                                                            "soglia_pubblicata": v["soglia_pubblicata"]} for v in voci],
                "motivo": "la categoria ha piu' classi d'importo: passa --classe o --importo"}
    v = voci[0]
    return {**comune, "esito": "OK", "classe": v["classe"], "tegm": v["tegm"], "soglia": v["soglia_calcolata"],
            "soglia_pubblicata": v["soglia_pubblicata"]}


def _pct(x) -> str:
    return (f"{x:.4f}".rstrip("0").rstrip(".") if x is not None else "n/d").replace(".", ",") + "%"


def stampa(r: dict) -> None:
    if r["esito"] == "OK":
        d = r.get("decreto") or {}
        print(f"OK {r['categoria']} — classe {r['classe']} — trimestre {r['trimestre']['inizio']} → {r['trimestre']['fine']}")
        print(f"  TEGM {_pct(r['tegm'])} · SOGLIA {_pct(r['soglia'])} (pubblicata {_pct(r['soglia_pubblicata'])})")
        print(f"  formula: {r['formula']}")
        print(f"  decreto: {d.get('decreto') or 'estremi da verificare'} · {d.get('gu') or ''}".rstrip(" ·")
              + (f" · {d.get('url')}" if d.get("url") else "") + ("  [da_verificare]" if d.get("da_verificare") else ""))
        print(f"  fonte: {r['fonte_tipo']} — {r['url']} (tabella verificata il {r['verificato_il']})")
    elif r["esito"] == "PIU_CLASSI":
        print(f"PIU_CLASSI {r['categoria']} — trimestre {r['trimestre']['inizio']} → {r['trimestre']['fine']}: {r['motivo']}")
        for c in r["classi"]:
            print(f"  {c['classe']:<28} TEGM {_pct(c['tegm'])} · soglia {_pct(c['soglia'])}")
    else:
        print(f"{r['esito']}: {r.get('motivo')}")
        if r.get("categorie_disponibili"):
            print("  categorie: " + " | ".join(r["categorie_disponibili"]))
    for a in r.get("avvisi") or []:
        print(f"  ⚠ {a}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tassi soglia antiusura (Banca d'Italia) dalla tabella locale, < 1 s.")
    ap.add_argument("--data", help="data del contratto/della pattuizione (AAAA-MM-GG)")
    ap.add_argument("--categoria", help='es. "credito finalizzato", "altri finanziamenti", "credito personale", "mutui tasso fisso"')
    ap.add_argument("--classe", help='classe d\'importo, es. "fino a 5.000", "oltre", "intera"')
    ap.add_argument("--importo", type=float, help="importo del finanziamento: sceglie la classe")
    ap.add_argument("--categorie", action="store_true", help="elenca le categorie del trimestre di --data (o dell'ultimo)")
    ap.add_argument("--aggiorna", action="store_true", help="riscarica la serie storica Banca d'Italia e riscrive dati/tassi-soglia.json")
    ap.add_argument("--da-zip", help="con --aggiorna: usa uno zip locale (offline / test)")
    ap.add_argument("--dal", default=DAL_DEFAULT, help=f"con --aggiorna: primo trimestre da tenere (default {DAL_DEFAULT})")
    ap.add_argument("--da-decreto", help="aggiunge il trimestre dall'Allegato A del decreto MEF (.pdf con pdftotext, oppure .txt)")
    ap.add_argument("--decreto", help='con --da-decreto: estremi, es. "D.M. MEF 23 giugno 2026"')
    ap.add_argument("--gu", help='con --da-decreto: es. "G.U. Serie Generale n. 149 del 30/06/2026"')
    ap.add_argument("--codice", help="con --da-decreto: codice redazionale G.U. (es. 26A03259)")
    ap.add_argument("--url", help="con --da-decreto: URL del PDF/atto letto")
    ap.add_argument("--tabella", help="file tabella alternativo (test)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.da_decreto:
        try:
            testo = testo_da_file(a.da_decreto)
        except (OSError, RuntimeError) as e:
            print(f"ERRORE: {e}"); return 1
        r = aggiungi_decreto(testo, a.decreto, a.gu, a.codice, a.url, dest=a.tabella)
        print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else f"{r['esito']}: {r.get('trimestre') or r.get('motivo')}")
        return 0 if r["esito"] == "AGGIUNTO" else 1
    if a.aggiorna:
        r = aggiorna(a.da_zip, dal=a.dal, dest=a.tabella)
        print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else
              (f"{r['esito']}: {r.get('trimestri', '')} trimestri, ultimo {r.get('ultimo_trimestre')} → {r.get('file')}" if r["esito"] == "AGGIORNATA"
               else f"{r['esito']}: {r.get('motivo')} — {r.get('istruzione', '')} ({r.get('url')})"))
        return 0 if r["esito"] == "AGGIORNATA" else 1
    tab = carica(a.tabella)
    if a.categorie:
        data = a.data or ((tab.get("trimestri") or [{}])[-1].get("inizio") or "")
        t = trimestre_per(tab, data) if data else None
        if not t:
            print("FUORI_TABELLA: nessun trimestre per la data"); return 1
        print(f"trimestre {t['inizio']} → {t['fine']} ({len(t['voci'])} voci):")
        for v in t["voci"]:
            print(f"  {v['categoria']:<75} {v['classe']:<26} TEGM {_pct(v['tegm'])} soglia {_pct(v['soglia_calcolata'])}")
        return 0
    if not (a.data and a.categoria):
        ap.print_help(); return 2
    r = cerca(a.data, a.categoria, classe=a.classe, importo=a.importo, tab=tab)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        stampa(r)
    return 0 if r["esito"] in ("OK", "PIU_CLASSI") else 1


if __name__ == "__main__":
    sys.exit(main())
