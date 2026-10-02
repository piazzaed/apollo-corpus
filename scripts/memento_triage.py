#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IL TRIAGE DEL MEMENTO LAVORO (v0.36): quali schede vanno riviste, quali create, quali numeri annuali aggiornati.

Una scheda si rivede quando:
  - il testo di una norma che dichiara non e' piu' quello sigillato (impronta diversa): la scheda diventa subito
    «da ricontrollare», anche se poi il passo del modello non parte;
  - il changelog del corpus registra una modifica di un suo articolo, o la Gazzetta lo mette «in movimento»;
  - nell'indice della prassi e' comparso un documento il cui oggetto contiene una sua parola chiave;
  - e' gia' «da ricontrollare», o la richiede chi ha scritto wiki-studio/lavoro/richiesta.json (o l'input del
    workflow).
Un numero annuale si aggiorna quando esce prassi che lo riguarda (`watch`) o quando manca il valore dell'anno.

Scrive il file di triage per il passo del modello e, con --github-output, `lavoro=true|false`.

Uso:
  python3 scripts/memento_triage.py --triage T.json [--schede "a b"] [--crea "c d"] [--github-output F] [--report F]
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import datetime as _dt
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
import memento_verifica as mv  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TIPI_CHANGELOG = ("modificato", "abrogato", "rimosso", "aggiunto")
#: i valori annuali escono di solito entro febbraio: da marzo, un anno senza valore e' da cercare
MESE_ATTESA_NUMERI = 3
MAX_MOTIVI = 6


def _l(p: Path, default=None):
    return mv._leggi_json(p, default)


def triage(radice: Path = ROOT, schede_richieste=(), crea_richieste=(), oggi: str = "") -> dict:
    radice = Path(radice)
    oggi = oggi or _dt.date.today().isoformat()
    area = mv.area_lavoro(radice)
    stato = _l(area / "stato.json", {}) or {}
    ultimo = str(stato.get("ultimo_triage") or "0000-00-00")
    visti_mov = set(stato.get("movimento_visti") or [])
    richiesta = _l(area / "richiesta.json", {}) or {}
    schede_richieste = list(schede_richieste) + list(richiesta.get("schede") or [])
    crea_richieste = list(crea_richieste) + list(richiesta.get("crea") or [])
    changelog = [r for r in ((_l(radice / "wiki-studio" / "normativa" / "changelog-auto.json", {}) or {}).get("modifiche") or [])
                 if r.get("tipo") in TIPI_CHANGELOG and str(r.get("registrato_il") or "") >= ultimo]
    manifest = _l(radice / "manifest.json", {}) or {}
    movimento = {s: v.get("articoli_in_movimento") or [] for s, v in (manifest.get("atti") or {}).items() if v.get("in_movimento")}
    prassi = (_l(area / "prassi" / "indice.json", {}) or {}).get("voci") or {}
    prassi_nuove = [(k, v) for k, v in prassi.items() if str(v.get("visto_il") or "") > ultimo]
    out = {"data": oggi, "schede": {}, "crea": [], "numeri": [], "richiesta": bool(richiesta.get("schede") or richiesta.get("crea")),
           "marcate": []}

    def motivo(sid, testo):
        lst = out["schede"].setdefault(sid, [])
        if testo not in lst and len(lst) < MAX_MOTIVI:
            lst.append(testo)

    cache = {}
    nuovi_mov = set()
    for p in sorted((area / "memento").glob("*.md")) if (area / "memento").is_dir() else []:
        try:
            h = mv.leggi_scheda(p)["intestazione"]
        except (OSError, UnicodeDecodeError):
            continue
        sid = p.stem
        norme = [str(x) for x in h.get("norme") or []]
        impronte = h.get("impronte") or {}
        cambiate = []
        for chiave in norme:
            if chiave not in cache:
                cache[chiave] = mv.norma(chiave)
            n = cache[chiave]
            if n["esito"] != "OK":
                cambiate.append(f"{chiave}: {n['esito']}")
            elif n["abrogato"]:
                cambiate.append(f"{chiave}: abrogato")
            elif h.get("stato") == "verificata" and impronte.get(chiave) and impronte[chiave] != n["impronta"]:
                cambiate.append(f"{chiave}: testo cambiato")
        for c in cambiate:
            motivo(sid, f"norma {c}")
        if cambiate and h.get("stato") == "verificata":
            mv.marca(p, [f"norma {c} (triage del {oggi})" for c in cambiate])
            out["marcate"].append(sid)
        for r in changelog:
            if f"{r.get('slug')}:{r.get('articolo')}" in norme:
                motivo(sid, f"changelog: art. {r.get('articolo')} {r.get('slug')} {r.get('tipo')}"
                            + (f" da {r['atto_modificante']}" if r.get("atto_modificante") else ""))
        for chiave in norme:
            slug, _, art = chiave.partition(":")
            arts = movimento.get(slug) or []
            if arts and ("*" in arts or art in arts) and chiave not in visti_mov:
                motivo(sid, f"in movimento in Gazzetta Ufficiale: {chiave}")
                nuovi_mov.add(chiave)
        chiavi = [mv._piano(k) for k in (h.get("parole_chiave") or []) if len(mv._piano(k)) >= 4]
        for k, v in prassi_nuove:
            t = mv._piano(v.get("titolo"))
            if any(c in t for c in chiavi):
                motivo(sid, f"prassi nuova {k}: {str(v.get('titolo'))[:140]}")
        if h.get("stato") in ("da_ricontrollare", "bozza"):
            for m in (h.get("motivi") or ["da ricontrollare"])[:3]:
                motivo(sid, str(m))
        if sid in schede_richieste:
            motivo(sid, "rilettura richiesta")
    elenco = (_l(area / "memento" / "elenco.json", {}) or {}).get("schede") or {}
    for sid in crea_richieste:
        if not (area / "memento" / f"{sid}.md").exists():
            out["crea"].append({"id": sid, **(elenco.get(sid) or {})})
    dati = (_l(area / "dati" / "dati-lavoro.json", {}) or {}).get("voci") or {}
    anno = oggi[:4]
    for k, v in dati.items():
        if v.get("derivata"):
            continue
        m = []
        watch = [mv._piano(w) for w in v.get("watch") or [] if w]
        for pid, pv in prassi_nuove:
            t = mv._piano(pv.get("titolo"))
            if watch and all(w in t for w in watch):          # watch: parole che devono comparire TUTTE
                m.append(f"prassi nuova {pid}: {str(pv.get('titolo'))[:120]}")
        if anno not in (v.get("serie") or {}) and int(oggi[5:7]) >= MESE_ATTESA_NUMERI:
            m.append(f"manca il valore {anno}")
        if m:
            out["numeri"].append({"chiave": k, "descrizione": v.get("descrizione"), "motivi": m[:4]})
    stato.update(ultimo_triage=oggi, movimento_visti=sorted(visti_mov | nuovi_mov))
    stato.setdefault("_meta", {})["ultimo_triage"] = oggi
    (area / "stato.json").parent.mkdir(parents=True, exist_ok=True)
    (area / "stato.json").write_text(json.dumps(stato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    out["lavoro"] = bool(out["schede"] or out["crea"] or out["numeri"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Triage del memento lavoro.")
    ap.add_argument("--triage", required=True, help="dove scrivere il file di triage")
    ap.add_argument("--schede", default="")
    ap.add_argument("--crea", default="")
    ap.add_argument("--github-output", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--radice", default=str(ROOT))
    a = ap.parse_args(argv)
    t = triage(Path(a.radice), a.schede.split(), a.crea.split())
    Path(a.triage).write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    testo = ("### Triage del memento\n\n" + f"- schede da rivedere: {len(t['schede'])}"
             + (f" ({', '.join(sorted(t['schede'])[:20])})" if t["schede"] else "") + "\n"
             + f"- schede da creare: {len(t['crea'])}\n- numeri annuali: {len(t['numeri'])}"
             + (f" ({', '.join(n['chiave'] for n in t['numeri'])})" if t["numeri"] else "") + "\n"
             + (f"- marcate «da ricontrollare» (norma cambiata): {', '.join(t['marcate'])}\n" if t["marcate"] else ""))
    print(testo)
    if a.report:
        with open(a.report, "a", encoding="utf-8") as f:
            f.write(testo + "\n")
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as f:
            f.write(f"lavoro={'true' if t['lavoro'] else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
