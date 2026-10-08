"""Freshness checker DETERMINISTICO del ground truth normativo (Fase 2).

Risponde a DUE domande, distinte (vedi wiki-studio/protocolli/datazione-verifica.md):
  1) FRESCHEZZA: "la voce del nostro changelog e' ancora valida OGGI?" (verdetto FRESCO/SCADUTO/SOSPETTO)
  2) COPERTURA DATATA: dato --data-evento, "la voce congelata copre quella data del caso?"
     (se NO -> il congelato non basta, serve verifica datata su normattiva: e' il gancio del Potenziamento B)

Solo stdlib (Python 3.7+). Nessuna dipendenza esterna. Legge il sidecar
wiki-studio/normativa/changelog-riforme.meta.json e (per --check-coerenza) il changelog-riforme.md.

Esempi:
  python3 scripts/freshness.py --materie parametri_forensi
  python3 scripts/freshness.py --materie processo_civile --oggi 2028-01-01
  python3 scripts/freshness.py --materie processo_civile --data-evento 2021-05-01   # caso pre-Cartabia
  python3 scripts/freshness.py --check-coerenza
  python3 scripts/freshness.py --json
"""
from __future__ import annotations
import argparse, json, sys
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8 (accenti, frecce, emoji)
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import WIKI  # noqa: E402

SIDECAR = WIKI / "normativa" / "changelog-riforme.meta.json"
CHANGELOG_MD = WIKI / "normativa" / "changelog-riforme.md"
MODELLI_SIDECAR = WIKI / "modelli" / "modelli.meta.json"


def _load_sidecar(path: Path = SIDECAR) -> dict:
    """Legge il sidecar nella sua versione VIVA (v0.16).

    Le marcature `stato: da_ricontrollare` della Sentinella sono il debito di verifica del
    plugin: se le si leggesse solo dal file spedito col bundle, ogni reinstallazione le
    azzererebbe e il freshness tornerebbe a dire FRESCO su voci che la Sentinella aveva già
    segnalato. Il corpus vivo tiene quelle patch fuori dal pacchetto; qui le si rilegge.
    Se il corpus non è disponibile (o non ha patch), si legge il file com'è: comportamento
    identico alla v0.15.
    """
    if path == SIDECAR:
        try:
            import corpus as _cp
            return json.loads(_cp.risolvi("normativa/changelog-riforme.meta.json"))
        except Exception:
            pass
    if not path.exists():
        raise SystemExit(f"[freshness] sidecar non trovato: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _d(s):
    """Parsa una data ISO o None."""
    if not s:
        return None
    return date.fromisoformat(s)


def _match_materia(voce: dict, needles: list[str]) -> bool:
    """True se una delle materie richieste compare in materia/voce_id/keywords (case-insensitive, substring)."""
    if not needles:
        return True
    hay = " ".join([
        str(voce.get("materia", "")),
        str(voce.get("voce_id", "")),
        " ".join(voce.get("keywords", [])),
    ]).lower()
    return any(n.strip().lower() in hay for n in needles if n.strip())


def freschezza(voce: dict, oggi: date) -> dict:
    """Verdetto di freschezza della voce a 'oggi'."""
    stato = voce.get("stato", "congelato")
    prossima = _d(voce.get("prossima_verifica"))
    if stato == "da_ricontrollare":
        verdetto = "SOSPETTO"
        motivo = "la Sentinella ha marcato la voce 'da_ricontrollare'"
    elif prossima is None:
        verdetto = "FRESCO"
        motivo = "nessuna scadenza di verifica impostata"
    elif oggi > prossima:
        verdetto = "SCADUTO"
        motivo = f"prossima_verifica {prossima.isoformat()} < oggi {oggi.isoformat()}"
    else:
        verdetto = "FRESCO"
        motivo = f"verificata, prossima_verifica {prossima.isoformat()}"
    return {"verdetto": verdetto, "motivo": motivo}


def copre_data_evento(voce: dict, data_evento: date) -> dict:
    """Il congelato copre la data-evento del caso? (intervallo di vigenza)"""
    da = _d(voce.get("vigente_da"))
    a = _d(voce.get("vigente_a"))
    dentro = (da is None or data_evento >= da) and (a is None or data_evento <= a)
    if dentro:
        return {"copre": True, "nota": "data-evento dentro l'intervallo di vigenza: il congelato e' utilizzabile"}
    return {
        "copre": False,
        "nota": (
            f"data-evento {data_evento.isoformat()} FUORI dall'intervallo "
            f"[{voce.get('vigente_da')} -> {voce.get('vigente_a') or 'in vigore'}]: "
            "il congelato NON basta, verifica datata su normattiva (Potenziamento B)"
        ),
    }


def valuta(materie, oggi, data_evento, sidecar=None):
    sidecar = sidecar or _load_sidecar()
    out = []
    for voce in sidecar.get("voci", []):
        if not _match_materia(voce, materie):
            continue
        rec = {
            "voce_id": voce.get("voce_id"),
            "materia": voce.get("materia"),
            "estremi": voce.get("estremi"),
            "volatilita": voce.get("volatilita"),
            "fonte_primaria_url": voce.get("fonte_primaria_url"),
            **freschezza(voce, oggi),
        }
        if data_evento is not None:
            rec["copertura_datata"] = copre_data_evento(voce, data_evento)
        out.append(rec)
    return out


def _load_modelli_sidecar() -> dict:
    """Il sidecar dei modelli nella versione VIVA (v0.29): le marcature `da_ricontrollare` della sentinella dei
    modelli e le chiusure `--allinea` vivono nel corpus vivo (`corpus.py --patch-json`), non nel bundle. Leggere il
    file del pacchetto le renderebbe invisibili (era il bug della v0.28). Senza corpus: il file com'e'."""
    try:
        import corpus as _cp
        return json.loads(_cp.risolvi("modelli/modelli.meta.json"))
    except (Exception, SystemExit):
        pass
    return json.loads(MODELLI_SIDECAR.read_text(encoding="utf-8")) if MODELLI_SIDECAR.exists() else {"modelli": []}


def _verdetti_sentinella() -> dict:
    """{id: {verdetto, motivi, giro}} dall'ultimo giro della sentinella dei modelli (vuoto se mai girata)."""
    try:
        import sentinella_modelli as _sm
        return _sm.verdetti_modelli()
    except Exception:
        return {}


def valuta_modelli(oggi, mod_sidecar=None, chg_sidecar=None, sentinella=None):
    """Freschezza dei MODELLI di atto, DERIVATA dalle voci del changelog in changelog_deps
    (piu la propria prossima_verifica). Un modello e SCADUTO/SOSPETTO se lo e una sua
    dipendenza changelog, se e passata la sua prossima_verifica o se e marcato `da_ricontrollare`
    (sentinella dei modelli, sviluppo, avvocato). Il sidecar si legge VIVO (corpus.risolvi).
    Ogni record porta anche il verdetto sul TESTO dell'ultimo giro della sentinella (`sentinella`)."""
    if mod_sidecar is None:
        mod_sidecar = _load_modelli_sidecar()
    chg = chg_sidecar or _load_sidecar()
    sent = _verdetti_sentinella() if sentinella is None else sentinella
    verdetto_voce = {v.get("voce_id"): freschezza(v, oggi)["verdetto"] for v in chg.get("voci", [])}
    rank = {"FRESCO": 0, "SOSPETTO": 1, "SCADUTO": 2, "IGNOTO": 2}
    out = []
    for m in mod_sidecar.get("modelli", []):
        deps = m.get("changelog_deps", [])
        dep_verdetti = {d: verdetto_voce.get(d, "IGNOTO") for d in deps}
        prossima = _d(m.get("prossima_verifica"))
        dr = m.get("da_ricontrollare")
        if m.get("stato") == "da_ricontrollare" or dr:
            proprio = "SOSPETTO"
        elif prossima and oggi > prossima:
            proprio = "SCADUTO"
        else:
            proprio = "FRESCO"
        peggiore = proprio
        if proprio == "SOSPETTO":
            motivo = dr.get("motivo") if isinstance(dr, dict) else (dr if isinstance(dr, str) else "")
            causa = "da_ricontrollare" + (f": {str(motivo)[:160]}" if motivo else "")
        else:
            causa = "propria_scadenza" if proprio != "FRESCO" else "-"
        for d, v in dep_verdetti.items():
            if rank.get(v, 2) > rank.get(peggiore, 0):
                peggiore, causa = v, "dep:" + d
        rec = {"id": m.get("id"), "titolo": m.get("titolo"), "verdetto": peggiore,
               "causa": causa, "changelog_deps": dep_verdetti, "file": m.get("file"),
               "giurisprudenza_stato": m.get("giurisprudenza_stato")}
        if isinstance(dr, dict):
            rec["da_ricontrollare"] = dr
        s = sent.get(str(m.get("id"))) if isinstance(sent, dict) else None
        if s:
            rec["sentinella"] = {"verdetto": s.get("verdetto"), "motivi": (s.get("motivi") or [])[:3], "giro": s.get("giro")}
        out.append(rec)
    return out


def congelato_first(voce_id, riferimento, data_evento, oggi, sidecar=None):
    """Decide se una claim su NORMA puo' usare il ground truth CONGELATO (niente fetch live) o deve
    andare LIVE. USABILE_CONGELATO sse: la norma e' coperta da una voce del changelog FRESCA e la
    data-evento cade dentro l'intervallo di vigenza. Altrimenti VAI_LIVE. Vedi nucleo §3-ter."""
    sc = sidecar or _load_sidecar()
    voce = None
    if voce_id:
        voce = next((v for v in sc.get("voci", []) if v.get("voce_id") == voce_id), None)
    if voce is None and riferimento:
        rr = riferimento.lower()
        for v in sc.get("voci", []):
            estremi = str(v.get("estremi", "")).lower()
            kws = [k.lower() for k in v.get("keywords", [])]
            if (estremi and estremi in rr) or any(k and k in rr for k in kws):
                voce = v; break
    if voce is None:
        return {"decisione": "VAI_LIVE", "motivo": "norma non coperta dal changelog"}
    fr = freschezza(voce, oggi)["verdetto"]
    if fr != "FRESCO":
        return {"decisione": "VAI_LIVE", "voce": voce.get("voce_id"), "motivo": f"voce {fr}"}
    if data_evento is not None:
        cd = copre_data_evento(voce, data_evento)
        if not cd["copre"]:
            return {"decisione": "VAI_LIVE", "voce": voce.get("voce_id"), "motivo": "data-evento fuori vigenza"}
    return {"decisione": "USABILE_CONGELATO", "voce": voce.get("voce_id"),
            "verificato_il": voce.get("verificato_il"), "motivo": "voce fresca e in vigenza"}


def check_coerenza(sidecar=None) -> list[dict]:
    """Ogni voce del sidecar trova i propri 'estremi' nel changelog-riforme.md? (anti-divergenza)"""
    sidecar = sidecar or _load_sidecar()
    md = CHANGELOG_MD.read_text(encoding="utf-8") if CHANGELOG_MD.exists() else ""
    res = []
    for voce in sidecar.get("voci", []):
        estremi = str(voce.get("estremi", ""))
        ok = bool(estremi) and estremi in md
        res.append({"voce_id": voce.get("voce_id"), "estremi": estremi, "presente_nel_md": ok})
    return res


def _print_human(records, data_evento):
    icon = {"FRESCO": "✓", "SCADUTO": "✗", "SOSPETTO": "⚠"}
    for r in records:
        print(f"{icon.get(r['verdetto'], '?')} {r['verdetto']:8} {r['voce_id']:32} [{r['volatilita']}] — {r['motivo']}")
        if r["verdetto"] in ("SCADUTO", "SOSPETTO"):
            print(f"    → riverifica su: {r['fonte_primaria_url']}")
        if data_evento is not None and "copertura_datata" in r:
            cd = r["copertura_datata"]
            mark = "✓" if cd["copre"] else "✗"
            print(f"    {mark} copertura data-evento: {cd['nota']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Freshness checker del ground truth normativo (Fase 2).")
    ap.add_argument("--materie", default="", help="materie separate da virgola (vuoto = tutte)")
    ap.add_argument("--oggi", default=None, help="data odierna ISO YYYY-MM-DD (override per test)")
    ap.add_argument("--data-evento", default=None, help="data del caso ISO per la copertura datata (Potenziamento B)")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--check-coerenza", action="store_true", help="verifica che ogni voce del sidecar sia nel changelog-riforme.md")
    ap.add_argument("--modelli", action="store_true", help="freschezza dei MODELLI di atto (derivata dalle changelog_deps)")
    ap.add_argument("--congelato-first", action="store_true", help="decidi se una claim NORMA usa il congelato o va live")
    ap.add_argument("--voce", default=None, help="voce_id del changelog (per --congelato-first)")
    ap.add_argument("--riferimento", default=None, help="riferimento norma (match per keyword/estremi)")
    args = ap.parse_args(argv)

    if args.check_coerenza:
        res = check_coerenza()
        mancanti = [r for r in res if not r["presente_nel_md"]]
        if args.json:
            print(json.dumps({"coerenza": res, "mancanti": len(mancanti)}, ensure_ascii=False, indent=2))
        else:
            for r in res:
                print(("✓" if r["presente_nel_md"] else "✗"), r["voce_id"], "—", r["estremi"])
            print(f"\nVoci non trovate nel changelog .md: {len(mancanti)}")
        return 1 if mancanti else 0

    oggi = _d(args.oggi) if args.oggi else date.today()

    if args.modelli:
        recs = valuta_modelli(oggi)
        scaduti = [r for r in recs if r["verdetto"] != "FRESCO"]
        if args.json:
            print(json.dumps({"oggi": oggi.isoformat(), "totale": len(recs),
                              "da_rivedere": len(scaduti), "modelli": recs}, ensure_ascii=False, indent=2))
        else:
            icon = {"FRESCO": "✓", "SCADUTO": "✗", "SOSPETTO": "⚠", "IGNOTO": "?"}
            print("Freschezza MODELLI al " + oggi.isoformat() + " - " + str(len(recs)) + " modelli, " + str(len(scaduti)) + " da rivedere:")
            if not scaduti:
                print("  " + icon["FRESCO"] + " tutti i modelli FRESCHI (dipendenze changelog congelate).")
            for r in scaduti:
                print("  " + icon.get(r["verdetto"], "?") + " " + r["verdetto"] + "  " + str(r["id"]) + "  " + str(r["titolo"])[:44] + "  - causa: " + str(r["causa"])[:200])
            sent = [r for r in recs if (r.get("sentinella") or {}).get("verdetto") in ("ROSSO", "GIALLO")]
            if sent:
                rossi = sum(1 for r in sent if r["sentinella"]["verdetto"] == "ROSSO")
                print(f"Sentinella modelli (testo, giro {sent[0]['sentinella'].get('giro')}): {rossi} rossi, {len(sent) - rossi} gialli"
                      " — dettaglio: python3 scripts/sentinella_modelli.py --stato")
        return 0 if not scaduti else 2

    if getattr(args, "congelato_first", False):
        de = _d(args.data_evento) if args.data_evento else None
        res = congelato_first(args.voce, args.riferimento, de, oggi)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(res["decisione"] + " - " + res.get("motivo", "") + (" (voce: " + res["voce"] + ")" if res.get("voce") else ""))
        return 0 if res["decisione"] == "USABILE_CONGELATO" else 2
    data_evento = _d(args.data_evento) if args.data_evento else None
    materie = [m for m in args.materie.split(",") if m.strip()] if args.materie else []
    records = valuta(materie, oggi, data_evento)

    if args.json:
        print(json.dumps({"oggi": oggi.isoformat(), "records": records}, ensure_ascii=False, indent=2))
    else:
        if not records:
            print(f"[freshness] nessuna voce per materie={materie or 'tutte'}")
        else:
            print(f"Freschezza al {oggi.isoformat()}" + (f" · data-evento {data_evento.isoformat()}" if data_evento else "") + ":")
            _print_human(records, data_evento)
    # exit code: 0 se tutto FRESCO, 2 se almeno una SCADUTA/SOSPETTA (utile per la skill)
    return 0 if all(r["verdetto"] == "FRESCO" for r in records) else 2


if __name__ == "__main__":
    raise SystemExit(main())
