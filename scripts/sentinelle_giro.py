#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IL GIRO DELLE SENTINELLE AUTOMATICHE (v0.36): una fase per volta, un'area per volta, come la chiama l'Action.

    python3 scripts/sentinelle_giro.py --area dati --fase deterministica --triage T.json --github-output $GITHUB_OUTPUT \
        --report R.md
    python3 scripts/sentinelle_giro.py --area dati --fase dopo-claude --triage T.json --esiti E.json --claude-ok true \
        --issue I.md --github-output $GITHUB_OUTPUT --report R.md

Fase deterministica: i passi senza Claude dell'area (che possono gia' scrivere file controllati: tassi, rinnovi, giro
dei modelli) e il triage; con --github-output scrive `claude=true|false`.
Fase dopo-claude: il controllo meccanico (si applica solo cio' che ha una prova verificata), lo stato del giro in
`wiki-studio/sentinelle/stato.json`, la issue. Se il controllo va in errore, i file dell'area tornano com'erano: mai
pubblicare cio' che non si e' controllato.
Il resoconto della fase deterministica passa alla seconda in `<triage>.giro.json`.

Dal Mac (senza Action, senza Claude): `python3 scripts/sentinelle_pubblica.py --giro <area> --repo <clone>`.
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aree  # noqa: E402
import sentinelle_base as sb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
AREE_GIRO = ("dati", "normativa", "successioni", "modelli")


def _modulo(area: str):
    import importlib
    return importlib.import_module(f"sentinelle_{area}")


def _salva_giro(path: Path, giro: sb.Giro) -> None:
    path.write_text(json.dumps({"area": giro.area, "rapporto": giro.rapporto, "issue": giro.issue, "esito": giro.esito,
                                "da_ricontrollare": giro.da_ricontrollare, "dati": giro.dati}, ensure_ascii=False, indent=1),
                    encoding="utf-8")


def _carica_giro(path: Path, area: str) -> sb.Giro:
    g = sb.Giro(area)
    d = sb.leggi_json(path, {}) or {}
    g.rapporto, g.issue = list(d.get("rapporto") or []), list(d.get("issue") or [])
    g.esito, g.da_ricontrollare, g.dati = d.get("esito") or "ok", list(d.get("da_ricontrollare") or []), dict(d.get("dati") or {})
    return g


def ripristina_area(radice: Path, area: str) -> list:
    """Rimette com'erano (rispetto all'ultimo commit) i file dell'Action di un'area."""
    out = []
    for st, rel in sb.toccati(radice):
        c = aree.classifica(rel)
        if c and c[0] in (area, "stato"):
            sb.ripristina(radice, st, rel)
            out.append(rel)
    return out


def fase_deterministica(radice: Path, area: str, gu=None) -> tuple:
    giro = sb.Giro(area)
    mod = _modulo(area)
    if area == "modelli":
        triage = mod.deterministico(radice, giro)
    else:
        if gu is None:
            import sentinelle_dati as sd
            gu = sd.Gazzetta()
        triage = mod.deterministico(radice, giro, gu=gu)
    return giro, triage or {}


def fase_dopo_claude(radice: Path, area: str, giro: sb.Giro, triage: dict, esiti: dict, claude_ok: bool) -> sb.Giro:
    mod = _modulo(area)
    try:
        if area == "successioni":
            mod.dopo_claude(radice, triage, esiti, giro, claude_ok=claude_ok)
        elif triage:
            if not claude_ok:
                giro.parziale()
                giro.problema("il passo Claude non è riuscito (token scaduto o quota esaurita?): le voci del triage restano "
                              "com'erano e si ricontrollano al prossimo giro")
            mod.dopo_claude(radice, triage, esiti if claude_ok else {}, giro)
        sb.aggiorna_stato(radice, giro)
    except Exception as e:  # noqa: BLE001
        rimessi = ripristina_area(radice, area)
        giro.parziale()
        giro.problema(f"controllo meccanico interrotto ({e.__class__.__name__}: {str(e)[:200]}): nulla pubblicato per l'area "
                      f"{area} ({len(rimessi)} file rimessi com'erano)")
        try:
            sb.aggiorna_stato(radice, giro)
        except Exception:  # noqa: BLE001
            pass
    return giro


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Una fase del giro delle sentinelle automatiche, per un'area.")
    ap.add_argument("--area", choices=AREE_GIRO, required=True)
    ap.add_argument("--fase", choices=("deterministica", "dopo-claude"), required=True)
    ap.add_argument("--radice", default=str(ROOT))
    ap.add_argument("--triage", required=True)
    ap.add_argument("--esiti", default="")
    ap.add_argument("--claude-ok", default="true")
    ap.add_argument("--issue", default="")
    ap.add_argument("--github-output", default="")
    ap.add_argument("--report", default="")
    a = ap.parse_args(argv)
    radice = Path(a.radice)
    p_triage = Path(a.triage)
    p_giro = p_triage.with_suffix(".giro.json")
    if a.fase == "deterministica":
        try:
            giro, triage = fase_deterministica(radice, a.area)
        except Exception as e:  # noqa: BLE001
            giro, triage = sb.Giro(a.area), {}
            rimessi = ripristina_area(radice, a.area)
            giro.parziale()
            giro.problema(f"fase deterministica interrotta ({e.__class__.__name__}: {str(e)[:200]}): {len(rimessi)} file rimessi com'erano")
        p_triage.write_text(json.dumps(triage, ensure_ascii=False, indent=1), encoding="utf-8")
        _salva_giro(p_giro, giro)
        sb.github_output(a.github_output, claude="true" if triage else "false")
        print(f"{a.area}: triage {'per Claude' if triage else 'vuoto'} · " + " · ".join(giro.rapporto[-3:]))
        return 0
    giro = _carica_giro(p_giro, a.area)
    triage = sb.leggi_json(p_triage, {}) or {}
    esiti = sb.leggi_json(Path(a.esiti), {}) if a.esiti else {}
    giro = fase_dopo_claude(radice, a.area, giro, triage, esiti or {}, str(a.claude_ok).lower() == "true")
    sb.scrivi_rapporto(giro, a.report)
    n = sb.scrivi_issue([giro], a.issue) if a.issue else len(giro.issue)
    sb.github_output(a.github_output, problemi=str(n), esito=giro.esito)
    print(giro.markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
