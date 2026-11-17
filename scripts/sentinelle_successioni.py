#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA DELLE SUCCESSIONI (v0.36, area «successioni» dell'Action sentinelle): DEAS, AdE, uffici, coefficienti.

Prende il posto dell'attivita' programmata mensile «monitoraggio-successioni-deas».
  1. SENZA Claude, ogni settimana:
     * ultima release del DE.A.S. dalla pagina degli aggiornamenti di Geo Network (regex sulla versione 2.NNx);
     * uffici competenti per le successioni in TUTTA ITALIA (v0.53, `uffici_italia.py`, una volta al mese): si sostituisce solo
       se la struttura regge (Torino con 10 circoscrizioni, comuni non in calo, codici veri) — e i comuni ISTAT;
     * v0.53: le pagine AdE delle specifiche SUC13, del software di controllo e della normativa (pacchetto, versione,
       provvedimento): una versione piu' nuova di quella del plugin e' una issue (`successioni-specifiche.json`);
     * il D.M. MEF dei coefficienti dell'usufrutto e del tasso legale nei sommari della G.U. (dicembre);
     * le righe del changelog-auto su TUS (D.Lgs. 346/1990), D.Lgs. 347/1990 e D.Lgs. 139/2024.
  2. Claude, una volta al mese o quando una sonda segnala qualcosa: provvedimenti e prassi dell'AdE (modello, specifiche
     SUC13, modulo di controllo), contenuto delle release DEAS nuove; consegna esiti con PROVE, non scrive nel repo.
  3. Controllo meccanico: le novita' provate vanno in coda a `changelog-normativo.md` della skill; `suc_calcoli.py` non
     si tocca mai (V1 intoccabile): una costante superata apre una issue.
L'esito del giro va in `wiki-studio/sentinelle/successioni.json`: il gate di freschezza del plugin lo legge al posto della
data scritta a mano nel changelog, se l'esito e' «invariato» o «novita» (non «parziale»).

Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinelle_base as sb  # noqa: E402
import sentinelle_prove as sp  # noqa: E402

REL_CHANGELOG = "skills/assistente-successioni/references/changelog-normativo.md"
#: v0.53: la tabella nazionale ha un file suo; quella di sola Torino (`uffici-competenza-successioni.json`) resta ferma per i
#: plugin installati fino alla 0.52, che leggono solo quel formato
REL_UFFICI = "skills/assistente-successioni/references/uffici-italia-successioni.json"
REL_ESITO = "wiki-studio/sentinelle/successioni.json"
REL_SPECIFICHE = "wiki-studio/sentinelle/successioni-specifiche.json"
REL_PRASSI = "wiki-studio/successioni/prassi-ade.json"
REL_VERSIONE_LOCALE = "skills/assistente-successioni/references/specifiche-suc13/versione.json"
REL_COMUNI = "dati/comuni-italiani.json"
#: v0.53 — le pagine AdE delle specifiche, del software di compilazione/controllo e della normativa (sonde senza Claude)
URL_SPECIFICHE = ("https://www.agenziaentrate.gov.it/portale/schede/dichiarazioni/dichiarazione-di-successione/"
                  "specifiche-tecniche-dichiarazione-di-successione")
URL_SOFTWARE = ("https://www.agenziaentrate.gov.it/portale/schede/dichiarazioni/dichiarazione-di-successione/"
                "sw-comp-dichiarazione-successioni-telematiche")
URL_NORMATIVA = "https://www.agenziaentrate.gov.it/portale/schede/dichiarazioni/dichiarazione-di-successione/np-successione"
#: v0.55 — le pagine AdE dei moduli su cui sono tarati i documenti da firmare (wiki-studio/modelli/successioni): modello e
#: istruzioni (quadro EH, EG9), dichiarazioni sostitutive per la voltura (9T/10T/11T), modelli in uso negli uffici (Mod. 237)
URL_MODULI = {
    "modello e istruzioni": "https://www.agenziaentrate.gov.it/portale/schede/dichiarazioni/dichiarazione-di-successione/"
                            "modiistr-dichsucc",
    "dichiarazioni sostitutive per voltura": "https://www.agenziaentrate.gov.it/portale/strumenti/modelli/"
                                             "modelli-catastali-e-ipotecari/dichiarazioni-sostitutive-per-voltura-catastale",
    "modelli in uso negli uffici": "https://www.agenziaentrate.gov.it/portale/-/modelli-in-uso-presso-gli-uffici-delle-entrate",
}
#: la tabella nazionale degli uffici e i comuni ISTAT si ricostruiscono una volta al mese (≈ 700 pagine AdE)
GIORNI_UFFICI = 28
MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
        "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
URL_DEAS = "https://www.geonetwork.it/supporto/deas-ii-pro/aggiornamenti"
ATTI_SUCCESSIONI = ("tus", "tu-347-1990", "dlgs-139-2024", "dpr-131-1986", "dlgs-123-2025")
#: del codice civile si guarda il solo libro II (successioni, artt. 456-809)
CC_SUCCESSIONI = (456, 809)
SEZIONE_AUTO = "## Novità verificate dalle sentinelle automatiche"
INTRO_AUTO = ("Voci aggiunte dall'Action «sentinelle» del corpus pubblico dopo il controllo meccanico (fonte ufficiale "
              "riscaricata, estremi e citazione ritrovati). Le costanti di calcolo (`scripts/suc_calcoli.py`) non cambiano da "
              "sole: se una novità le tocca, c'è una issue.")
#: v0.53: anche una release 3.x (prima solo «2.NN»)
_RX_VERSIONE = re.compile(r"\b([2-9])\.(\d{2})([a-z]?)\b")


def versione_chiave(v: str) -> tuple:
    m = _RX_VERSIONE.search(str(v or ""))
    return (int(m.group(1)), int(m.group(2)), m.group(3)) if m else (0, 0, "")


def ultima_versione(testo: str) -> str:
    versioni = {f"{a}.{b}{c}" for a, b, c in _RX_VERSIONE.findall(testo or "")}
    return max(versioni, key=versione_chiave) if versioni else ""


def versione_nota(radice: Path) -> str:
    """L'ultima release DEAS che il plugin conosce: dall'esito del giro precedente, altrimenti dal changelog della skill."""
    e = sb.leggi_json(Path(radice) / REL_ESITO, {}) or {}
    if e.get("deas_versione"):
        return str(e["deas_versione"])
    try:
        return ultima_versione((Path(radice) / REL_CHANGELOG).read_text(encoding="utf-8"))
    except OSError:
        return ""


def _uffici(radice: Path, giro: sb.Giro, aggiorna=None, oggi: _dt.date = None) -> bool:
    """v0.53 — la tabella NAZIONALE degli uffici (uffici_italia.py, pagine AdE regione per regione), una volta al mese.
    `aggiorna(dest_tmp) -> dict` sostituisce la raccolta nei test. Non sostituisce la tabella se la nuova non regge:
    meno comuni di prima, Torino senza le sue 10 circoscrizioni, codici estranei (uffici_italia.controlla)."""
    import uffici_italia as ui
    oggi = oggi or sb.oggi()
    p = Path(radice) / REL_UFFICI
    vecchi = sb.leggi_json(p, {}) or {}
    meta = vecchi.get("_meta") or {}
    try:
        eta = (oggi - _dt.date.fromisoformat(str(meta.get("verificato_il")))).days
    except (TypeError, ValueError):
        eta = 9999
    if meta.get("versione") == 2 and eta < GIORNI_UFFICI and aggiorna is None:
        giro.riga(f"uffici competenti: tabella nazionale verificata il {meta.get('verificato_il')} (si rifà ogni mese)")
        return True
    with tempfile.TemporaryDirectory() as d:
        try:
            if aggiorna is not None:
                nuovi = aggiorna(Path(d) / p.name)
            else:
                ui.raccogli(Path(d) / "cache")
                nuovi = ui.costruisci(Path(d) / "cache")
        except (Exception, SystemExit) as e:  # noqa: BLE001 — una pagina AdE cambiata non riscrive la tabella
            giro.riga(f"uffici competenti: pagine AdE non lette ({str(e)[:140]}); tabella invariata "
                      f"(verificata il {meta.get('verificato_il')})")
            return False
    motivi = ui.controlla(nuovi, vecchi) if (nuovi.get("_meta") or {}).get("versione") == 2 else ["tabella non nazionale"]
    torino = ((nuovi.get("citta_divise") or {}).get("L219") or {}).get("parti") or {}
    if len(torino) != 10:
        motivi.append(f"Torino con {len(torino)} circoscrizioni (attese 10)")
    if meta.get("versione") == 2 and len(nuovi.get("comuni") or {}) < 0.98 * len(vecchi.get("comuni") or {}):
        motivi.append("comuni in calo oltre il 2 %")
    if motivi:
        giro.problema("uffici competenti: la tabella letta dall'AdE non regge il confronto (" + "; ".join(motivi)[:300]
                      + "); tabella invariata", "successioni:uffici")
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(nuovi, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cop = (nuovi.get("_meta") or {}).get("copertura") or {}
    giro.riga(f"uffici competenti: tabella nazionale riscritta ({cop.get('comuni_mappati')}/{cop.get('comuni_italiani')} comuni, "
              f"{len(nuovi.get('citta_divise') or {})} città divise)")
    return True


def _comuni(radice: Path, giro: sb.Giro, oggi: _dt.date = None) -> bool:
    """v0.53 — l'elenco ISTAT dei comuni (codici catastali), una volta al mese."""
    import comuni_istat as ci
    oggi = oggi or sb.oggi()
    p = Path(radice) / REL_COMUNI
    vecchi = sb.leggi_json(p, {}) or {}
    try:
        eta = (oggi - _dt.date.fromisoformat(str((vecchi.get("_meta") or {}).get("scaricato_il")))).days
    except (TypeError, ValueError):
        eta = 9999
    if eta < GIORNI_UFFICI:
        return True
    try:
        nuovi = ci.aggiorna(p)
        giro.riga(f"comuni ISTAT: {nuovi['_meta']['comuni']} vigenti, {nuovi['_meta']['soppressi']} soppressi")
        return True
    except (Exception, SystemExit) as e:  # noqa: BLE001
        giro.riga(f"comuni ISTAT: elenco non aggiornato ({str(e)[:120]})")
        return False


def _prassi(radice: Path, giro: sb.Giro, oggi: _dt.date = None) -> bool:
    """v0.53 — l'indice della prassi AdE su successioni e donazioni (circolari, risoluzioni, risposte), una volta al mese:
    l'anno corrente e il precedente (le annate vecchie restano come sono)."""
    import prassi_ade as pa
    oggi = oggi or sb.oggi()
    p = Path(radice) / REL_PRASSI
    vecchi = sb.leggi_json(p, {}) or {}
    try:
        eta = (oggi - _dt.date.fromisoformat(str((vecchi.get("_meta") or {}).get("verificato_il")))).days
    except (TypeError, ValueError):
        eta = 9999
    if eta < GIORNI_UFFICI:
        return True
    try:
        r = pa.aggiorna(oggi.year - 1, p)
        giro.riga(f"prassi AdE: {r['nuovi']} documenti nuovi, {r['totale']} in indice ({len(r['errori'])} pagine non lette)")
        return not r["errori"]
    except Exception as e:  # noqa: BLE001
        giro.riga(f"prassi AdE: indice non aggiornato ({e.__class__.__name__})")
        return False


def _data_italiana(s: str) -> str:
    """«13 febbraio 2025» / «11/03/2026» → ISO; '' se non si legge."""
    m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", str(s or "").lower())
    if m and m.group(2) in MESI:
        return f"{m.group(3)}-{MESI[m.group(2)]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", str(s or ""))
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def html_grezzo(url: str) -> str:
    """La pagina con i link (lo scaricatore delle prove la ripulisce dall'HTML: il nome del pacchetto sta nell'href)."""
    from urllib.request import Request, urlopen
    with urlopen(Request(url, headers={"User-Agent": sp.UA, "Accept-Language": "it"}), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def sonda_specifiche(get) -> dict:
    """v0.53 — che cosa pubblica l'AdE oggi: pacchetto delle specifiche SUC13 (nome con la data), versione del software di
    controllo, ultimo provvedimento sul modello. Solo regex sulle pagine: nessun giudizio."""
    out = {}
    t = get(URL_SPECIFICHE)
    pacchetti = sorted(set(re.findall(r"(SUC13_(\d{8}))\.zip", t)), key=lambda x: x[1])
    if pacchetti:
        nome, data = pacchetti[-1]
        link = re.search(r'href="([^"]*' + re.escape(nome) + r'\.zip[^"]*)"', t)
        out["pacchetto"] = nome
        out["data_pacchetto"] = f"{data[:4]}-{data[4:6]}-{data[6:]}"
        if link:
            href = link.group(1)
            out["url_pacchetto"] = href if href.startswith("http") else "https://www.agenziaentrate.gov.it" + href
    t = get(URL_SOFTWARE)
    versioni = re.findall(r"[Vv]ersione\s+(\d+\.\d+(?:\.\d+)?)\s+del\s+(\d{2}/\d{2}/\d{4})", re.sub(r"<[^>]+>", " ", t))
    if versioni:
        v = max(versioni, key=lambda x: tuple(int(n) for n in x[0].split(".")))
        out["software_controllo"] = {"versione": v[0], "data": _data_italiana(v[1])}
    t = get(URL_NORMATIVA)
    prov = [_data_italiana(x) for x in re.findall(r"Provvedimento del (\d{1,2} [a-z]+ \d{4})", re.sub(r"<[^>]+>", " ", t))]
    prov = sorted(x for x in prov if x)
    if prov:
        out["provvedimento"] = prov[-1]
    return out


def sonda_moduli(get) -> dict:
    """v0.55 — per ogni pagina dei moduli: data «Ultimo aggiornamento» e nomi dei file scaricabili (PDF, RTF, DOC). Solo
    regex; una pagina non letta resta fuori (nessun segnale)."""
    out = {}
    for nome, url in URL_MODULI.items():
        try:
            t = get(url)
        except Exception:  # noqa: BLE001
            continue
        if not t:
            continue
        piano = re.sub(r"<[^>]+>", " ", t)
        agg = re.search(r"Ultimo aggiornamento:?\s*(\d{1,2} [a-z]+ \d{4})", piano)
        file = sorted({_nome_file(h) for h in re.findall(r'href="([^"]+)"', t)
                       if re.search(r"\.(?:pdf|rtf|doc|docx)(?:[/?#]|$)", h, re.I) or "/documents/d/guest/" in h})
        out[nome] = {"aggiornato": _data_italiana(agg.group(1)) if agg else "", "file": file}
    return out


def _nome_file(href: str) -> str:
    """Il nome del file di un link AdE («…/Modello+Successione.pdf/88520cc9…?t=…» → «Modello+Successione.pdf»)."""
    pezzi = [x for x in re.sub(r"[?#].*$", "", href).split("/") if x]
    con_estensione = [x for x in pezzi if re.search(r"\.(?:pdf|rtf|doc|docx)$", x, re.I)]
    return (con_estensione or pezzi or [href])[-1]


def confronta_moduli(prima: dict, ora: dict) -> list:
    """Le pagine dei moduli cambiate dall'ultimo giro (data di aggiornamento piu' nuova o file diversi)."""
    segnali = []
    for nome, v in (ora or {}).items():
        p = (prima or {}).get(nome)
        if not p:
            continue
        if v.get("aggiornato") and v["aggiornato"] > str(p.get("aggiornato") or ""):
            segnali.append(f"pagina AdE «{nome}» aggiornata il {v['aggiornato']}")
        elif v.get("file") and p.get("file") and set(v["file"]) != set(p["file"]):
            nuovi = sorted(set(v["file"]) - set(p["file"]))
            segnali.append(f"pagina AdE «{nome}»: file cambiati" + (f" (nuovi: {', '.join(nuovi[:4])})" if nuovi else ""))
    return segnali


def confronta_specifiche(pubblicato: dict, locale: dict) -> list:
    """Le differenze che contano: pacchetto, software di controllo, provvedimento piu' nuovi di quelli del plugin."""
    segnali = []
    if pubblicato.get("data_pacchetto") and pubblicato["data_pacchetto"] > str(locale.get("data_pacchetto") or ""):
        segnali.append(f"specifiche tecniche nuove {pubblicato['pacchetto']} (il generatore è tarato su {locale.get('pacchetto')})")
    sw, swl = pubblicato.get("software_controllo") or {}, locale.get("software_controllo") or {}
    if sw.get("versione") and tuple(int(x) for x in sw["versione"].split(".")) > tuple(int(x) for x in str(swl.get("versione") or "0").split(".")):
        segnali.append(f"software di controllo AdE {sw['versione']} del {sw.get('data')} (il plugin conosce la {swl.get('versione')})")
    if pubblicato.get("provvedimento") and pubblicato["provvedimento"] > str(locale.get("provvedimento") or ""):
        segnali.append(f"provvedimento AdE del {pubblicato['provvedimento']} sul modello (il plugin conosce il {locale.get('provvedimento')})")
    return segnali


def deterministico(radice: Path, giro: sb.Giro, oggi: _dt.date = None, gu=None, get=None, aggiorna_uffici=None,
                   comuni: bool = True) -> dict:
    """Le sonde senza Claude; ritorna il triage per Claude ({} se non serve) e prepara l'esito del giro."""
    oggi = oggi or sb.oggi()
    radice = Path(radice)
    esito_prec = sb.leggi_json(radice / REL_ESITO, {}) or {}
    sonde = {"deas": False, "uffici": False, "gu": False}
    segnali = []
    nota = versione_nota(radice)
    try:
        testo = (get or (lambda u: sp.scarica(u)[0]))(URL_DEAS)
        ultima = ultima_versione(testo)
        sonde["deas"] = bool(ultima)
        if ultima and versione_chiave(ultima) > versione_chiave(nota):
            segnali.append({"tipo": "deas", "cosa": f"release DEAS {ultima} (il plugin conosce la {nota or 'n.d.'})", "url": URL_DEAS})
            giro.riga(f"DEAS: release nuova {ultima} (nota {nota or 'n.d.'})")
        else:
            giro.riga(f"DEAS: ultima release {ultima or 'non letta'}")
        giro.dati["deas_versione"] = ultima or nota
    except Exception as e:  # noqa: BLE001
        giro.riga(f"DEAS: pagina degli aggiornamenti non letta ({e.__class__.__name__})")
        giro.dati["deas_versione"] = nota
    sonde["uffici"] = _uffici(radice, giro, aggiorna_uffici, oggi)
    if comuni and aggiorna_uffici is None:
        _comuni(radice, giro, oggi)
        _prassi(radice, giro, oggi)
    # v0.53 — specifiche SUC13, software di controllo, provvedimenti: sonde deterministiche (fuori dal giudizio «completo»
    # per i primi giri: una pagina AdE muta non deve bloccare la freschezza)
    try:
        pubblicato = sonda_specifiche(get or html_grezzo)
        locale = sb.leggi_json(radice / REL_VERSIONE_LOCALE, {}) or {}
        nuove = confronta_specifiche(pubblicato, locale) if pubblicato else []
        prec = sb.leggi_json(radice / REL_SPECIFICHE, {}) or {}
        moduli = {}
        try:
            moduli = sonda_moduli(get or html_grezzo)
        except Exception as e:  # noqa: BLE001
            giro.riga(f"AdE: pagine dei moduli non lette ({e.__class__.__name__})")
        cambi_moduli = confronta_moduli(prec.get("moduli") or {}, moduli)
        for c in cambi_moduli:
            segnali.append({"tipo": "moduli", "cosa": c, "url": URL_MODULI.get(c.split("«")[1].split("»")[0]) if "«" in c else ""})
            giro.problema(f"{c}: rivedere le schede dei documenti da firmare (wiki-studio/modelli/successioni) contro il "
                          "modulo AdE", "successioni:moduli")
        sb.scrivi_json(radice / REL_SPECIFICHE, {"_meta": {"descrizione": "Ultime specifiche SUC13, software di controllo e "
                                                                          "provvedimento pubblicati dall'AdE (sentinella delle successioni)",
                                                           "verificato_il": oggi.isoformat()},
                                                 **pubblicato, "novita": nuove,
                                                 "moduli": {**(prec.get("moduli") or {}), **moduli},
                                                 "moduli_novita": cambi_moduli})
        sonde["specifiche"] = bool(pubblicato.get("pacchetto"))
        for s in nuove:
            segnali.append({"tipo": "specifiche", "cosa": s, "url": URL_SPECIFICHE})
            giro.problema(f"{s}: rigenerare schema e codici sul Mac (scripts/suc13_aggiorna.py) e rieseguire i test del generatore",
                          "successioni:specifiche")
        giro.riga("AdE: " + (", ".join(f"{k} {v if not isinstance(v, dict) else v.get('versione')}" for k, v in pubblicato.items()
                                       if k in ("pacchetto", "software_controllo", "provvedimento")) or "pagine non lette"))
    except Exception as e:  # noqa: BLE001
        giro.riga(f"AdE: pagine delle specifiche non lette ({e.__class__.__name__})")
    if gu is not None:
        try:
            dm = gu.cerca(r"usufrutto|rendite\s+e\s+pensioni|coefficienti\s+per\s+la\s+determinazione")
            sonde["gu"] = True
            for a in dm:
                segnali.append({"tipo": "coefficienti", "cosa": f"G.U.: {a['titolo'][:200]}", "codice": a["codice"], "data": a["data"]})
                giro.problema(f"G.U. {a['data']} ({a['codice']}): decreto su usufrutto/coefficienti — le costanti di "
                              "scripts/suc_calcoli.py vanno riviste a mano (mai dalla sentinella)", "successioni:coefficienti")
        except Exception as e:  # noqa: BLE001
            giro.riga(f"G.U.: sommari non letti ({e.__class__.__name__})")
    ultimo = str(esito_prec.get("verificato_il") or "")
    righe_cc = [r for r in sb.cambi_dopo(sb.changelog_auto(radice), "cc", ultimo)
                if str(r.get("articolo") or "").split("-")[0].isdigit()
                and CC_SUCCESSIONI[0] <= int(str(r.get("articolo")).split("-")[0]) <= CC_SUCCESSIONI[1]]
    for r in righe_cc:
        segnali.append({"tipo": "corpus", "cosa": f"c.c. art. {r.get('articolo')} {r.get('tipo')} (successioni, libro II)"})
    for slug in ATTI_SUCCESSIONI:
        for r in sb.cambi_dopo(sb.changelog_auto(radice), slug, ultimo):
            segnali.append({"tipo": "corpus", "cosa": f"{r.get('atto')} art. {r.get('articolo')} {r.get('tipo')} "
                                                      f"(atto modificante: {r.get('atto_modificante') or 'n.d.'})"})
    if any(s["tipo"] == "corpus" for s in segnali):
        giro.problema("corpus: articoli di TUS / D.Lgs. 347/1990 / D.Lgs. 139/2024 / TUR / D.Lgs. 123/2025 / c.c. libro II "
                      "cambiati — verificare aliquote, franchigie e importi di scripts/suc_calcoli.py (si rivedono a mano)",
                      "successioni:corpus")
    mensile = str(esito_prec.get("claude_il") or "")[:7] != oggi.strftime("%Y-%m")
    giro.dati["sonde"] = sonde
    giro.dati["segnali"] = segnali
    if not (mensile or segnali):
        return {}
    return {"oggi": oggi.isoformat(), "mensile": mensile, "segnali": segnali, "deas_nota": nota,
            "cerca": ["provvedimenti del Direttore dell'Agenzia delle Entrate sul modello di dichiarazione di successione e "
                      "domanda di volture catastali", "specifiche tecniche SUC13 e modulo di controllo (versione nuova)",
                      "circolari e risoluzioni AdE in materia di imposta di successione e donazione",
                      "contenuto delle release DEAS nuove (pagina degli aggiornamenti di Geo Network)"]}


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z]", "", (s or "").lower())


def _estremi_riga(riga: str) -> str:
    """Gli estremi di una riga del changelog («… (estremi) — sintesi»), o il nome se non ci sono."""
    nome = riga.split(" · ", 1)[-1].split(" — ", 1)[0]
    m = re.search(r"\(([^()]*)\)\s*$", nome)
    return m.group(1) if m else nome


def aggiungi_al_changelog(p: Path, righe: list) -> None:
    """In coda alla sezione delle sentinelle; una novita' gia' scritta (stessi estremi) non si riscrive."""
    if not righe:
        return
    testo = p.read_text(encoding="utf-8") if p.exists() else ""
    gia = _norm(testo.split(SEZIONE_AUTO, 1)[1]) if SEZIONE_AUTO in testo else ""
    righe = [r for r in righe if not (gia and len(_norm(_estremi_riga(r))) >= 8 and _norm(_estremi_riga(r)) in gia)]
    if not righe:
        return
    if SEZIONE_AUTO not in testo:
        testo = testo.rstrip("\n") + "\n\n" + SEZIONE_AUTO + "\n\n" + INTRO_AUTO + "\n\n"
    p.write_text(testo.rstrip("\n") + "\n" + "\n".join(righe) + "\n", encoding="utf-8")


def dopo_claude(radice: Path, triage: dict, esiti: dict, giro: sb.Giro, oggi: _dt.date = None, get=None, claude_ok: bool = True) -> None:
    """Applica le novita' provate; scrive l'esito del giro. Va chiamata anche quando Claude non e' partito (triage vuoto)."""
    oggi = oggi or sb.oggi()
    radice = Path(radice)
    fuori = sb.ripristina_fuori_da(radice, lambda rel: rel in (REL_UFFICI, REL_SPECIFICHE, REL_COMUNI, REL_PRASSI))  # li scrivono le sonde
    if fuori:
        giro.problema(f"file del repo modificati fuori dal controllo, rimessi com'erano: {', '.join(fuori[:6])}")
    righe, novita, scartate = [], 0, 0
    for e in (esiti or {}).get("novita") or []:
        prove = [p for p in (e.get("prove") or []) if isinstance(p, dict)]
        verificate = [r for r in (sp.verifica_prova(p, get=get) for p in prove) if r["esito"] == "OK"]
        if not verificate:
            scartate += 1
            giro.problema(f"novità segnalata ma non provata: {str(e.get('estremi') or e.get('titolo') or '')[:160]}")
            continue
        novita += 1
        titolo, estremi = str(e.get("titolo") or "").strip(), str(e.get("estremi") or "").strip()
        nome = f"{titolo} ({estremi})" if titolo and estremi and estremi not in titolo else (titolo or estremi or "novità")
        righe.append(f"- **{oggi.strftime('%d/%m/%Y')}** · {nome} — "
                     f"{str(e.get('sintesi') or '').strip()} ([fonte ufficiale]({verificate[0]['url']}))")
        if e.get("tocca_calcoli"):
            giro.problema(f"{e.get('estremi') or e.get('titolo')}: tocca i calcoli — rivedere a mano scripts/suc_calcoli.py",
                          "successioni:calcoli")
    aggiungi_al_changelog(radice / REL_CHANGELOG, righe)
    sonde = giro.dati.get("sonde") or {}
    # gli uffici hanno una vita utile di un anno: una pagina AdE che non si legge non rende il giro incompleto
    completo = bool(sonde.get("deas")) and (not triage or claude_ok) and not scartate
    esito = "novita" if novita and completo else "invariato" if completo else "parziale"
    if esito == "parziale":
        giro.parziale()
    prec = sb.leggi_json(radice / REL_ESITO, {}) or {}
    dati = {"_meta": {"descrizione": "Esito dell'ultimo giro della sentinella delle successioni (Action «sentinelle» del corpus). "
                                     "Il gate di freschezza del plugin vale come data di controllo se l'esito non è «parziale»."},
            "verificato_il": oggi.isoformat() if esito != "parziale" else prec.get("verificato_il"),
            "ultimo_giro": oggi.isoformat(), "esito": esito,
            # con un giro parziale la release nota non avanza: le novita' della release si cercano di nuovo al giro dopo
            "deas_versione": (giro.dati.get("deas_versione") if esito != "parziale" else None) or prec.get("deas_versione"),
            "claude_il": oggi.isoformat() if (triage and claude_ok) else prec.get("claude_il"),
            "novita": novita, "segnali": [s.get("cosa") for s in giro.dati.get("segnali") or []][:20]}
    sb.scrivi_json(radice / REL_ESITO, dati)
    giro.riga(f"esito: {esito} · novità provate {novita} · scartate {scartate}")
