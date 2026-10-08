#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA DEI DATI PERIODICI (v0.36, area «dati» dell'Action sentinelle): tassi, soglie d'usura, tabelle datate.

I numeri li estraggono SOLO gli script, da documenti ufficiali scaricati nel giro:
  * BCE: BCE Data Portal (`tassi.aggiorna_bce`);
  * tasso legale e mora commerciale: decreto o comunicato trovato nei sommari della G.U. (`tassi.aggiorna_legale`,
    `tassi.aggiorna_mora`);
  * soglie d'usura: Allegato A del decreto MEF (PDF del Dipartimento del Tesoro, `soglia_usura.parse_decreto`), con
    due controlli: la soglia pubblicata coincide con quella ricalcolata dal TEGM per ogni categoria, e il trimestre e'
    quello atteso; gli estremi della G.U. si cercano nei sommari;
  * FOI ISTAT e BOT a 12 mesi: Claude trova la pagina ufficiale, ma il valore entra solo se lo script lo ritrova su
    quella pagina (`sentinelle_prove`) ed e' plausibile rispetto alla serie;
  * tabelle datate (contributo unificato, G.d.P., D.M. 110): la verifica si rinnova solo se gli articoli da cui
    dipendono sono verificati questa settimana nel corpus, non in movimento e senza modifiche dopo l'ultima verifica
    della tabella; per il contributo unificato ogni importo deve anche comparire nel testo vigente dell'art. 13.
Ciò che non passa resta com'era, con una riga nella issue.

Solo stdlib (pdftotext per il PDF del MEF), Python 3.9.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinelle_base as sb  # noqa: E402
import sentinelle_prove as sp  # noqa: E402

REL_TASSI = "dati/tassi.json"
REL_SOGLIE = "dati/tassi-soglia.json"
GU = "https://www.gazzettaufficiale.it"
MEF_BASE = "https://www.dt.mef.gov.it"
#: tabella → articoli del corpus da cui dipende (None: non verificabile in automatico)
TABELLE = {
    "wiki-studio/parcella/contributo-unificato.json": (("dpr-115-2002", ("13", "30")),),
    "wiki-studio/normativa/competenza-materia-gdp.json": (("cpc", ("7",)),),
    "wiki-studio/normativa/limiti-dm-110-2023.json": (("dm-110-2023", ("1", "2", "3", "4", "5", "6")),),
    "wiki-studio/normativa/pct-specifiche.json": None,     # specifiche DGSIA fuori dal corpus
}
#: anticipo con cui una tabella in scadenza si riverifica, e l'intervallo di default della prossima verifica
ANTICIPO_GIORNI = 7
INTERVALLO_GIORNI = 90
#: il corpus deve essere stato verificato da non piu' di tanti giorni perche' «invariato» valga
CORPUS_FRESCO_GIORNI = 8
_MESI_IT = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
            "novembre", "dicembre")
_TRIMESTRI = {1: "gennaio-marzo", 4: "aprile-giugno", 7: "luglio-settembre", 10: "ottobre-dicembre"}
AMMESSI_DOPO_CLAUDE = ()        # nell'area dati Claude non scrive nel repo: consegna solo esiti


# ----------------------------------------------------------------------------------------------- Gazzetta Ufficiale

class Gazzetta:
    """I sommari della Serie Generale degli ultimi 30 giorni, letti una volta per giro (atti con codice A e G)."""

    def __init__(self, get=None):
        self._get = get
        self._atti = None

    def get(self, url: str) -> str:
        if self._get:
            return self._get(url)
        import corpus_pubblica as cp
        return cp._get_testo(url)

    def atti(self) -> list:
        if self._atti is not None:
            return self._atti
        import corpus_pubblica as cp
        out = []
        for d, n in cp.numeri_gu(self.get(f"{GU}/30giorni/serie_generale")):
            try:
                html = self.get(f"{GU}/gazzetta/serie_generale/caricaDettaglio?dataPubblicazioneGazzetta={d}&numeroGazzetta={n}")
            except Exception:  # noqa: BLE001
                continue
            out += [dict(a, numero=n) for a in atti_sommario(html)]
        self._atti = out
        return out

    def cerca(self, rx: str) -> list:
        r = re.compile(rx, re.I)
        return [a for a in self.atti() if r.search(a.get("titolo") or "")]


def atti_sommario(html_sommario: str) -> list:
    """[{codice, data, titolo}] di tutti gli atti di un numero della G.U. (codici redazionali G e A)."""
    import corpus_pubblica as cp
    voci, ordine = {}, []
    rx = (r'<a\b[^>]*href="[^"]*caricaDettaglioAtto/originario\?atto\.dataPubblicazioneGazzetta=(\d{4}-\d{2}-\d{2})'
          r'&(?:amp;)?atto\.codiceRedazionale=(\w+)[^"]*"[^>]*>(.*?)</a>')
    for data, cod, anchor in re.findall(rx, html_sommario or "", re.S):
        if not re.fullmatch(r"\d{2}[AG]\d{5}", cod):
            continue
        testo = cp._testo_html(anchor)
        if cod not in voci:
            voci[cod] = {"codice": cod, "data": data, "titolo": testo}
            ordine.append(cod)
        elif testo and len(voci[cod]["titolo"]) < 300:
            voci[cod]["titolo"] = (voci[cod]["titolo"] + " — " + testo).strip(" —")
    return [voci[c] for c in ordine]


# ----------------------------------------------------------------------------------------------- tassi

def _plausibile(valori, minimo: float, massimo: float) -> bool:
    return all(isinstance(v, (int, float)) and minimo <= v <= massimo for v in valori)


def _bce(radice: Path, giro: sb.Giro, oggi: _dt.date, scarica=None) -> None:
    import tassi
    path = Path(radice) / REL_TASSI
    tab = tassi.carica(path)
    meta = (tab.get("bce") or {}).get("_meta") or {}
    if str(meta.get("verificato_il") or "") > (oggi - _dt.timedelta(days=6)).isoformat():
        giro.riga("BCE: verificato in settimana")
        return
    r = tassi.aggiorna_bce(path=path, scarica=scarica, oggi=oggi)
    if r.get("esito") != "AGGIORNATA":
        giro.problema(f"tasso BCE non aggiornato: {r.get('esito')} {r.get('motivo') or ''}".strip())
        sb.git(radice, "checkout", "--", REL_TASSI)
        return
    serie = (tassi.carica(path).get("bce") or {}).get("serie") or []
    if not serie or not _plausibile([v.get("valore") for v in serie[-6:]], -1.0, 20.0):
        sb.git(radice, "checkout", "--", REL_TASSI)
        giro.problema("tasso BCE scartato: valori fuori dai limiti di plausibilita'")
        return
    giro.riga(f"BCE: serie aggiornata, ultimo {serie[-1].get('dal')} {serie[-1].get('valore')}%")


def _legale(radice: Path, giro: sb.Giro, oggi: _dt.date, gu: Gazzetta, scarica=None) -> None:
    import tassi
    path = Path(radice) / REL_TASSI
    serie = (tassi.carica(path).get("legale") or {}).get("serie") or []
    anno = oggi.year + 1 if oggi.month == 12 else oggi.year if oggi.month == 1 else None
    if anno is None or any(str(v.get("dal")) == f"{anno}-01-01" for v in serie):
        return
    trovati = gu.cerca(r"saggio\s+degli\s+interessi\s+legali|tasso\s+di\s+interesse\s+legale|interessi\s+legali")
    if not trovati:
        giro.riga(f"tasso legale {anno}: decreto non ancora nei sommari della G.U.")
        return
    a = trovati[-1]
    r = tassi.aggiorna_legale(a["data"], a["codice"], path=path, scarica=scarica, oggi=oggi, gu_numero=a.get("numero"))
    voce = r.get("voce") or {}
    if r.get("esito") != "AGGIORNATA" or str(voce.get("dal")) != f"{anno}-01-01" or not _plausibile([voce.get("valore")], 0.0, 15.0):
        sb.git(radice, "checkout", "--", REL_TASSI)
        giro.problema(f"tasso legale {anno}: decreto {a['codice']} trovato ma non letto ({r.get('esito')}): da inserire a mano",
                      "dati:legale")
        return
    giro.riga(f"tasso legale {anno}: {voce['valore']}% ({voce.get('decreto')}, {voce.get('gu')})")


def _mora(radice: Path, giro: sb.Giro, oggi: _dt.date, gu: Gazzetta, scarica=None) -> None:
    import tassi
    path = Path(radice) / REL_TASSI
    serie = (tassi.carica(path).get("mora_commerciale") or {}).get("serie") or []
    inizio = f"{oggi.year}-01-01" if oggi.month in (1, 2) else f"{oggi.year}-07-01" if oggi.month in (7, 8) else None
    if inizio is None or any(str(v.get("dal")) == inizio for v in serie):
        return
    trovati = gu.cerca(r"ritardo\s+nei\s+pagamenti|transazioni\s+commerciali")
    if not trovati:
        giro.riga(f"mora commerciale dal {inizio}: comunicato non ancora nei sommari della G.U.")
        return
    a = trovati[-1]
    r = tassi.aggiorna_mora(a["data"], a["codice"], path=path, scarica=scarica, oggi=oggi)
    voce = r.get("voce") or {}
    if r.get("esito") != "AGGIORNATA" or str(voce.get("dal")) != inizio or not _plausibile([voce.get("valore")], 0.0, 30.0):
        sb.git(radice, "checkout", "--", REL_TASSI)
        giro.problema(f"mora commerciale dal {inizio}: comunicato {a['codice']} trovato ma non letto ({r.get('esito')})",
                      "dati:mora")
        return
    giro.riga(f"mora commerciale dal {inizio}: {voce['valore']}%")


# ----------------------------------------------------------------------------------------------- soglie d'usura

def trimestre_atteso(fine_ultimo: str) -> tuple:
    """(inizio, fine) del trimestre successivo a quello che finisce il giorno `fine_ultimo`."""
    f = _dt.date.fromisoformat(str(fine_ultimo)[:10])
    ini = f + _dt.timedelta(days=1)
    mese_fine = ini.month + 2
    fine = (_dt.date(ini.year + (mese_fine > 12), (mese_fine - 1) % 12 + 1, 1) + _dt.timedelta(days=32)).replace(day=1) \
        - _dt.timedelta(days=1)
    return ini.isoformat(), fine.isoformat()


def link_decreto_mef(html: str, inizio: str) -> str:
    """L'indirizzo del PDF del decreto del trimestre che comincia il giorno `inizio`, dalla pagina del MEF."""
    d = _dt.date.fromisoformat(inizio)
    periodo, anno = _TRIMESTRI.get(d.month, ""), str(d.year)
    for href in re.findall(r'href="([^"]+\.pdf)"', html or "", re.I):
        h = href.lower()
        if "decreto" in h and periodo.split("-")[0] in h and anno in h:
            return href if href.startswith("http") else MEF_BASE + href
    return ""


def estremi_gu(gu: Gazzetta, inizio: str, testo: str = None, giro: sb.Giro = None) -> tuple:
    """(decreto, gu, codice) del decreto di RILEVAZIONE del trimestre `inizio` nei sommari della G.U., o tre None.

    Nella G.U. di fine settembre esce anche il decreto annuale di classificazione delle operazioni, con le stesse
    parole: si scarta. Se c'e' il testo del PDF del Tesoro («emesso alla data del protocollo»), la data del protocollo
    deve essere quella del decreto in G.U."""
    d0 = _dt.date.fromisoformat(inizio)
    candidati = [a for a in gu.cerca(r"rilevazione\s+dei\s+tassi(\s+di\s+interesse)?\s+effettiv[io]\s+global[ei]\s+med[io]")
                 if a["data"] >= (d0 - _dt.timedelta(days=45)).isoformat()
                 and not re.search(r"\bclassificazione\b", a.get("titolo") or "", re.I)]
    applicazione = re.compile(rf"applicazione\s+dal\s+{d0.day}\D{{0,2}}\s*{_MESI_IT[d0.month - 1]}\b", re.I)
    atto = next((a for a in reversed(candidati) if applicazione.search(a.get("titolo") or "")), None) or (
        candidati[0] if len(candidati) == 1 else None)
    m = re.search(r"DECRETO\s+(\d{1,2}\s+\w+\s+\d{4})", (atto or {}).get("titolo") or "", re.I)
    if not (atto and m):
        return None, None, None
    decreto = f"D.M. MEF {m.group(1).lower()}"
    gu_txt = f"G.U. Serie Generale n. {atto.get('numero')} del {_dt.date.fromisoformat(atto['data']).strftime('%d/%m/%Y')}"
    prot = re.search(r"Prot\.?\s*Num\.?\s*:?\s*[\d/]+\s+del\s+(\d{1,2})/(\d{1,2})/(\d{4})", testo or "", re.I)
    if prot:
        data_prot = f"{int(prot.group(1))} {_MESI_IT[int(prot.group(2)) - 1]} {prot.group(3)}"
        if data_prot != m.group(1).lower():
            if giro:
                giro.problema(f"soglie d'usura {inizio}: il decreto in G.U. ({m.group(1)}, {atto['codice']}) non ha la data "
                              f"del protocollo del PDF ({data_prot}): estremi non scritti", "dati:usura")
            return None, None, None
    return decreto, gu_txt, atto["codice"]


def _completa_estremi(path: Path, giro: sb.Giro, oggi: _dt.date, gu: Gazzetta) -> None:
    """L'ultimo trimestre preso dal decreto senza gli estremi della G.U.: si cercano di nuovo nei sommari."""
    tab = json.loads(path.read_text(encoding="utf-8"))
    ultimo = (tab.get("trimestri") or [{}])[-1]
    dec = ultimo.get("decreto") or {}
    if ultimo.get("origine") != "decreto MEF" or not dec.get("da_verificare"):
        return
    decreto, gu_txt, codice = estremi_gu(gu, ultimo["inizio"])
    if not decreto:
        if oggi > _dt.date.fromisoformat(ultimo["inizio"]) + _dt.timedelta(days=30):
            giro.problema(f"soglie d'usura {ultimo['inizio']}: estremi del decreto ancora da verificare (non trovati nei "
                          "sommari della G.U.)", "dati:usura")
        return
    dec.update(decreto=decreto, gu=gu_txt, codice_redazionale=codice, verificato_il=oggi.isoformat(), da_verificare=False)
    path.write_text(json.dumps(tab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    giro.riga(f"soglie d'usura {ultimo['inizio']}: estremi del decreto completati ({decreto}, {gu_txt})")


def _usura(radice: Path, giro: sb.Giro, oggi: _dt.date, gu: Gazzetta, get_html=None, get_pdf=None) -> None:
    import soglia_usura as su
    path = Path(radice) / REL_SOGLIE
    tab = su.carica(path)
    trimestri = tab.get("trimestri") or []
    if not trimestri:
        return
    _completa_estremi(path, giro, oggi, gu)
    inizio, fine = trimestre_atteso(trimestri[-1]["fine"])
    if oggi < _dt.date.fromisoformat(inizio) - _dt.timedelta(days=15):
        giro.riga(f"soglie d'usura: coperte fino al {trimestri[-1]['fine']}")
        return
    try:
        html = (get_html or Gazzetta().get)(su.URL_DECRETI_MEF)
    except Exception as e:  # noqa: BLE001
        giro.problema(f"soglie d'usura {inizio}: pagina del MEF non raggiungibile ({e.__class__.__name__})")
        return
    url = link_decreto_mef(html, inizio)
    if not url:
        giro.riga(f"soglie d'usura {inizio}: decreto non ancora sulla pagina del MEF")
        if oggi > _dt.date.fromisoformat(inizio) + _dt.timedelta(days=10):
            giro.problema(f"soglie d'usura del trimestre {inizio} → {fine}: nessun decreto sulla pagina del MEF", "dati:usura")
        return
    try:
        testo = get_pdf(url) if get_pdf else sp.scarica(url)[0]
    except Exception as e:  # noqa: BLE001
        giro.problema(f"soglie d'usura {inizio}: PDF non leggibile ({e.__class__.__name__}: {str(e)[:100]})", "dati:usura")
        return
    p = su.parse_decreto(testo)
    voci = p.get("voci") or []
    errori = []
    if p.get("esito") != "OK":
        errori.append(f"decreto non letto ({p.get('motivo') or p.get('esito')})")
    elif p.get("inizio") != inizio or p.get("fine") != fine:
        errori.append(f"il PDF e' del trimestre {p.get('inizio')} → {p.get('fine')}, atteso {inizio} → {fine}")
    elif len(voci) < 20:
        errori.append(f"solo {len(voci)} categorie lette")
    else:
        diverse = [f"{v.get('categoria')} {v.get('classe') or ''}".strip() for v in voci
                   if v.get("soglia_pubblicata") is not None and v.get("soglia_calcolata") is not None
                   and abs(float(v["soglia_pubblicata"]) - float(v["soglia_calcolata"])) > 0.005]
        if diverse:
            errori.append("soglia pubblicata diversa da quella ricalcolata dal TEGM per: " + "; ".join(diverse[:4]))
        if not _plausibile([v.get("tegm") for v in voci], 0.0, 40.0):
            errori.append("TEGM fuori dai limiti di plausibilita'")
    if errori:
        giro.problema(f"soglie d'usura {inizio}: " + "; ".join(errori), "dati:usura")
        return
    # gli estremi della G.U. (seconda fonte)
    decreto, gu_txt, codice = estremi_gu(gu, inizio, testo, giro)
    r = su.aggiungi_decreto(testo, decreto=decreto, gu=gu_txt, codice=codice, url=url, dest=path, oggi=oggi)
    if r.get("esito") != "AGGIUNTO":
        sb.git(radice, "checkout", "--", REL_SOGLIE)
        giro.problema(f"soglie d'usura {inizio}: non aggiunte ({r.get('esito')})", "dati:usura")
        return
    giro.riga(f"soglie d'usura {inizio} → {fine}: {len(voci)} categorie dal decreto MEF"
              + (f" ({decreto}, {gu_txt})" if decreto else " (estremi della G.U. non ancora trovati: si cercano di nuovo ai prossimi giri)"))


# ----------------------------------------------------------------------------------------------- tabelle datate

def _euro(v: float) -> str:
    intero = f"{int(round(v)):,}".replace(",", ".")
    return intero if abs(v - round(v)) < 0.005 else f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def importi_cu(tab: dict) -> list:
    return [float(s["cu"]) for s in (tab.get("scaglioni") or []) if isinstance(s.get("cu"), (int, float))]


def controlla_importi(importi: list, testo: str) -> list:
    """Gli importi che NON compaiono come «euro N» nel testo dell'articolo."""
    t = re.sub(r"\s+", " ", testo or "")
    return [x for x in importi if not re.search(r"euro\s+" + re.escape(_euro(x)) + r"(?![\d.,])", t, re.I)]


def _tabelle(radice: Path, giro: sb.Giro, oggi: _dt.date, articolo=None) -> None:
    manifest = sb.manifest_corpus(radice)
    righe = sb.changelog_auto(radice)
    for rel, dipende in TABELLE.items():
        p = Path(radice) / rel
        tab = sb.leggi_json(p)
        if not isinstance(tab, dict):
            continue
        meta = tab.setdefault("_meta", {})
        prossima = str(meta.get("prossima_verifica") or "")
        if prossima and prossima > (oggi + _dt.timedelta(days=ANTICIPO_GIORNI)).isoformat():
            continue
        nome = Path(rel).name
        if dipende is None:
            giro.riga(f"{nome}: non rinnovabile in automatico (fonte fuori dal corpus); prossima verifica {prossima or 'n.d.'}")
            continue
        motivi = []
        verificata = str(meta.get("verificato_il") or "")[:10]
        for slug, arts in dipende:
            st = sb.stato_atto(manifest, slug)
            if not st:
                motivi.append(f"{slug} non e' nel corpus")
                continue
            if str(st.get("verificato_il") or "") < (oggi - _dt.timedelta(days=CORPUS_FRESCO_GIORNI)).isoformat():
                motivi.append(f"{slug} non verificato di recente nel corpus ({st.get('verificato_il')})")
            if st.get("in_movimento"):
                motivi.append(f"{slug} in movimento in G.U.")
            cambi = sb.cambi_dopo(righe, slug, verificata, arts)
            if cambi:
                motivi.append(f"{slug} art. {', '.join(sorted({str(c.get('articolo')) for c in cambi}))} modificato dopo il {verificata}")
        if not motivi and rel.endswith("contributo-unificato.json"):
            a = (articolo or _articolo)("13", "dpr-115-2002")
            mancanti = controlla_importi(importi_cu(tab), a.get("testo") or "")
            if not a.get("testo"):
                motivi.append("testo dell'art. 13 d.P.R. 115/2002 non disponibile nel corpus")
            elif mancanti:
                motivi.append("importi non trovati nell'art. 13: " + ", ".join(_euro(x) for x in mancanti))
        if motivi:
            meta["da_ricontrollare"] = {"motivo": "; ".join(motivi)[:500], "dal": oggi.isoformat(), "fonte": "sentinelle"}
            sb.scrivi_json(p, tab)
            giro.problema(f"{nome}: verifica non rinnovata — " + "; ".join(motivi), f"dati:{nome}")
            continue
        try:
            passo = (_dt.date.fromisoformat(prossima) - _dt.date.fromisoformat(verificata)).days if prossima and verificata else INTERVALLO_GIORNI
        except ValueError:
            passo = INTERVALLO_GIORNI
        meta["verificato_il"] = oggi.isoformat()
        meta["prossima_verifica"] = (oggi + _dt.timedelta(days=max(30, min(passo, 365)))).isoformat()
        meta.pop("da_ricontrollare", None)
        meta["rinnovata_da"] = ("sentinelle (Action del corpus): articoli di riferimento verificati nel corpus questa settimana, "
                                "non in movimento, senza modifiche dopo la verifica precedente")
        sb.scrivi_json(p, tab)
        giro.riga(f"{nome}: verifica rinnovata (prossima {meta['prossima_verifica']})")


def _articolo(token: str, slug: str) -> dict:
    import codice_locale as cl
    return cl.articolo(token, slug)


# ----------------------------------------------------------------------------------------------- FOI e BOT (con Claude)

def triage_claude(radice: Path, oggi: _dt.date) -> dict:
    """Le serie per cui serve una pagina ufficiale che lo script non sa trovare da solo."""
    import tassi
    tab = tassi.carica(Path(radice) / REL_TASSI)
    out = {}
    ultimo_foi = tassi.ultimo_mese_foi(tab)
    atteso = (oggi.replace(day=1) - _dt.timedelta(days=1)).strftime("%Y-%m") if oggi.day >= 18 else \
        ((oggi.replace(day=1) - _dt.timedelta(days=1)).replace(day=1) - _dt.timedelta(days=1)).strftime("%Y-%m")
    if ultimo_foi and ultimo_foi < atteso:
        out["foi"] = {"dopo": ultimo_foi, "fino_a": atteso,
                      "cosa": "indice FOI senza tabacchi dei mesi mancanti, base corrente (sito ISTAT)"}
    bot = ((tab.get("bot12") or {}).get("serie") or [])
    ultima = str(bot[-1].get("asta")) if bot else ""
    if ultima and ultima < (oggi - _dt.timedelta(days=35)).isoformat():
        out["bot12"] = {"dopo": ultima, "cosa": "rendimento medio ponderato delle aste dei BOT a 12 mesi successive (Banca d'Italia o MEF)"}
    return out


def _numero_it(x: float, decimali: int) -> str:
    return f"{x:.{decimali}f}".replace(".", ",")


def dopo_claude(radice: Path, triage: dict, esiti: dict, giro: sb.Giro, oggi: _dt.date, get=None) -> None:
    import tassi
    path = Path(radice) / REL_TASSI
    tab = tassi.carica(path)
    for e in ((esiti or {}).get("foi") or []) if "foi" in (triage or {}) else []:
        mese, indice = str(e.get("mese") or ""), e.get("indice")
        serie = (tab.get("istat_foi") or {}).get("serie") or []
        prec = next((v["valore"] for v in reversed(serie) if v.get("mese") < mese and v.get("valore") is not None), None)
        prova = dict(e.get("prova") or {})
        try:
            nome_mese = _MESI_IT[int(mese[5:7]) - 1]
        except (ValueError, IndexError):
            giro.problema(f"FOI: mese non valido «{mese}»", "dati:foi")
            continue
        prova["estremi"] = list(dict.fromkeys(list(prova.get("estremi") or []) + [_numero_it(float(indice or 0), 1), nome_mese]))
        r = sp.verifica_prova(prova, get=get)
        if not re.fullmatch(r"\d{4}-\d{2}", mese) or not isinstance(indice, (int, float)) or r["esito"] != "OK" \
                or (prec and abs(indice / prec - 1) > 0.03):
            giro.problema(f"FOI {mese}: valore {indice} non accettato — " + "; ".join(r["motivi"] or ["fuori dai limiti rispetto al mese precedente"]),
                          "dati:foi")
            continue
        tassi.aggiungi_foi(mese, float(indice), r["url"], tab=tab, path=path, oggi=oggi)
        giro.riga(f"FOI {mese}: {indice} (verificato su {r['url']})")
    for e in ((esiti or {}).get("bot12") or []) if "bot12" in (triage or {}) else []:
        asta, rend = str(e.get("asta") or ""), e.get("rendimento")
        serie = (tab.setdefault("bot12", {"_meta": {}, "serie": []})).setdefault("serie", [])
        prec = next((v.get("rendimento_medio_ponderato") for v in reversed(serie) if str(v.get("asta")) < asta), None)
        prova = dict(e.get("prova") or {})
        prova["estremi"] = list(dict.fromkeys(list(prova.get("estremi") or []) + [_numero_it(float(rend or 0), 3)]))
        r = sp.verifica_prova(prova, get=get)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", asta) or not isinstance(rend, (int, float)) or r["esito"] != "OK" \
                or not -1.0 <= rend <= 12.0 or (prec is not None and abs(rend - prec) > 1.5):
            giro.problema(f"BOT 12 mesi {asta}: {rend} non accettato — " + "; ".join(r["motivi"] or ["fuori dai limiti"]), "dati:bot12")
            continue
        voce = {"asta": asta, "rendimento_medio_ponderato": float(rend), "da_verificare": False, "fonte": r["url"],
                "verificato_il": oggi.isoformat(), "inserito_da": "sentinelle (Action del corpus)"}
        serie[:] = sorted([v for v in serie if v.get("asta") != asta] + [voce], key=lambda v: v["asta"])
        tassi._salva(tab, path)
        giro.riga(f"BOT 12 mesi, asta del {asta}: {rend}%")


# ----------------------------------------------------------------------------------------------- giro

def deterministico(radice: Path, giro: sb.Giro, oggi: _dt.date = None, gu: Gazzetta = None, **iniezioni) -> dict:
    """I passi senza Claude; ritorna il triage per Claude ({} se non serve)."""
    oggi = oggi or sb.oggi()
    gu = gu or Gazzetta()
    for nome, f in (("BCE", lambda: _bce(radice, giro, oggi, iniezioni.get("scarica"))),
                    ("tasso legale", lambda: _legale(radice, giro, oggi, gu, iniezioni.get("scarica"))),
                    ("mora", lambda: _mora(radice, giro, oggi, gu, iniezioni.get("scarica"))),
                    ("soglie d'usura", lambda: _usura(radice, giro, oggi, gu, iniezioni.get("get_html"), iniezioni.get("get_pdf"))),
                    ("tabelle", lambda: _tabelle(radice, giro, oggi, iniezioni.get("articolo")))):
        try:
            f()
        except Exception as e:  # noqa: BLE001 — una fonte che cade non ferma le altre
            giro.parziale()
            giro.problema(f"{nome}: errore ({e.__class__.__name__}: {str(e)[:160]})")
    return triage_claude(radice, oggi)
