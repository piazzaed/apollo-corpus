#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA NORMATIVA AUTOMATICA (v0.36, area «normativa» dell'Action sentinelle).

Fa ogni settimana, nel repo pubblico del corpus, il giro che prima faceva l'attivita' programmata di Cowork:
  1. SENZA Claude (deterministico):
     * una voce del sidecar (`changelog-riforme.meta.json`) in scadenza si rinnova da sola se tutti i suoi atti sono nel
       corpus, verificati questa settimana, non in movimento e senza modifiche dopo l'ultima verifica della voce;
     * una voce «da ricontrollare» per una modifica gia' provata si richiude da sola quando il corpus la recepisce
       (l'atto modificante compare nel changelog-auto degli atti della voce e nessuno e' piu' in movimento);
     * gli altri casi, il debito scaduto, le voci ALTA della watchlist e le decisioni della Consulta (1ª Serie Speciale
       della G.U.) vanno nel triage per Claude.
  2. Claude (WebSearch, WebFetch) consegna per ogni voce un esito con le PROVE; non scrive nel repo.
  3. Controllo meccanico (`sentinelle_prove.verifica_prova`): si applica solo cio' che ha almeno una prova verificata.
     CONFERMATO → la voce diventa «da ricontrollare» (a runtime: SOSPETTO, il testo si rilegge alla data) con
     `modificata_da`, una voce nuova in coda a `changelog-riforme.md` e una voce di debito; INVARIATO → verifica
     rinnovata; il resto → nessuna modifica, una riga nella issue.
  4. Il drift-report del giro lo scrive lo script, solo con esiti verificati.

Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import datetime as _dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinelle_base as sb  # noqa: E402
import sentinelle_prove as sp  # noqa: E402

REL_META = "wiki-studio/normativa/changelog-riforme.meta.json"
REL_DEBITO = "wiki-studio/normativa/sentinella-debito.json"
REL_CHANGELOG = "wiki-studio/normativa/changelog-riforme.md"
REL_WATCHLIST = "wiki-studio/normativa/vigenza-watchlist.md"
DIR_DRIFT = "wiki-studio/normativa/drift-reports"
#: voci e debiti per giro affidati a Claude (il resto passa al giro dopo: nessuna voce si perde)
MAX_VOCI = 8
MAX_DEBITI = 6
#: anticipo con cui una voce in scadenza entra nel giro
ANTICIPO_GIORNI = 3
CORPUS_FRESCO_GIORNI = 8
#: una voce di debito riaperta si ricontrolla dopo tanti giorni
RINVIO_DEBITO_GIORNI = 7
SEZIONE_AUTO = "## Aggiornamenti verificati dalle sentinelle automatiche"
INTRO_AUTO = ("Voci aggiunte dall'Action «sentinelle» del corpus pubblico: ognuna ha superato il controllo meccanico (fonte "
              "ufficiale riscaricata, estremi e citazione ritrovati). Sono notizie da recepire nelle sezioni sopra: il "
              "sidecar marca le voci toccate «da ricontrollare» finché il corpus non recepisce la modifica.")
GU = "https://www.gazzettaufficiale.it"


# ----------------------------------------------------------------------------------------------- utilità

def _mesi(volatilita: str, meta: dict) -> int:
    regole = (meta.get("_meta") or {}).get("regola_prossima_verifica_mesi") or {}
    return int(regole.get(str(volatilita or "media").lower()) or 12)


def _piu_mesi(d: _dt.date, mesi: int) -> _dt.date:
    m = d.month - 1 + mesi
    anno, mese = d.year + m // 12, m % 12 + 1
    for giorno in (d.day, 30, 29, 28):
        try:
            return _dt.date(anno, mese, giorno)
        except ValueError:
            continue
    return d


def righe_watchlist(testo: str, priorita: str = "ALTA") -> list:
    """Le righe della tabella della watchlist con la priorità data: [{n, testo}]."""
    out = []
    for i, riga in enumerate((testo or "").splitlines(), 1):
        celle = [c.strip() for c in riga.strip().strip("|").split("|")] if riga.startswith("|") else []
        if len(celle) >= 3 and priorita in celle[0]:
            out.append({"n": i, "testo": re.sub(r"\*\*|\*", "", " | ".join(celle[1:]))[:900]})
    return out


def consulta_recenti(gu, giorni: int = 9) -> list:
    """I numeri della 1ª Serie Speciale (Corte costituzionale) degli ultimi giorni, con l'indirizzo del sommario: li legge
    Claude (il sito della Consulta ha il CAPTCHA, la G.U. no)."""
    out = []
    try:
        html = gu.get(f"{GU}/30giorni/corte_costituzionale")
    except Exception:  # noqa: BLE001
        return out
    limite = (sb.oggi() - _dt.timedelta(days=giorni)).isoformat()
    for d, n in re.findall(r"dataPubblicazioneGazzetta=(\d{4}-\d{2}-\d{2})&(?:amp;)?numeroGazzetta=(\d+)", html or ""):
        if d >= limite and not any(x["numero"] == n for x in out):
            out.append({"numero": n, "data": d,
                        "url": f"{GU}/gazzetta/corte_costituzionale/caricaDettaglio?dataPubblicazioneGazzetta={d}&numeroGazzetta={n}"})
    return out


# ----------------------------------------------------------------------------------------------- deterministico

def _atti_ok(atti: list, manifest: dict, righe: list, dal: str, oggi: _dt.date) -> tuple:
    """(tutti invariati?, motivi) per gli atti di una voce."""
    motivi = []
    for slug in atti:
        st = sb.stato_atto(manifest, slug)
        if not st:
            motivi.append(f"{slug} non nel corpus")
            continue
        if str(st.get("verificato_il") or "") < (oggi - _dt.timedelta(days=CORPUS_FRESCO_GIORNI)).isoformat():
            motivi.append(f"{slug} non verificato di recente")
        if st.get("in_movimento"):
            motivi.append(f"{slug} in movimento in G.U.")
        cambi = sb.cambi_dopo(righe, slug, dal)
        if cambi:
            motivi.append(f"{slug} modificato dopo il {dal} (art. {', '.join(sorted({str(c.get('articolo')) for c in cambi})[:6])})")
    return (bool(atti) and not motivi), motivi


def _recepita(voce: dict, atti: list, manifest: dict, righe: list) -> bool:
    """La modifica provata (modificata_da) compare nel changelog-auto degli atti della voce e nessuno e' in movimento."""
    mod = voce.get("modificata_da") or []
    if not mod or not atti or any(sb.stato_atto(manifest, s).get("in_movimento") for s in atti):
        return False
    coppie = set()
    for m in mod:
        coppie |= set(sb._RX_ESTREMI.findall(str(m.get("estremi") or "")))
    if not coppie:
        return False
    for r in righe:
        if r.get("slug") in atti and r.get("tipo") in sb.TIPI_CAMBIO:
            if coppie & set(sb._RX_ESTREMI.findall(str(r.get("atto_modificante") or ""))):
                return True
    return False


def deterministico(radice: Path, giro: sb.Giro, oggi: _dt.date = None, gu=None) -> dict:
    oggi = oggi or sb.oggi()
    radice = Path(radice)
    p_meta = radice / REL_META
    meta = sb.leggi_json(p_meta, {}) or {}
    manifest, righe = sb.manifest_corpus(radice), sb.changelog_auto(radice)
    triage = {"voci": [], "debito": [], "watchlist": [], "consulta": [], "oggi": oggi.isoformat()}
    rinnovate, richiuse = [], []
    candidate = []
    for v in meta.get("voci") or []:
        vid = str(v.get("voce_id") or "")
        atti = sb.slug_da_estremi(v.get("estremi"), radice)
        stato = str(v.get("stato") or "")
        if stato == "da_ricontrollare" and _recepita(v, atti, manifest, righe):
            v["stato"] = "congelato"
            v["verificato_il"] = oggi.isoformat()
            v["prossima_verifica"] = _piu_mesi(oggi, _mesi(v.get("volatilita"), meta)).isoformat()
            v["recepita_il"] = oggi.isoformat()
            richiuse.append(vid)
            continue
        scade = str(v.get("prossima_verifica") or "") <= (oggi + _dt.timedelta(days=ANTICIPO_GIORNI)).isoformat()
        cambiati = any(sb.cambi_dopo(righe, s, v.get("verificato_il")) for s in atti) or \
            any(sb.stato_atto(manifest, s).get("in_movimento") for s in atti)
        if not (scade or stato == "da_ricontrollare" or cambiati):
            continue
        ok, motivi = _atti_ok(atti, manifest, righe, str(v.get("verificato_il") or ""), oggi)
        if ok and stato != "da_ricontrollare":
            v["verificato_il"] = oggi.isoformat()
            v["prossima_verifica"] = _piu_mesi(oggi, _mesi(v.get("volatilita"), meta)).isoformat()
            v["verificato_su"] = (f"sentinelle (Action del corpus), {oggi.isoformat()}: atti {', '.join(atti)} verificati nel corpus, "
                                  "non in movimento, senza modifiche dopo la verifica precedente")
            rinnovate.append(vid)
            continue
        candidate.append((0 if str(v.get("volatilita")) == "alta" else 1, 0 if stato == "da_ricontrollare" else 1,
                          str(v.get("prossima_verifica") or ""),
                          {"voce_id": vid, "estremi": v.get("estremi"), "keywords": v.get("keywords"), "materia": v.get("materia"),
                           "stato": stato, "verificato_il": v.get("verificato_il"), "fonte": v.get("fonte_primaria_url"),
                           "nota": str(v.get("nota") or "")[:600],
                           "motivo": "; ".join(motivi) or ("scaduta" if scade else stato or "atti cambiati")}))
    candidate.sort(key=lambda x: x[:3])
    triage["voci"] = [c[3] for c in candidate[:MAX_VOCI]]
    if len(candidate) > MAX_VOCI:
        giro.riga(f"{len(candidate) - MAX_VOCI} voci del sidecar rinviate al prossimo giro (tetto di {MAX_VOCI} per giro)")
    if rinnovate or richiuse:
        sb.scrivi_json(p_meta, meta)
    if rinnovate:
        giro.riga(f"voci rinnovate senza Claude (atti invariati nel corpus): {', '.join(rinnovate)}")
    if richiuse:
        giro.riga(f"voci richiuse (la modifica e' ora nel corpus): {', '.join(richiuse)}")
    deb = sb.leggi_json(radice / REL_DEBITO, {}) or {}
    scaduti = sorted([d for d in deb.get("debito") or [] if str(d.get("stato")) == "aperto"
                      and str(d.get("scadenza") or "9999") <= oggi.isoformat()], key=lambda d: str(d.get("scadenza")))
    triage["debito"] = [{"id": d.get("id"), "voce_id": d.get("voce_id"), "cosa": d.get("cosa"),
                         "perche": str(d.get("perche") or "")[-1200:], "scadenza": d.get("scadenza")} for d in scaduti[:MAX_DEBITI]]
    try:
        triage["watchlist"] = righe_watchlist((radice / REL_WATCHLIST).read_text(encoding="utf-8"))
    except OSError:
        pass
    if gu is not None:
        triage["consulta"] = consulta_recenti(gu)
    giro.dati["triage_normativa"] = {k: len(v) for k, v in triage.items() if isinstance(v, list)}
    return triage


# ----------------------------------------------------------------------------------------------- dopo Claude

def _prove_ok(esito: dict, get=None) -> tuple:
    prove = [p for p in (esito.get("prove") or []) if isinstance(p, dict)]
    if not prove:
        return False, ["nessuna prova consegnata"], []
    risultati = [sp.verifica_prova(p, get=get) for p in prove]
    buone = [r for r in risultati if r["esito"] == "OK"]
    motivi = [m for r in risultati if r["esito"] != "OK" for m in r["motivi"]]
    return bool(buone), motivi, buone


def _voce_changelog(oggi: _dt.date, estremi: str, sintesi: str, url: str) -> str:
    return f"- **{oggi.strftime('%d/%m/%Y')}** · {estremi or 'atto da identificare'} — {sintesi.strip()} ([fonte ufficiale]({url}))"


def aggiungi_al_changelog(p: Path, righe: list) -> None:
    if not righe:
        return
    testo = p.read_text(encoding="utf-8") if p.exists() else ""
    if SEZIONE_AUTO not in testo:
        testo = testo.rstrip("\n") + "\n\n---\n\n" + SEZIONE_AUTO + "\n\n" + INTRO_AUTO + "\n\n"
    p.write_text(testo.rstrip("\n") + "\n" + "\n".join(righe) + "\n", encoding="utf-8")


def _nuovo_id(deb: dict) -> int:
    return max([int(d.get("id") or 0) for d in deb.get("debito") or [] if str(d.get("id") or "").isdigit()] + [0]) + 1


def dopo_claude(radice: Path, triage: dict, esiti: dict, giro: sb.Giro, oggi: _dt.date = None, get=None) -> dict:
    oggi = oggi or sb.oggi()
    radice = Path(radice)
    esiti = esiti or {}
    fuori = sb.ripristina_fuori_da(radice, lambda rel: False)        # Claude non scrive nel repo: si rimette tutto
    if fuori:
        giro.problema(f"Claude aveva modificato file del repo, rimessi com'erano: {', '.join(fuori[:6])}")
    p_meta, p_deb = radice / REL_META, radice / REL_DEBITO
    meta = sb.leggi_json(p_meta, {}) or {}
    deb = sb.leggi_json(p_deb, {}) or {}
    per_id = {str(v.get("voce_id")): v for v in meta.get("voci") or []}
    debiti = {str(d.get("id")): d for d in deb.get("debito") or []}
    changelog, drift = [], {"confermati": [], "invariati": [], "debito": [], "inconclusi": [], "watchlist": []}
    for t in triage.get("voci") or []:
        vid = str(t.get("voce_id"))
        e = (esiti.get("voci") or {}).get(vid) or {}
        voce = per_id.get(vid)
        tipo = str(e.get("esito") or "").upper()
        ok, motivi, buone = _prove_ok(e, get) if tipo in ("CONFERMATO", "INVARIATO") else (False, [], [])
        if voce is None:
            continue
        if tipo == "CONFERMATO" and ok:
            mod = e.get("modificata_da") or {}
            voce["stato"] = "da_ricontrollare"
            voce.setdefault("modificata_da", []).append({"estremi": mod.get("estremi") or "", "vigente_da": mod.get("vigente_da"),
                                                          "url": buone[0]["url"], "verificato_il": oggi.isoformat()})
            changelog.append(_voce_changelog(oggi, mod.get("estremi") or t.get("estremi") or "", e.get("sintesi") or vid, buone[0]["url"]))
            nid = _nuovo_id(deb)
            deb.setdefault("debito", []).append({
                "id": nid, "voce_id": vid, "cosa": f"Recepire nel changelog umano la modifica di «{vid}»: {str(e.get('sintesi') or '')[:300]}",
                "perche": f"Confermata dalle sentinelle automatiche il {oggi.isoformat()} su {buone[0]['url']}.",
                "aperto_il": oggi.isoformat(), "scadenza": (oggi + _dt.timedelta(days=30)).isoformat(), "stato": "aperto",
                "fonte": "sentinelle"})
            drift["confermati"].append((vid, e.get("sintesi") or "", buone[0]["url"]))
            giro.problema(f"**{vid}**: modifica confermata ({mod.get('estremi') or 'atto'}) — la voce e' «da ricontrollare» "
                          f"finché il corpus non la recepisce; debito #{nid} per recepirla nel changelog umano", vid)
        elif tipo == "INVARIATO" and ok:
            voce["stato"] = "congelato" if voce.get("stato") == "da_ricontrollare" and not voce.get("modificata_da") else voce.get("stato")
            voce["verificato_il"] = oggi.isoformat()
            voce["prossima_verifica"] = _piu_mesi(oggi, _mesi(voce.get("volatilita"), meta)).isoformat()
            voce["verificato_su"] = f"sentinelle (Action del corpus), {oggi.isoformat()}: {str(e.get('sintesi') or '')[:300]} ({buone[0]['url']})"
            drift["invariati"].append((vid, e.get("sintesi") or "", buone[0]["url"]))
        else:
            motivo = "; ".join(motivi) if motivi else (f"esito {tipo or 'mancante'}")
            drift["inconclusi"].append((vid, motivo))
            giro.problema(f"**{vid}**: non verificata ({motivo[:300]})", vid if voce.get("stato") == "da_ricontrollare" else "")
    for t in triage.get("debito") or []:
        did = str(t.get("id"))
        d = debiti.get(did)
        e = (esiti.get("debito") or {}).get(did) or {}
        tipo = str(e.get("esito") or "").upper()
        if d is None:
            continue
        ok, motivi, buone = _prove_ok(e, get) if tipo in ("RISOLTO", "ANCORA_APERTO") else (False, [], [])
        nota = f"{oggi.strftime('%d/%m/%Y')} - sentinelle automatiche: "
        if tipo == "RISOLTO" and ok:
            d["stato"], d["chiuso_il"] = "chiuso", oggi.isoformat()
            d["esito"] = f"{str(e.get('sintesi') or '')[:400]} ({buone[0]['url']})"
            drift["debito"].append((did, "chiuso", e.get("sintesi") or "", buone[0]["url"]))
        elif tipo == "ANCORA_APERTO" and ok:
            d["perche"] = (str(d.get("perche") or "") + " | " + nota + str(e.get("sintesi") or "")[:400] + f" ({buone[0]['url']})").strip(" |")
            d["scadenza"] = (oggi + _dt.timedelta(days=RINVIO_DEBITO_GIORNI)).isoformat()
            drift["debito"].append((did, "ancora aperto", e.get("sintesi") or "", buone[0]["url"]))
        else:
            d["perche"] = (str(d.get("perche") or "") + " | " + nota + "esito non verificato").strip(" |")
            d["scadenza"] = (oggi + _dt.timedelta(days=RINVIO_DEBITO_GIORNI)).isoformat()
            giro.problema(f"debito #{did}: non verificato ({'; '.join(motivi)[:300] if motivi else 'esito ' + (tipo or 'mancante')})")
    for e in (esiti.get("watchlist") or []) + (esiti.get("nuove") or []):
        if str(e.get("esito") or "CONFERMATO").upper() != "CONFERMATO":
            continue
        ok, motivi, buone = _prove_ok(e, get)
        if ok:
            changelog.append(_voce_changelog(oggi, e.get("estremi") or "", e.get("sintesi") or e.get("titolo") or "", buone[0]["url"]))
            drift["watchlist"].append((e.get("estremi") or e.get("titolo") or "", e.get("sintesi") or "", buone[0]["url"]))
            giro.problema(f"novità confermata: {e.get('estremi') or e.get('titolo') or ''} — {str(e.get('sintesi') or '')[:200]}")
        else:
            giro.problema(f"novità segnalata ma non provata: {str(e.get('estremi') or e.get('titolo') or '')[:120]} ({'; '.join(motivi)[:200]})")
    if changelog:
        aggiungi_al_changelog(radice / REL_CHANGELOG, changelog)
    sb.scrivi_json(p_meta, meta)
    sb.scrivi_json(p_deb, deb)
    giro.da_ricontrollare = sorted({str(v.get("voce_id")) for v in meta.get("voci") or [] if v.get("stato") == "da_ricontrollare"}
                                   | set(giro.da_ricontrollare))
    scrivi_drift_report(radice, triage, drift, oggi)
    giro.riga(f"confermate {len(drift['confermati'])} · invariate {len(drift['invariati'])} · debito {len(drift['debito'])} · "
              f"non verificate {len(drift['inconclusi'])} · novità {len(drift['watchlist'])}")
    return drift


def scrivi_drift_report(radice: Path, triage: dict, drift: dict, oggi: _dt.date) -> Path:
    import corpus_diff as cd
    r = [f"# Drift-report delle sentinelle automatiche — {oggi.isoformat()}", "",
         "**Giro:** GitHub Action «sentinelle» del corpus pubblico · solo esiti con prova verificata dallo script "
         "(fonte ufficiale riscaricata, estremi e citazione ritrovati).", ""]
    n = sum(len(v) for v in drift.values())
    r.append(f"**In sintesi:** {len(drift['confermati'])} modifiche confermate, {len(drift['watchlist'])} novità, "
             f"{len(drift['invariati'])} voci riverificate, {len(drift['inconclusi'])} non verificate." if n else
             "**In sintesi:** nessun esito da registrare in questo giro.")
    r.append("")
    for titolo, chiave in (("Modifiche confermate", "confermati"), ("Novità confermate (watchlist e atti nuovi)", "watchlist"),
                           ("Voci riverificate", "invariati")):
        if drift[chiave]:
            r += [f"## {titolo}", ""] + [f"- **{a}** — {b} ([fonte]({c}))" for a, b, c in drift[chiave]] + [""]
    if drift["debito"]:
        r += ["## Debito di verifica", ""] + [f"- **#{a}** {b} — {c} ([fonte]({d}))" for a, b, c, d in drift["debito"]] + [""]
    if drift["inconclusi"]:
        r += ["## Non verificate (restano com'erano, nella issue del giro)", ""] + [f"- **{a}** — {b}" for a, b in drift["inconclusi"]] + [""]
    righe = sb.changelog_auto(radice)
    r.append(cd.drift_report_sezione(dal=(oggi - _dt.timedelta(days=8)).isoformat(), righe=righe))
    p = Path(radice) / DIR_DRIFT / f"{oggi.isoformat()}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(r).rstrip("\n") + "\n", encoding="utf-8")
    return p
