#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA DELLE SUCCESSIONI (v0.36, area «successioni» dell'Action sentinelle): DEAS, AdE, uffici, coefficienti.

Prende il posto dell'attivita' programmata mensile «monitoraggio-successioni-deas».
  1. SENZA Claude, ogni settimana:
     * ultima release del DE.A.S. dalla pagina degli aggiornamenti di Geo Network (regex sulla versione 2.NNx);
     * uffici competenti per le successioni della provincia di Torino (`uffici_competenza.aggiorna` su un file
       temporaneo: si sostituisce solo se la struttura regge — 10 circoscrizioni, TT2 e TT3 — e i comuni non calano);
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
REL_UFFICI = "skills/assistente-successioni/references/uffici-competenza-successioni.json"
REL_ESITO = "wiki-studio/sentinelle/successioni.json"
URL_DEAS = "https://www.geonetwork.it/supporto/deas-ii-pro/aggiornamenti"
ATTI_SUCCESSIONI = ("tus", "tu-347-1990", "dlgs-139-2024")
SEZIONE_AUTO = "## Novità verificate dalle sentinelle automatiche"
INTRO_AUTO = ("Voci aggiunte dall'Action «sentinelle» del corpus pubblico dopo il controllo meccanico (fonte ufficiale "
              "riscaricata, estremi e citazione ritrovati). Le costanti di calcolo (`scripts/suc_calcoli.py`) non cambiano da "
              "sole: se una novità le tocca, c'è una issue.")
_RX_VERSIONE = re.compile(r"\b2\.(\d{2})([a-z]?)\b")


def versione_chiave(v: str) -> tuple:
    m = _RX_VERSIONE.search(str(v or ""))
    return (int(m.group(1)), m.group(2)) if m else (0, "")


def ultima_versione(testo: str) -> str:
    versioni = {f"2.{a}{b}" for a, b in _RX_VERSIONE.findall(testo or "")}
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


def _uffici(radice: Path, giro: sb.Giro, aggiorna=None) -> bool:
    import uffici_competenza as uc
    p = Path(radice) / REL_UFFICI
    vecchi = sb.leggi_json(p, {}) or {}
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / p.name
        try:
            nuovi = (aggiorna or uc.aggiorna)(tmp)
        except (Exception, SystemExit) as e:  # noqa: BLE001 — una pagina AdE cambiata non riscrive la tabella
            giro.riga(f"uffici competenti: pagine AdE non lette ({str(e)[:140]}); tabella invariata "
                      f"(verificata il {(vecchi.get('_meta') or {}).get('verificato_il')})")
            return False
        if set(nuovi.get("uffici") or {}) != set(vecchi.get("uffici") or {}) and vecchi.get("uffici") \
                or len(nuovi.get("torino_circoscrizioni") or {}) != 10 \
                or len(nuovi.get("comuni") or {}) < 0.98 * len(vecchi.get("comuni") or {}):
            giro.problema("uffici competenti: la tabella letta dall'AdE non regge il confronto (circoscrizioni o comuni mancanti); "
                          "tabella invariata", "successioni:uffici")
            return False
        cambiati = {k: v for k, v in nuovi.items() if k != "_meta" and vecchi.get(k) != v}
        if cambiati or not p.exists():
            p.write_text(tmp.read_text(encoding="utf-8"), encoding="utf-8")
            giro.riga(f"uffici competenti: tabella aggiornata ({', '.join(cambiati) or 'nuova'})")
        else:
            vecchi.setdefault("_meta", {})["verificato_il"] = sb.oggi().isoformat()
            sb.scrivi_json(p, vecchi)
            giro.riga("uffici competenti: invariati, verifica rinnovata")
    return True


def deterministico(radice: Path, giro: sb.Giro, oggi: _dt.date = None, gu=None, get=None, aggiorna_uffici=None) -> dict:
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
    sonde["uffici"] = _uffici(radice, giro, aggiorna_uffici)
    if gu is not None:
        try:
            dm = gu.cerca(r"usufrutto|rendite\s+e\s+pensioni|coefficienti\s+per\s+la\s+determinazione")
            sonde["gu"] = True
            for a in dm:
                segnali.append({"tipo": "coefficienti", "cosa": f"G.U.: {a['titolo'][:200]}", "codice": a["codice"], "data": a["data"]})
                giro.problema(f"G.U. {a['data']} ({a['codice']}): decreto su usufrutto/coefficienti — le costanti di "
                              "scripts/suc_calcoli.py vanno riviste a mano (V1 intoccabile)", "successioni:coefficienti")
        except Exception as e:  # noqa: BLE001
            giro.riga(f"G.U.: sommari non letti ({e.__class__.__name__})")
    ultimo = str(esito_prec.get("verificato_il") or "")
    for slug in ATTI_SUCCESSIONI:
        for r in sb.cambi_dopo(sb.changelog_auto(radice), slug, ultimo):
            segnali.append({"tipo": "corpus", "cosa": f"{r.get('atto')} art. {r.get('articolo')} {r.get('tipo')} "
                                                      f"(atto modificante: {r.get('atto_modificante') or 'n.d.'})"})
    if any(s["tipo"] == "corpus" for s in segnali):
        giro.problema("corpus: articoli di TUS / D.Lgs. 347/1990 / D.Lgs. 139/2024 cambiati — verificare aliquote, franchigie e "
                      "importi di scripts/suc_calcoli.py (si rivedono a mano)", "successioni:corpus")
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
    fuori = sb.ripristina_fuori_da(radice, lambda rel: rel in (REL_UFFICI,))     # gli uffici li scrive la sonda, non Claude
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
