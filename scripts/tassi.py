#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASSI E INDICI DI RIFERIMENTO alla data, da tabella locale (solo stdlib).

PERCHE' (Piano v3 §11, replay 18-19/09/2026; revisione v0.29 del 23/09/2026)
--------------------------------------------------------------------------
Il tasso legale, il tasso di mora commerciale, il tasso BCE, l'indice FOI, il rendimento dei BOT: sono
DATI, non giudizi, e la rete della VM Cowork spesso non arriva alle fonti. Vivono in `dati/tassi.json`
(una serie per tipo, ognuna con `_meta`: fonte, URL, verificato_il, prossima_verifica; ogni voce con la
propria `fonte`) e lo script risponde in millisecondi: valore alla data, atto che lo fissa, fonte.
DISCIPLINA DEI DATI: una voce entra SOLO se letta su fonte ufficiale (G.U., normattiva, BCE, ISTAT,
Banca d'Italia, MEF); le altre restano `da_verificare` con l'URL da cui prenderle, e lo script si FERMA
(esito DA_VERIFICARE) invece di rispondere con un numero non letto.

SERIE (dati/tassi.json)
  legale            art. 1284 c.c.: 5% (c.c. 1942) → 10% dal 16/12/1990 (L. 353/1990) → 5% dal 1/1/1997
                    (L. 662/1996) → D.M. MEF annuali (dal 1999). Vale la voce con `dal` piu' recente.
  mora_commerciale  art. 5 D.Lgs. 231/2002: tasso di riferimento BCE del semestre (in vigore il 1° gennaio /
                    1° luglio; prima del D.Lgs. 192/2012: quello della piu' recente operazione di
                    rifinanziamento principale effettuata il primo giorno di calendario del semestre)
                    + 8 punti (transazioni concluse dal 1/1/2013) o + 7 punti (transazioni anteriori).
                    Il riferimento del semestre e' quello pubblicato dal MEF in G.U. (voce con codice
                    redazionale) o, dove il comunicato non e' in tabella, il tasso BCE della serie `bce`
                    in vigore il primo giorno del semestre (voce marcata «calcolato dalla serie BCE»).
  bce               tasso sulle operazioni di rifinanziamento principali (tasso fisso; minimo di offerta nelle
                    aste a tasso variabile 28/06/2000-14/10/2008) — BCE Data Portal.
  istat_foi         indice FOI senza tabacchi, mensile, con le basi e i coefficienti di raccordo ISTAT;
                    `coefficiente_foi(da, a)` applica il metodo ISTAT (rapporto × raccordi × Cst 1,0009
                    a cavallo di febbraio 1992, arrotondamento finale a 3 decimali).
  bot12             aste dei BOT a 12 mesi (nuove emissioni, vita residua ≥ 330 giorni): rendimento medio
                    ponderato di aggiudicazione (Banca d'Italia); `finestra_117(data)` da' minimo e massimo
                    dei BOT annuali emessi nei dodici mesi precedenti (art. 117 co. 7 TUB).

Aggiornamento (scrive solo cio' che legge):
  --aggiorna --tipo legale --gu-data AAAA-MM-GG --codice NNANNNNN        decreto MEF sulla G.U.
  --aggiorna --tipo mora_commerciale --gu-data AAAA-MM-GG --codice ...    comunicato MEF sulla G.U.
  --aggiorna --tipo bce                                                  BCE Data Portal (CSV)
  --aggiorna --tipo istat_foi --mese AAAA-MM --indice 103,7 --url URL     indice letto sulla pagina ISTAT
  --aggiorna --tipo bot12 --da-file comunicato.txt                        comunicato MEF dell'asta

Uso:
  python3 scripts/tassi.py --tipo legale --data 2024-03-10 [--json]
  python3 scripts/tassi.py --tipo mora_commerciale --data 2025-09-01 [--data-transazione 2012-05-01]
  python3 scripts/tassi.py --tipo istat_foi --data 2026-08-01
  python3 scripts/tassi.py --tipo istat_foi --coefficiente 2009-01 2026-01     # metodo ISTAT: 1,336
  python3 scripts/tassi.py --tipo bot12 --data 2025-03-01 --finestra-117
  python3 scripts/tassi.py --tipo legale --serie                               # la serie con lo stato
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT  # noqa: E402

TABELLA = ROOT / "dati" / "tassi.json"
TIPI = ("legale", "mora_commerciale", "bot12", "bce", "istat_foi")
UA = "Mozilla/5.0 (corpus-normativo tassi)"
TIMEOUT = float(os.environ.get("FONTI_TIMEOUT") or 25)
GU_ARTICOLO = ("https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticoloDefault/originario"
               "?atto.dataPubblicazioneGazzetta={data}&atto.codiceRedazionale={codice}&atto.tipoProvvedimento={tipo}")
ECB_CSV = "https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.{serie}.LEV?format=csvdata"
#: transazioni concluse dal 1/1/2013: + 8 punti (art. 3 co. 1 D.Lgs. 192/2012); prima: + 7
DATA_REGIME_192_2012 = "2013-01-01"
#: coefficiente ISTAT per gli intervalli a cavallo di febbraio 1992 (indice senza tabacchi)
MESE_SENZA_TABACCHI = "1992-02"


def _tabella() -> Path:
    """v0.36: la tabella aggiornata dalle sentinelle automatiche (copia del corpus pubblico) se vale, o quella del bundle."""
    try:
        import aree as _ar
        return _ar.file("dati/tassi.json") or TABELLA
    except Exception:
        return TABELLA


def carica(path: Path = None) -> dict:
    p = Path(path) if path else _tabella()
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _json_compatto(obj, livello: int = 0) -> str:
    """JSON leggibile: dizionari indentati, ma le voci delle liste (serie, basi) una per riga."""
    ind = " " * livello
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        parti = [f'{ind} {json.dumps(k, ensure_ascii=False)}: {_json_compatto(v, livello + 1)}' for k, v in obj.items()]
        return "{\n" + ",\n".join(parti) + "\n" + ind + "}"
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        return "[\n" + ",\n".join(f"{ind}  " + json.dumps(x, ensure_ascii=False) for x in obj) + "\n" + ind + " ]"
    return json.dumps(obj, ensure_ascii=False)


def _salva(dati: dict, path: Path = None) -> None:
    p = Path(path or TABELLA)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json_compatto(dati) + "\n", encoding="utf-8")


def _avvisi_meta(meta: dict, oggi: _dt.date) -> list:
    out = []
    try:
        pv = _dt.date.fromisoformat(str(meta.get("prossima_verifica")))
        if oggi > pv:
            out.append(f"serie verificata il {meta.get('verificato_il') or 'mai'}: prossima verifica prevista il {pv.isoformat()} — {meta.get('url')}")
    except (TypeError, ValueError):
        pass
    return out


def _mese(data_iso: str) -> str:
    return str(data_iso)[:7]


# ---------------------------------------------------------------- interrogazione

def cerca(tipo: str, data_iso: str, tab: dict = None, oggi: _dt.date = None, data_transazione: str = None) -> dict:
    """Il valore del tipo alla data. Esiti: OK | DA_VERIFICARE | FUORI_TABELLA | TIPO_IGNOTO | TABELLA_ASSENTE.

    `data_transazione` (solo mora_commerciale): data di conclusione del contratto; se anteriore al 1/1/2013 la
    maggiorazione e' di 7 punti anche per i semestri successivi (art. 3 D.Lgs. 192/2012)."""
    tab = tab if tab is not None else carica()
    oggi = oggi or _dt.date.today()
    if tipo not in TIPI:
        return {"esito": "TIPO_IGNOTO", "tipo": tipo, "motivo": f"tipi ammessi: {', '.join(TIPI)}"}
    serie_obj = tab.get(tipo) or {}
    meta = serie_obj.get("_meta") or {}
    base = {"tipo": tipo, "data": data_iso, "nome": meta.get("nome"), "fonte": meta.get("fonte"), "url": meta.get("url"),
            "unita": meta.get("unita"), "formula": meta.get("formula"), "avvisi": _avvisi_meta(meta, oggi),
            "verificato_il": meta.get("verificato_il")}
    serie = serie_obj.get("serie") or []
    if not serie_obj:
        return {**base, "esito": "TABELLA_ASSENTE", "motivo": f"tabella {TABELLA} senza la serie «{tipo}»"}
    if tipo == "bot12":
        voci = [v for v in serie if str(v.get("asta") or "") <= data_iso]
        if not voci:
            return {**base, "esito": "FUORI_TABELLA", "motivo": f"nessuna asta BOT in tabella fino al {data_iso}: {serie_obj.get('come_aggiungere') or meta.get('url')}"}
        v = voci[-1]
        campo = "rendimento_medio_ponderato" if v.get("rendimento_medio_ponderato") is not None else "rendimento_minimo"
        if v.get("da_verificare") or v.get(campo) is None:
            return {**base, "esito": "DA_VERIFICARE", "voce": v, "motivo": f"asta {v.get('asta')}: rendimento non letto su fonte primaria — {v.get('url') or meta.get('url')}"}
        return {**base, "esito": "OK", "valore": v[campo], "campo": campo, "dal": v["asta"], "voce": v,
                "atto": f"asta BOT del {v['asta']} ({v.get('descrizione') or '12 mesi'})",
                "fonte_tipo": "primaria (Banca d'Italia, risultati delle aste)" if "Banca d'Italia" in str(v.get("fonte")) else "primaria (MEF)",
                "fonte_voce": v.get("fonte"), "nota": v.get("nota")}
    if tipo == "mora_commerciale":
        voci = [v for v in serie if str(v.get("dal") or "") <= data_iso <= str(v.get("al") or "9999")]
        if not voci:
            return {**base, "esito": "FUORI_TABELLA", "motivo": f"nessun semestre in tabella per il {data_iso}: {meta.get('url')}"}
        v = voci[-1]
        avvisi = list(base["avvisi"])
        if data_iso < DATA_REGIME_192_2012:
            magg = serie_obj.get("maggiorazione_punti_ante_2013", 7)
        elif data_transazione and str(data_transazione) < DATA_REGIME_192_2012:
            magg = serie_obj.get("maggiorazione_punti_ante_2013", 7)
            avvisi.append(f"transazione conclusa il {data_transazione} (prima del 1/1/2013): maggiorazione {magg} punti (art. 3 co. 1 D.Lgs. 192/2012)")
        else:
            magg = serie_obj.get("maggiorazione_punti", 8)
            if not data_transazione:
                avvisi.append(f"maggiorazione {magg} punti: presuppone una transazione conclusa dal 1/1/2013 (se anteriore: --data-transazione)")
        if v.get("da_verificare") or v.get("riferimento_bce") is None:
            return {**base, "esito": "DA_VERIFICARE", "voce": v, "maggiorazione_punti": magg, "avvisi": avvisi,
                    "motivo": (f"semestre {v.get('dal')}→{v.get('al')}: tasso di riferimento non letto su fonte primaria — "
                               f"{v.get('nota') or ''} {v.get('url') or meta.get('url')}; formula: riferimento + {magg} punti").replace("  ", " ")}
        return {**base, "esito": "OK", "valore": round(float(v["riferimento_bce"]) + magg, 4), "riferimento_bce": v["riferimento_bce"],
                "maggiorazione_punti": magg, "dal": v["dal"], "al": v.get("al"), "atto": v.get("atto") or "comunicato MEF in G.U.",
                "gu": v.get("gu"), "codice_redazionale": v.get("codice_redazionale"), "url_atto": v.get("url"), "avvisi": avvisi,
                "fonte_tipo": "primaria (G.U., comunicato MEF)" if v.get("codice_redazionale") else "primaria (serie BCE, tasso in vigore il primo giorno del semestre)",
                "fonte_voce": v.get("fonte"), "verificato_il_voce": v.get("verificato_il"), "nota": v.get("nota")}
    if tipo == "istat_foi":
        mese = _mese(data_iso)
        voce = next((v for v in serie if v.get("mese") == mese), None)
        if voce is None:
            ultimo = serie[-1].get("mese") if serie else None
            return {**base, "esito": "FUORI_TABELLA", "ultimo_mese": ultimo,
                    "motivo": f"indice FOI di {mese} non in tabella (serie {serie[0].get('mese') if serie else '?'} → {ultimo}): "
                              f"ISTAT lo pubblica a meta' del mese successivo — {meta.get('url')}"}
        if voce.get("da_verificare") or voce.get("valore") is None:
            return {**base, "esito": "DA_VERIFICARE", "voce": voce, "motivo": f"indice di {mese} non letto su fonte primaria — {meta.get('url')}"}
        return {**base, "esito": "OK", "valore": voce["valore"], "mese": mese, "base": voce.get("base"), "dal": voce.get("dal"),
                "atto": f"indice FOI senza tabacchi, {mese} (base {voce.get('base')})", "fonte_tipo": "primaria (ISTAT)",
                "fonte_voce": voce.get("fonte"), "nota": voce.get("nota")}
    # legale / bce: serie con «dal»; vale l'ultima voce non posteriore alla data
    voci = [v for v in serie if str(v.get("dal") or "") <= data_iso]
    if not voci:
        primo = serie[0].get("dal") if serie else None
        return {**base, "esito": "FUORI_TABELLA", "motivo": f"nessuna voce «{tipo}» in tabella fino al {data_iso}" + (f" (serie dal {primo})" if primo else "") + f": {meta.get('url')}"}
    v = voci[-1]
    if v.get("da_verificare") or v.get("valore") is None:
        return {**base, "esito": "DA_VERIFICARE", "voce": v, "dal": v.get("dal"),
                "motivo": f"voce dal {v.get('dal')}: valore non letto su fonte primaria — {v.get('nota') or ''} {v.get('url') or meta.get('url')}".strip()}
    if v.get("codice_redazionale"):
        ft = "primaria (G.U., testo del decreto)"
    elif tipo == "bce":
        ft = "primaria (BCE Data Portal)"
    elif v.get("fonte"):
        ft = "primaria (" + str(v.get("fonte_tipo") or "normattiva") + ")"
    else:
        ft = "tabella locale"
    return {**base, "esito": "OK", "valore": v["valore"], "dal": v["dal"], "atto": v.get("decreto") or v.get("atto"),
            "gu": v.get("gu"), "codice_redazionale": v.get("codice_redazionale"), "url_atto": v.get("url"),
            "fonte_tipo": ft, "fonte_voce": v.get("fonte"),
            "verificato_il_voce": v.get("verificato_il"), "nota": v.get("nota")}


# ---------------------------------------------------------------- ISTAT FOI: coefficienti (metodo ISTAT)

def _cmp_mese(a: str, b: str) -> int:
    return (a > b) - (a < b)


def coefficiente_foi(da_mese: str, a_mese: str, tab: dict = None) -> dict:
    """Coefficiente per tradurre valori monetari del mese `da_mese` in valuta del mese `a_mese` (AAAA-MM).

    Metodo ISTAT («Indice dei prezzi per le rivalutazioni monetarie», nota metodologica 2026): rapporto degli
    indici × coefficienti di raccordo tra basi contigue (tanti quanti i cambi di base nell'intervallo) × Cst
    1,0009 se l'intervallo e' a cavallo di febbraio 1992; un solo passaggio senza arrotondamenti intermedi;
    coefficiente arrotondato a 3 decimali, variazione percentuale a 1 decimale.
    Esiti: OK | FUORI_TABELLA | ORDINE (a_mese anteriore a da_mese)."""
    tab = tab if tab is not None else carica()
    s = tab.get("istat_foi") or {}
    serie = {v["mese"]: v for v in (s.get("serie") or []) if v.get("mese") and v.get("valore") is not None}
    da_mese, a_mese = _mese(da_mese), _mese(a_mese)
    for m in (da_mese, a_mese):
        if m not in serie:
            mesi = sorted(serie)
            return {"esito": "FUORI_TABELLA", "mese": m, "ultimo_mese": mesi[-1] if mesi else None,
                    "motivo": f"indice FOI di {m} non in tabella ({mesi[0] if mesi else '?'} → {mesi[-1] if mesi else '?'})"}
    if _cmp_mese(a_mese, da_mese) < 0:
        return {"esito": "ORDINE", "motivo": f"il mese di arrivo {a_mese} precede quello di partenza {da_mese}"}
    v0, v1 = serie[da_mese], serie[a_mese]
    raccordi = []
    for b in s.get("basi") or []:
        # un cambio di base «entra» nell'intervallo se la nuova base inizia dopo da_mese e non dopo a_mese
        if b.get("raccordo_con_precedente") and da_mese < b["dal_mese"] <= a_mese:
            raccordi.append({"base": b["base"], "dal_mese": b["dal_mese"], "coefficiente": b["raccordo_con_precedente"]})
    cst = s.get("coefficiente_senza_tabacchi") or {}
    usa_cst = bool(cst.get("valore")) and da_mese < MESE_SENZA_TABACCHI <= a_mese
    esatto = float(v1["valore"]) / float(v0["valore"])
    for r in raccordi:
        esatto *= float(r["coefficiente"])
    if usa_cst:
        esatto *= float(cst["valore"])
    return {"esito": "OK", "da_mese": da_mese, "a_mese": a_mese, "indice_da": v0["valore"], "base_da": v0.get("base"),
            "indice_a": v1["valore"], "base_a": v1.get("base"), "raccordi": raccordi, "cst": float(cst["valore"]) if usa_cst else None,
            "coefficiente_esatto": esatto, "coefficiente": round(esatto + 1e-12, 3),
            "variazione_pct": round((esatto - 1) * 100 + 1e-12, 1),
            "formula": "coefficiente = I(a)/I(da) × Π raccordi" + (" × Cst 1,0009" if usa_cst else "") + " (metodo ISTAT, 3 decimali)",
            "fonte": (s.get("_meta") or {}).get("fonte")}


def ultimo_mese_foi(tab: dict = None):
    tab = tab if tab is not None else carica()
    mesi = [v["mese"] for v in ((tab.get("istat_foi") or {}).get("serie") or []) if v.get("valore") is not None]
    return max(mesi) if mesi else None


# ---------------------------------------------------------------- BOT: finestra dell'art. 117 co. 7 TUB

def finestra_117(data_iso: str, tab: dict = None) -> dict:
    """Minimo e massimo dei rendimenti dei BOT annuali emessi (data di regolamento) nei 12 mesi precedenti `data_iso`.

    Art. 117 co. 7 lett. a) TUB: in caso di nullita' della clausola sui tassi si applica «il tasso nominale
    minimo e quello massimo, rispettivamente per le operazioni attive e per quelle passive, dei buoni ordinari
    del tesoro annuali o di altri titoli similari ... emessi nei dodici mesi precedenti la conclusione del
    contratto». Il valore di ogni asta e' il rendimento medio ponderato di aggiudicazione (Banca d'Italia)."""
    tab = tab if tab is not None else carica()
    d = _dt.date.fromisoformat(data_iso)
    try:
        inizio = d.replace(year=d.year - 1)
    except ValueError:          # 29 febbraio
        inizio = d.replace(year=d.year - 1, day=28)
    voci = [v for v in ((tab.get("bot12") or {}).get("serie") or [])
            if v.get("rendimento_medio_ponderato") is not None and inizio.isoformat() <= str(v.get("regolamento") or v.get("asta")) < data_iso]
    if not voci:
        return {"esito": "FUORI_TABELLA", "motivo": f"nessuna emissione di BOT annuali in tabella fra il {inizio.isoformat()} e il {data_iso}"}
    mn = min(voci, key=lambda v: v["rendimento_medio_ponderato"])
    mx = max(voci, key=lambda v: v["rendimento_medio_ponderato"])
    return {"esito": "OK", "dal": inizio.isoformat(), "al_escluso": data_iso, "emissioni": len(voci),
            "minimo": mn["rendimento_medio_ponderato"], "asta_minimo": mn["asta"], "massimo": mx["rendimento_medio_ponderato"], "asta_massimo": mx["asta"],
            "norma": "art. 117 co. 7 lett. a) TUB: minimo per le operazioni attive, massimo per le passive",
            "fonte": ((tab.get("bot12") or {}).get("_meta") or {}).get("fonte")}


def _pct(x) -> str:
    return (f"{float(x):.4f}".rstrip("0").rstrip(".").replace(".", ",") + "%") if x is not None else "n/d"


def stampa(r: dict) -> None:
    if r["esito"] == "OK":
        unita = "" if r["tipo"] == "istat_foi" else "%"
        val = (f"{r['valore']}".replace(".", ",") + f" (base {r.get('base')})") if r["tipo"] == "istat_foi" else _pct(r["valore"])
        print(f"OK {r['tipo']} al {r['data']}: {val}" + (f" (dal {r['dal']})" if r.get("dal") and unita else ""))
        if r.get("riferimento_bce") is not None:
            print(f"  = riferimento BCE {_pct(r['riferimento_bce'])} + {r['maggiorazione_punti']} punti — art. 5 D.Lgs. 231/2002")
        print(f"  atto: {r.get('atto') or 'n/d'}" + (f" · {r['gu']}" if r.get("gu") else "") + (f" · {r['url_atto']}" if r.get("url_atto") else ""))
        print(f"  fonte: {r.get('fonte_tipo')} — {r.get('fonte_voce') or r.get('fonte')}" + (f" (verificata il {r.get('verificato_il_voce') or r.get('verificato_il')})" if r.get("verificato_il_voce") or r.get("verificato_il") else ""))
        if r.get("nota"):
            print(f"  nota: {r['nota']}")
    else:
        print(f"{r['esito']}: {r.get('motivo')}")
    for a in r.get("avvisi") or []:
        print(f"  ⚠ {a}")


# ---------------------------------------------------------------- aggiornamento (solo cio' che si legge)

def _testo_html(h: str) -> str:
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    t = re.sub(r"(?s)<[^>]+>", "\n", h)
    t = _html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)


def _scaricatore(url: str):
    """(scarica(url)->str, errore) — rispetta la mappa host di ambiente.py."""
    try:
        import ambiente as _amb
        hc = _amb.host_consentito(url)
        if hc["consentito"] is False:
            return None, {"esito": "HOST_BLOCCATO", "motivo": hc["motivo"], "istruzione": hc["istruzione"], "url": url}
    except Exception:
        pass
    from urllib.request import Request, urlopen

    def scarica(u):
        with urlopen(Request(u, headers={"User-Agent": UA}), timeout=TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    return scarica, None


def _errore_rete(e, url) -> dict:
    codice_http = getattr(e, "code", None)
    return {"esito": "HOST_BLOCCATO" if codice_http in (403, 407, 451) else "HOST_NON_RAGGIUNGIBILE",
            "motivo": f"{e.__class__.__name__}: {e}", "url": url}


def parse_decreto_legale(testo: str) -> dict:
    """Dal testo del decreto: {valore, dal, decreto} oppure {} se non riconosciuto.
    Forma attesa (letta su 14 decreti 2009-2025): «La misura del saggio degli interessi legali di cui
    all'art. 1284 del codice civile e' fissata al X per cento in ragione d'anno, con decorrenza dal 1° gennaio AAAA»."""
    t = " ".join(testo.split())
    # solo la parte dispositiva: le premesse («Visto il decreto … con decorrenza dal 1° gennaio 2004») citano il
    # decreto precedente e ingannavano il parser (bug trovato il 23/09/2026 sui decreti 2007, 2010, 2013)
    k = re.search(r"\bDecreta\b\s*:?", t, re.I)
    disp = t[k.end():] if k else t
    m = re.search(r"saggio degli interessi legali.{0,120}?fissat[ao]\s+(?:al|all'|allo)\s*(\d+(?:[,.]\d+)?)\s*(?:per cento|%)", disp, re.I)
    if not m:
        return {}
    valore = float(m.group(1).replace(",", "."))
    a = re.search(r"decorrenza dal 1\s*[°ºo]?\s*gennaio\s*(\d{4})", disp[m.start():], re.I)
    d = re.search(r"Roma,\s*(\d{1,2})\s*[°º]?\s+([a-z]+)\s+(\d{4})", disp, re.I)
    return {"valore": valore, "dal": f"{a.group(1)}-01-01" if a else None,
            "decreto": f"D.M. MEF {int(d.group(1))} {d.group(2).lower()} {d.group(3)}" if d else "D.M. MEF"}


def aggiorna_legale(gu_data: str, codice: str, tab: dict = None, path: Path = None, scarica=None, oggi: _dt.date = None,
                    gu_numero: str = None) -> dict:
    """Legge l'art. 1 del decreto sulla G.U. e scrive la voce. `scarica(url)->html` iniettabile (test)."""
    tab = tab if tab is not None else carica(path)
    oggi = oggi or _dt.date.today()
    url = GU_ARTICOLO.format(data=gu_data, codice=codice, tipo="DECRETO")
    if scarica is None:
        scarica, err = _scaricatore(url)
        if err:
            return err
    try:
        testo = _testo_html(scarica(url))
    except Exception as e:
        return _errore_rete(e, url)
    p = parse_decreto_legale(testo)
    if not p or not p.get("dal"):
        return {"esito": "PARSER_FALLITO", "motivo": "il testo scaricato non contiene la formula attesa «fissata al X per cento … dal 1° gennaio AAAA»: inserire a mano dopo lettura", "url": url}
    serie_obj = tab.setdefault("legale", {"_meta": {}, "serie": []})
    serie = serie_obj.setdefault("serie", [])
    m = re.search(r"Serie Generale n\.\s*(\d+)\s+del\s+(\d{1,2}-\d{1,2}-\d{4})", testo)
    voce = {"dal": p["dal"], "valore": p["valore"], "decreto": p["decreto"],
            "gu": (f"G.U. Serie Generale n. {m.group(1)} del {m.group(2).replace('-', '/')}" if m else
                   f"G.U. Serie Generale n. {gu_numero} del {_dt.date.fromisoformat(gu_data).strftime('%d/%m/%Y')}" if gu_numero else f"G.U. del {gu_data}"),
            "codice_redazionale": codice, "url": url, "fonte": "testo del decreto sulla G.U.", "verificato_il": oggi.isoformat(), "da_verificare": False}
    serie[:] = [v for v in serie if v.get("dal") != p["dal"]] + [voce]
    serie.sort(key=lambda v: str(v.get("dal")))
    meta = serie_obj.setdefault("_meta", {})
    meta["verificato_il"] = oggi.isoformat()
    _salva(tab, path)
    return {"esito": "AGGIORNATA", "voce": voce, "file": str(path or TABELLA)}


_MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
         "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}


def parse_comunicato_mora(testo: str) -> dict:
    """Dal comunicato MEF: {dal, al, riferimento} oppure {}.
    Forme lette (G.U. 2013-2026): «per il periodo 1° luglio - 31 dicembre 2026 il tasso di riferimento e' pari al 2,40 per cento»;
    prima del 2013: «... il saggio d'interesse ... e' pari al X per cento» per il semestre indicato."""
    t = " ".join(testo.split())
    m = re.search(r"(?:periodo|semestre)\s+(?:dal\s+)?1\s*[°º]?\s*(gennaio|luglio)\s*(\d{4})?\s*[-–al ]+\s*(30 giugno|31 dicembre)\s*(\d{4}).{0,200}?"
                  r"pari\s+(?:al|all'|allo|a)\s*(\d+(?:,\d+)?)\s*(?:per cento|%)", t, re.I)
    if not m:
        return {}
    anno = int(m.group(4))
    dal = f"{anno}-01-01" if m.group(1).lower() == "gennaio" else f"{anno}-07-01"
    al = f"{anno}-06-30" if dal.endswith("01-01") else f"{anno}-12-31"
    return {"dal": dal, "al": al, "riferimento": float(m.group(5).replace(",", "."))}


def bce_al(data_iso: str, tab: dict) -> float:
    r = cerca("bce", data_iso, tab=tab)
    return r.get("valore") if r.get("esito") == "OK" else None


def aggiorna_mora(gu_data: str, codice: str, tab: dict = None, path: Path = None, scarica=None, oggi: _dt.date = None) -> dict:
    """Legge il comunicato MEF del semestre sulla G.U. e scrive la voce (con il riscontro sulla serie BCE)."""
    tab = tab if tab is not None else carica(path)
    oggi = oggi or _dt.date.today()
    url = GU_ARTICOLO.format(data=gu_data, codice=codice, tipo="COMUNICATO")
    if scarica is None:
        scarica, err = _scaricatore(url)
        if err:
            return err
    try:
        testo = _testo_html(scarica(url))
    except Exception as e:
        return _errore_rete(e, url)
    p = parse_comunicato_mora(testo)
    if not p:
        return {"esito": "PARSER_FALLITO", "motivo": "nel testo non trovo «per il periodo … il tasso di riferimento e' pari al X per cento»", "url": url}
    serie_obj = tab.setdefault("mora_commerciale", {"_meta": {}, "serie": []})
    magg = serie_obj.get("maggiorazione_punti", 8) if p["dal"] >= DATA_REGIME_192_2012 else serie_obj.get("maggiorazione_punti_ante_2013", 7)
    m = re.search(r"Serie Generale n\.\s*(\d+)\s+del\s+(\d{1,2}-\d{1,2}-\d{4})", testo)
    bce = bce_al(p["dal"], tab)
    voce = {"dal": p["dal"], "al": p["al"], "riferimento_bce": p["riferimento"], "maggiorazione": magg, "valore": round(p["riferimento"] + magg, 4),
            "atto": "comunicato MEF", "gu": f"G.U. Serie Generale n. {m.group(1)} del {m.group(2).replace('-', '/')}" if m else f"G.U. del {gu_data}",
            "codice_redazionale": codice, "url": url, "fonte": "comunicato MEF sulla G.U.", "bce_primo_giorno": bce,
            "verificato_il": oggi.isoformat(), "da_verificare": False}
    serie = serie_obj.setdefault("serie", [])
    serie[:] = sorted([v for v in serie if v.get("dal") != p["dal"]] + [voce], key=lambda v: v["dal"])
    _salva(tab, path)
    out = {"esito": "AGGIORNATA", "voce": voce, "file": str(path or TABELLA)}
    if bce is not None and abs(bce - p["riferimento"]) > 1e-9 and p["dal"] >= "2008-10-15":
        out["avviso"] = f"il comunicato ({p['riferimento']}) differisce dal tasso BCE in tabella al {p['dal']} ({bce}): verificare"
    return out


def _leggi_csv_bce(testo: str) -> list:
    import csv
    import io
    return [(r["TIME_PERIOD"], float(r["OBS_VALUE"])) for r in csv.DictReader(io.StringIO(testo)) if r.get("OBS_VALUE") not in (None, "")]


def costruisci_bce(csv_fisso: str, csv_minimo: str, oggi: _dt.date = None) -> list:
    """La serie `bce` dai due CSV del BCE Data Portal: tasso fisso (MRR_FR) fino al 27/06/2000 e dal 15/10/2008,
    tasso minimo di offerta (MRR_MBR) nelle aste a tasso variabile (28/06/2000-14/10/2008). Solo i cambi."""
    oggi = oggi or _dt.date.today()
    fisso, minimo = _leggi_csv_bce(csv_fisso), _leggi_csv_bce(csv_minimo)
    grezze = ([(d, v, "MRR_FR", "tasso fisso") for d, v in fisso if d < "2000-06-28" or d >= "2008-10-15"]
              + [(d, v, "MRR_MBR", "tasso minimo di offerta (aste a tasso variabile)") for d, v in minimo if "2000-06-28" <= d < "2008-10-15"])
    out, prec = [], None
    for d, v, cod, tipo in sorted(grezze):
        if prec is not None and abs(prec[0] - v) < 1e-12 and prec[1] == cod:
            continue            # la BCE registra anche le date in cui cambiano solo gli altri tassi ufficiali
        out.append({"dal": d, "valore": v, "tipo_tasso": tipo, "fonte": f"BCE Data Portal FM.B.U2.EUR.4F.KR.{cod}.LEV",
                    "verificato_il": oggi.isoformat(), "da_verificare": False})
        prec = (v, cod)
    return out


def aggiorna_bce(tab: dict = None, path: Path = None, scarica=None, oggi: _dt.date = None) -> dict:
    tab = tab if tab is not None else carica(path)
    oggi = oggi or _dt.date.today()
    url = ECB_CSV.format(serie="MRR_FR")
    if scarica is None:
        scarica, err = _scaricatore(url)
        if err:
            return err
    try:
        fisso = scarica(url)
        minimo = scarica(ECB_CSV.format(serie="MRR_MBR"))
    except Exception as e:
        return _errore_rete(e, url)
    serie = costruisci_bce(fisso, minimo, oggi)
    if not serie:
        return {"esito": "PARSER_FALLITO", "motivo": "CSV BCE senza osservazioni", "url": url}
    s = tab.setdefault("bce", {"_meta": {}, "serie": []})
    s["serie"] = serie
    s.setdefault("_meta", {})["verificato_il"] = oggi.isoformat()
    _salva(tab, path)
    return {"esito": "AGGIORNATA", "voci": len(serie), "ultima": serie[-1], "file": str(path or TABELLA)}


def aggiungi_foi(mese: str, indice: float, url: str, tab: dict = None, path: Path = None, oggi: _dt.date = None) -> dict:
    """Aggiunge l'indice FOI di `mese` letto dall'avvocato/agente sulla pagina ISTAT (base corrente)."""
    tab = tab if tab is not None else carica(path)
    oggi = oggi or _dt.date.today()
    if not re.fullmatch(r"\d{4}-\d{2}", mese or ""):
        return {"esito": "ERRORE", "motivo": "--mese AAAA-MM"}
    s = tab.setdefault("istat_foi", {"_meta": {}, "serie": []})
    basi = s.get("basi") or []
    base = basi[-1]["base"] if basi else None
    if basi and mese < basi[-1]["dal_mese"]:
        return {"esito": "ERRORE", "motivo": f"{mese} precede la base corrente {base}: gli indici storici si correggono solo dalla tavola ISTAT"}
    voce = {"mese": mese, "dal": mese + "-01", "valore": float(indice), "base": base, "fonte": url, "verificato_il": oggi.isoformat()}
    serie = s.setdefault("serie", [])
    serie[:] = sorted([v for v in serie if v.get("mese") != mese] + [voce], key=lambda v: v["mese"])
    _salva(tab, path)
    return {"esito": "AGGIORNATA", "voce": voce}


def aggiorna_da_file(tipo: str, file_testo: str, tab: dict = None, path: Path = None, oggi: _dt.date = None) -> dict:
    """Legge un comunicato caricato dall'avvocato (testo) per bot12. Parser prudente:
    scrive solo se riconosce data e valore; altrimenti PARSER_FALLITO con cio' che ha visto."""
    tab = tab if tab is not None else carica(path)
    oggi = oggi or _dt.date.today()
    testo = " ".join(Path(file_testo).read_text(encoding="utf-8", errors="replace").split())
    if tipo == "bot12":
        d = re.search(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4})", testo)
        r = re.search(r"rendimento\s+medio\s+ponderato[^0-9]{0,40}?(-?\d+[,.]\d+)", testo, re.I)
        if not (d and r):
            return {"esito": "PARSER_FALLITO", "motivo": "nel file non trovo data dell'asta e «rendimento medio ponderato X,XXX»"}
        voce = {"asta": f"{d.group(3)}-{int(d.group(2)):02d}-{int(d.group(1)):02d}", "rendimento_medio_ponderato": float(r.group(1).replace(",", ".")),
                "da_verificare": False, "fonte": f"comunicato MEF caricato dall'avvocato ({Path(file_testo).name})", "verificato_il": oggi.isoformat()}
        serie = tab.setdefault("bot12", {"_meta": {}, "serie": []}).setdefault("serie", [])
        serie[:] = sorted([v for v in serie if v.get("asta") != voce["asta"]] + [voce], key=lambda v: v["asta"])
        _salva(tab, path)
        return {"esito": "AGGIORNATA", "voce": voce}
    return {"esito": "NON_SUPPORTATO", "motivo": f"--da-file per «{tipo}» non implementato: legale e mora dalla G.U. (--gu-data/--codice), bce dal BCE Data Portal, istat_foi con --mese/--indice"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tassi e indici di riferimento alla data (legale, mora commerciale, BOT 12m, BCE, ISTAT FOI) da tabella locale.")
    ap.add_argument("--tipo", choices=TIPI)
    ap.add_argument("--data", help="AAAA-MM-GG")
    ap.add_argument("--data-transazione", help="mora_commerciale: data di conclusione del contratto (prima del 1/1/2013: + 7 punti)")
    ap.add_argument("--serie", action="store_true", help="stampa la serie del tipo con lo stato di ogni voce")
    ap.add_argument("--coefficiente", nargs=2, metavar=("DA_MESE", "A_MESE"), help="istat_foi: coefficiente di rivalutazione (metodo ISTAT)")
    ap.add_argument("--finestra-117", action="store_true", help="bot12: minimo e massimo dei BOT annuali emessi nei 12 mesi precedenti --data")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--gu-data", help="con --aggiorna (legale, mora_commerciale): data di pubblicazione in G.U.")
    ap.add_argument("--codice", help="con --aggiorna (legale, mora_commerciale): codice redazionale (es. 25A06705)")
    ap.add_argument("--da-file", help="con --aggiorna --tipo bot12: comunicato/testo caricato dall'avvocato")
    ap.add_argument("--mese", help="con --aggiorna --tipo istat_foi: AAAA-MM"); ap.add_argument("--indice", help="con --aggiorna --tipo istat_foi")
    ap.add_argument("--url", help="con --aggiorna --tipo istat_foi: pagina ISTAT da cui e' letto l'indice")
    ap.add_argument("--tabella", help="file tabella alternativo (test)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.aggiorna:
        if not a.tipo:
            ap.error("--aggiorna richiede --tipo")
        if a.da_file:
            r = aggiorna_da_file(a.tipo, a.da_file, path=a.tabella)
        elif a.tipo == "legale" and a.gu_data and a.codice:
            r = aggiorna_legale(a.gu_data, a.codice, path=a.tabella)
        elif a.tipo == "mora_commerciale" and a.gu_data and a.codice:
            r = aggiorna_mora(a.gu_data, a.codice, path=a.tabella)
        elif a.tipo == "bce":
            r = aggiorna_bce(path=a.tabella)
        elif a.tipo == "istat_foi" and a.mese and a.indice and a.url:
            r = aggiungi_foi(a.mese, float(a.indice.replace(",", ".")), a.url, path=a.tabella)
        else:
            meta = (carica(a.tabella).get(a.tipo) or {}).get("_meta") or {}
            r = {"esito": "ISTRUZIONI", "motivo": f"per «{a.tipo}»: " + {
                "legale": "--gu-data e --codice del decreto (sommario G.U. di dicembre)",
                "mora_commerciale": "--gu-data e --codice del comunicato MEF (G.U. di gennaio/luglio)",
                "istat_foi": f"--mese AAAA-MM --indice X --url <pagina ISTAT> ({meta.get('url')})"}.get(a.tipo, f"--da-file con il documento caricato; fonte: {meta.get('url')}")}
        print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else f"{r['esito']}: {r.get('motivo') or r.get('voce') or r.get('ultima')}")
        return 0 if r["esito"] == "AGGIORNATA" else 1
    tab = carica(a.tabella)
    if a.serie:
        if not a.tipo:
            ap.error("--serie richiede --tipo")
        s = tab.get(a.tipo) or {}
        print(f"{a.tipo}: {(s.get('_meta') or {}).get('nome')} — verificata il {(s.get('_meta') or {}).get('verificato_il') or 'mai'}")
        for v in s.get("serie") or []:
            chiave = v.get("mese") or v.get("dal") or v.get("asta")
            val = v.get("valore", v.get("rendimento_medio_ponderato", v.get("rendimento_minimo", v.get("riferimento_bce"))))
            txt = (str(val).replace(".", ",") if a.tipo == "istat_foi" else _pct(val)) if val is not None else "n/d"
            print(f"  {chiave}  {txt:>8}  {'DA_VERIFICARE' if v.get('da_verificare') or val is None else 'ok'}  "
                  f"{v.get('decreto') or v.get('atto') or v.get('base') or v.get('descrizione') or ''}")
        return 0
    if a.coefficiente:
        r = coefficiente_foi(a.coefficiente[0], a.coefficiente[1], tab=tab)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        elif r["esito"] == "OK":
            print(f"OK coefficiente FOI {r['da_mese']} → {r['a_mese']}: {str(r['coefficiente']).replace('.', ',')} (variazione {str(r['variazione_pct']).replace('.', ',')}%)")
            print(f"  indici: {r['indice_da']} (base {r['base_da']}) → {r['indice_a']} (base {r['base_a']}); raccordi: "
                  + (", ".join(f"{x['coefficiente']} ({x['base']})" for x in r["raccordi"]) or "nessuno") + (f"; Cst {r['cst']}" if r["cst"] else ""))
            print(f"  formula: {r['formula']}\n  fonte: {r['fonte']}")
        else:
            print(f"{r['esito']}: {r['motivo']}")
        return 0 if r["esito"] == "OK" else 1
    if not (a.tipo and a.data):
        ap.print_help(); return 2
    if a.tipo == "bot12" and a.finestra_117:
        r = finestra_117(a.data, tab=tab)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        elif r["esito"] == "OK":
            print(f"OK BOT annuali emessi dal {r['dal']} al {r['al_escluso']} (escluso): {r['emissioni']} aste — minimo {_pct(r['minimo'])} "
                  f"(asta {r['asta_minimo']}), massimo {_pct(r['massimo'])} (asta {r['asta_massimo']})\n  {r['norma']}\n  fonte: {r['fonte']}")
        else:
            print(f"{r['esito']}: {r['motivo']}")
        return 0 if r["esito"] == "OK" else 1
    r = cerca(a.tipo, a.data, tab=tab, data_transazione=a.data_transazione)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        stampa(r)
    return 0 if r["esito"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
