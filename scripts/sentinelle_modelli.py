#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA DEI MODELLI NELL'ACTION (v0.36, area «modelli» dell'Action sentinelle).

Fa nel repo pubblico del corpus il giro mensile che in Cowork non partiva mai, e lo fa ogni settimana:
  1. SENZA Claude: `sentinella_modelli.giro(motori=False)` — norme citate contro il corpus datato, requisiti per tipo,
     formule superate, cifre delle tabelle, metadati (i motori .docx restano ai test del plugin). Lo stato delle impronte
     sta nel repo (`wiki-studio/sentinelle/modelli-stato.json`); le marcature «da ricontrollare» si consolidano in
     `wiki-studio/modelli/modelli.meta.json`; `norme-citate.json` si riesporta.
  2. Claude corregge SOLO i modelli rossi nuovi e quelli che citano norme con testo cambiato (al massimo MAX_MODELLI per
     giro), modificando la scheda del modello; consegna gli esiti.
  3. Controllo meccanico per ogni scheda toccata:
     * cambiano solo le sezioni «Testo del modello», «Normativa» e «Aggiornamenti» (frontmatter e resto identici);
     * nessun nome vietato e nessun dato personale nuovo; nessun estremo di pronuncia aggiunto;
     * `giro(solo_ids=[id])` della scheda corretta da' VERDE.
     Se passa: `allinea(...)` (verifica del modello rinnovata). Se no: la scheda torna com'era, resta «da ricontrollare»,
     riga nella issue.

Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinelle_base as sb  # noqa: E402

REL_STATO_REPO = "wiki-studio/sentinelle/modelli-stato.json"
REL_META = "wiki-studio/modelli/modelli.meta.json"
DIR_SCHEDE = "wiki-studio/modelli/civile/"
MAX_MODELLI = 10
SEZIONI_MODIFICABILI = ("testo del modello", "normativa", "aggiornamenti")
_RX_PRONUNCIA = re.compile(r"\b(?:cass(?:azione|\.)|ss\.\s?uu\.|sez(?:ioni)?\.?\s+unite|corte\s+cost(?:ituzionale|\.)|"
                           r"trib(?:unale|\.)|c\.\s?app\.|corte\s+d['’]appello)[^\n]{0,80}?\b\d{1,6}\s*/\s*\d{4}\b", re.I)


def _sm():
    import sentinella_modelli as sm
    return sm


def _consolida_meta(radice: Path) -> bool:
    """Scrive nel file del repo il sidecar dei modelli VIVO (bundle + patch del giro), senza la nota del corpus vivo."""
    import corpus
    try:
        dati = json.loads(corpus.risolvi("modelli/modelli.meta.json"))
    except (Exception, SystemExit):
        return False
    (dati.get("_meta") or {}).pop("corpus_vivo", None)
    p = Path(radice) / REL_META
    vecchio = sb.leggi_json(p, {})
    if dati == vecchio:
        return False
    sb.scrivi_json(p, dati)
    # le patch ora sono nel file: il corpus vivo del giro si svuota per quel percorso
    agg = corpus._agg("modelli/modelli.meta.json")
    if agg.exists():
        agg.unlink()
    return True


def _stato_dentro(radice: Path) -> None:
    """Lo stato delle impronte dal repo alla cartella persistente del giro (STUDIO_STATO_PERSISTENTE)."""
    sm = _sm()
    src = Path(radice) / REL_STATO_REPO
    if src.is_file():
        sm.file_stato().parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, sm.file_stato())


def _stato_fuori(radice: Path) -> None:
    sm = _sm()
    if sm.file_stato().is_file():
        dest = Path(radice) / REL_STATO_REPO
        dest.parent.mkdir(parents=True, exist_ok=True)
        st = json.loads(sm.file_stato().read_text(encoding="utf-8"))
        st.pop("report", None)                       # percorso locale del runner: non si pubblica
        sb.scrivi_json(dest, st)


def deterministico(radice: Path, giro: sb.Giro, oggi: _dt.date = None, fonte=None) -> dict:
    sm = _sm()
    oggi = oggi or sb.oggi()
    _stato_dentro(radice)
    prima = dict((sm.stato().get("verdetti") or {}))
    res = sm.giro(oggi=oggi, fonte=fonte, motori=False, patch=True, scrivi=True)
    _consolida_meta(radice)
    try:
        sm.esporta_norme_citate(fonte=fonte, scrivi=True)
    except Exception as e:  # noqa: BLE001
        giro.riga(f"norme-citate.json non riesportato ({e.__class__.__name__})")
    _stato_fuori(radice)
    c = res.get("conteggi") or {}
    giro.riga(f"giro dei modelli: {res.get('modelli_valutati')} modelli · 🔴 {c.get('ROSSO', 0)} · 🟡 {c.get('GIALLO', 0)} · "
              f"🟢 {c.get('VERDE', 0)}")
    for a in res.get("avvisi") or []:
        giro.riga(f"⚠️ {a}")
    # al triage: i rossi nuovi (o con motivi nuovi) e i modelli con norme dal testo cambiato
    scelti = []
    for r in res.get("modelli") or []:
        if r.get("verdetto") != "ROSSO":
            continue
        motivi = sm.motivi_brevi(r, 6)
        nuovo = (prima.get(str(r["id"])) or {}).get("verdetto") != "ROSSO" or (prima.get(str(r["id"])) or {}).get("motivi") != sm.motivi_brevi(r)
        testo_cambiato = any(str(i.get("regola") or "") in ("norme:modificata", "norme:abrogata") for i in r.get("issue") or [])
        if nuovo or testo_cambiato:
            scelti.append({"id": str(r["id"]), "titolo": r.get("titolo"), "file": _file_modello(r["id"]),
                           "problemi": [{"regola": i.get("regola"), "messaggio": i.get("messaggio"), "correzione": i.get("correzione")}
                                        for i in r.get("issue") or [] if i.get("gravita") == sm.ROSSO][:8],
                           "motivi": motivi})
    for r in res.get("modelli") or []:
        if r.get("verdetto") == "ROSSO":
            giro.da_ricontrollare.append(f"modello:{r['id']}")
    if len(scelti) > MAX_MODELLI:
        giro.riga(f"{len(scelti) - MAX_MODELLI} modelli rossi rinviati al prossimo giro (tetto di {MAX_MODELLI} per giro)")
    return {"oggi": oggi.isoformat(), "modelli": scelti[:MAX_MODELLI]} if scelti else {}


def _file_modello(ident) -> str:
    sm = _sm()
    for m in sm.leggi_json_vivo(sm.REL_CATALOGO).get("modelli", []):
        if str(m.get("id")) == str(ident):
            return str(m.get("file") or "")
    return ""


def sezioni(testo: str) -> tuple:
    """(frontmatter, {titolo sezione minuscolo: contenuto}, testo fuori dalle sezioni)."""
    m = re.match(r"^---\s*\n.*?\n---\s*\n", testo or "", re.S)
    fm = m.group(0) if m else ""
    corpo = (testo or "")[len(fm):]
    parti = re.split(r"(?m)^(## .*)$", corpo)
    fuori, sez = parti[0], {}
    for i in range(1, len(parti), 2):
        sez[parti[i][3:].strip().lower()] = parti[i + 1] if i + 1 < len(parti) else ""
    return fm, sez, fuori


def controlla_scheda(vecchio: str, nuovo: str) -> list:
    """I motivi per cui la scheda corretta NON si accetta ([] = forma accettabile)."""
    motivi = []
    fm_v, sez_v, fuori_v = sezioni(vecchio)
    fm_n, sez_n, fuori_n = sezioni(nuovo)
    if fm_v != fm_n:
        motivi.append("il frontmatter è cambiato")
    if fuori_v.strip() != fuori_n.strip():
        motivi.append("è cambiato il testo prima delle sezioni")
    for nome in set(sez_v) | set(sez_n):
        modificabile = any(nome.startswith(s) for s in SEZIONI_MODIFICABILI)
        if not modificabile and sez_v.get(nome, "").strip() != sez_n.get(nome, "").strip():
            motivi.append(f"è cambiata la sezione «{nome}», che non si tocca")
    if sb.nomi_vietati(nuovo) != sb.nomi_vietati(vecchio):
        motivi.append("compare un nome vietato")
    nuovi_dati = set(sb.dati_personali(nuovo)) - set(sb.dati_personali(vecchio))
    if nuovi_dati:
        motivi.append("compaiono dati personali (" + ", ".join(sorted({t for t, _ in nuovi_dati})) + ")")
    pron = set(m.group(0) for m in _RX_PRONUNCIA.finditer(nuovo)) - set(m.group(0) for m in _RX_PRONUNCIA.finditer(vecchio))
    if pron:
        motivi.append("sono stati aggiunti estremi di pronunce (nei modelli si citano solo norme)")
    return motivi


def dopo_claude(radice: Path, triage: dict, esiti: dict, giro: sb.Giro, oggi: _dt.date = None, fonte=None) -> dict:
    sm = _sm()
    oggi = oggi or sb.oggi()
    radice = Path(radice)
    ammessi = {str(m.get("file")) for m in (triage or {}).get("modelli") or [] if m.get("file")}
    fuori = sb.ripristina_fuori_da(radice, lambda rel: rel in ammessi)
    if fuori:
        giro.problema(f"file fuori dal triage modificati, rimessi com'erano: {', '.join(fuori[:6])}")
    toccati = {rel for _st, rel in sb.toccati(radice) if rel in ammessi}
    out = {"corretti": [], "respinti": [], "non_toccati": []}
    _stato_dentro(radice)
    for m in (triage or {}).get("modelli") or []:
        rel, ident = str(m.get("file")), str(m.get("id"))
        if rel not in toccati:
            out["non_toccati"].append(ident)
            giro.problema(f"modello {ident} ({m.get('titolo')}): rosso, non corretto in questo giro — "
                          + "; ".join(m.get("motivi") or [])[:300], f"modello:{ident}")
            continue
        vecchio = sb.git(radice, "show", f"HEAD:{rel}").stdout
        nuovo = (radice / rel).read_text(encoding="utf-8")
        motivi = controlla_scheda(vecchio, nuovo)
        if not motivi:
            r = sm.giro(oggi=oggi, fonte=fonte, solo_ids=[ident], motori=False, patch=False, scrivi=False)
            verdetto = ((r.get("modelli") or [{}])[0]).get("verdetto")
            if verdetto != "VERDE":
                motivi.append(f"dopo la correzione il controllo dà {verdetto}: " + "; ".join(sm.motivi_brevi((r.get("modelli") or [{}])[0])))
        if motivi:
            sb.git(radice, "checkout", "--", rel)
            out["respinti"].append(ident)
            giro.problema(f"modello {ident}: correzione respinta — " + "; ".join(motivi)[:400], f"modello:{ident}")
            continue
        sintesi = str(((esiti or {}).get("modelli") or {}).get(ident, {}).get("sintesi") or "correzione delle sentinelle automatiche")
        sm.allinea(ident, sintesi[:300], fonte_nome="sentinella-action", oggi=oggi)
        out["corretti"].append(ident)
        giro.riga(f"modello {ident} corretto e riverificato: {sintesi[:160]}")
    # giro finale: stato, marcature e norme citate allineati alle schede corrette
    if out["corretti"]:
        sm.giro(oggi=oggi, fonte=fonte, solo_ids=out["corretti"], motori=False, patch=True, scrivi=True)
        try:
            sm.esporta_norme_citate(fonte=fonte, scrivi=True)
        except Exception:  # noqa: BLE001
            pass
    _consolida_meta(radice)
    _stato_fuori(radice)
    giro.da_ricontrollare = sorted(set(giro.da_ricontrollare) - {f"modello:{i}" for i in out["corretti"]})
    return out


def prepara_ambiente(radice: Path) -> None:
    """Nell'Action: corpus vivo e stato persistente in cartelle temporanee (le imposta il workflow)."""
    for var in ("STUDIO_CORPUS", "STUDIO_STATO_PERSISTENTE"):
        if not os.environ.get(var):
            raise SystemExit(f"[sentinelle_modelli] manca {var}: nell'Action la imposta il workflow (cartella temporanea)")
