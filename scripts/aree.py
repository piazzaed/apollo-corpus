#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LE AREE DELLE SENTINELLE (v0.36): quali file aggiorna da sola la GitHub Action «sentinelle» del corpus pubblico e
quale copia si legge, quella del pacchetto o quella sincronizzata.

PERCHE'
-------
Il lavoro delle sentinelle (riforme della watchlist, modelli d'atto, successioni, tassi e tabelle datate) gira ogni
settimana nel repo pubblico del corpus, non piu' in attivita' programmate. I file che l'Action scrive arrivano al plugin
col sync del corpus (`corpus_sync.py`), in `<stato>/aree/`, allo stesso percorso relativo che hanno nel plugin e nel
repo: cosi' gli stessi script girano tali e quali nell'Action e nel plugin.

Due tipi di file per area:
  * «action»: li scrive SOLO l'Action (dopo il controllo meccanico). Il plugin li riceve col sync;
  * «seme»: li scrive il plugin (dal Mac, `sentinelle_pubblica.py --carica-semi`); l'Action li legge soltanto.
Ogni percorso che arriva dal manifest deve rispettare queste regole: e' anche il filtro del client (niente «..», niente
cartelle inattese).

QUALE COPIA SI LEGGE
--------------------
La sincronizzata, se il suo manifest (`wiki-studio/sentinelle/manifest.json`) e' generato non prima di quello del pacchetto;
altrimenti il pacchetto (un pacchetto piu' nuovo della copia di una vecchia attivita' vince). Con STUDIO_AREE_OFF=1 si
legge sempre il pacchetto (interruttore d'emergenza).

Solo stdlib, Python 3.9. Nessun import pesante: lo usano anche gli hook.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, stato_root  # noqa: E402

CARTELLA = "aree"
#: il manifest delle aree, nel repo pubblico e nel plugin (lo stesso percorso)
MANIFEST = "wiki-studio/sentinelle/manifest.json"
STATO = "wiki-studio/sentinelle/stato.json"

_NOME = r"[a-z0-9][a-z0-9._-]{0,150}"
#: area → (proprietario, regex del percorso relativo alla radice)
AREE = {
    "normativa": (
        ("action", r"wiki-studio/normativa/changelog-riforme\.meta\.json"),
        ("action", r"wiki-studio/normativa/sentinella-debito\.json"),
        ("action", r"wiki-studio/normativa/changelog-riforme\.md"),
        ("action", r"wiki-studio/normativa/drift-reports/\d{4}-\d{2}-\d{2}\.md"),
        ("seme", r"wiki-studio/normativa/vigenza-watchlist\.md"),
        ("seme", r"wiki-studio/normativa/stato-orientamenti\.md"),
    ),
    "modelli": (
        ("action", r"wiki-studio/modelli/civile/" + _NOME + r"\.md"),
        ("action", r"wiki-studio/modelli/(?:modelli\.meta|catalogo|norme-citate)\.json"),
        ("seme", r"wiki-studio/modelli/(?:formule-obsolete|requisiti-per-tipo)\.json"),
        ("seme", r"wiki-studio/modelli/(?:README|STRATEGIA-CATALOGO|INDEX-MODELLI)\.md"),
    ),
    "dati": (
        ("action", r"dati/tassi(?:-soglia)?\.json"),
        ("action", r"wiki-studio/parcella/contributo-unificato\.json"),
        ("action", r"wiki-studio/normativa/(?:pct-specifiche|limiti-dm-110-2023|competenza-materia-gdp)\.json"),
    ),
    "successioni": (
        ("action", r"skills/assistente-successioni/references/changelog-normativo\.md"),
        ("action", r"skills/assistente-successioni/references/uffici-competenza-successioni\.json"),
    ),
    "stato": (
        ("action", r"wiki-studio/sentinelle/(?:stato|modelli-stato|successioni)\.json"),
    ),
}
_RX = [(area, prop, re.compile("^" + rx + "$")) for area, voci in AREE.items() for prop, rx in voci]
#: i drift-report che il client tiene (gli ultimi N)
DRIFT_TENUTI = 2
_CACHE: dict = {}


def classifica(rel: str):
    """(area, proprietario) del percorso relativo alla radice, o None se non appartiene a nessuna area."""
    rel = str(rel or "").replace("\\", "/")
    if ".." in rel.split("/") or rel.startswith("/"):
        return None
    for area, prop, rx in _RX:
        if rx.match(rel):
            return area, prop
    return None


def rel_valido(rel: str) -> bool:
    return classifica(rel) is not None


def dell_action(rel: str) -> bool:
    c = classifica(rel)
    return bool(c) and c[1] == "action"


def dir_runtime() -> Path:
    return stato_root() / CARTELLA


def _generato(p: Path) -> str:
    try:
        return str(json.loads(p.read_text(encoding="utf-8")).get("generato_il") or "")
    except (OSError, ValueError, AttributeError):
        return ""


def sincronizzata_valida() -> bool:
    """True se la copia sincronizzata va letta: esiste, non e' spenta, e non e' piu' vecchia del pacchetto."""
    if os.environ.get("STUDIO_AREE_OFF"):
        return False
    sinc = dir_runtime() / MANIFEST
    if not sinc.is_file():
        return False
    pacchetto = ROOT / MANIFEST
    return not pacchetto.is_file() or _generato(sinc) >= _generato(pacchetto)


def file_sincronizzato(rel: str):
    """La copia sincronizzata di un file dell'Action, se va letta; None altrimenti."""
    if not dell_action(rel) or not sincronizzata_valida():
        return None
    p = dir_runtime() / rel
    return p if p.is_file() else None


def file(rel: str):
    """Il file da leggere: la copia sincronizzata se c'e' e vale, altrimenti quella del pacchetto (o None)."""
    p = file_sincronizzato(rel)
    if p is not None:
        return p
    b = ROOT / str(rel)
    return b if b.is_file() else None


def leggi_json(rel: str):
    """Il JSON da leggere (sincronizzato o del pacchetto), in cache per (percorso, mtime, dimensione); None se manca."""
    p = file(rel)
    if not p:
        return None
    try:
        st = p.stat()
        chiave = (str(p), st.st_mtime_ns, st.st_size)
    except OSError:
        return None
    if _CACHE.get(rel, (None,))[0] == chiave:
        return _CACHE[rel][1]
    try:
        dati = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    _CACHE[rel] = (chiave, dati)
    return dati


def stato_sentinelle() -> dict:
    """Lo stato dell'ultimo giro dell'Action (`wiki-studio/sentinelle/stato.json`), {} se non c'e'."""
    d = leggi_json(STATO)
    return d if isinstance(d, dict) else {}


def riga_router(oggi=None) -> str:
    """Una riga per il router: vuota se tutto e' in ordine. I modelli hanno gia' la riga della sentinella dei modelli."""
    import datetime as _dt
    a = stato_sentinelle().get("aree") or {}
    if not a:
        return ""
    oggi = oggi or _dt.date.today()
    pezzi, ferme = [], []
    for area in ("normativa", "successioni", "dati"):
        v = a.get(area) or {}
        n = len(v.get("da_ricontrollare") or [])
        if n:
            pezzi.append(f"{area} {n} da ricontrollare")
        if v.get("esito") == "parziale":
            pezzi.append(f"{area} giro parziale")
        try:
            if v.get("ultimo_giro") and (oggi - _dt.date.fromisoformat(str(v["ultimo_giro"])[:10])).days > 8:
                ferme.append(area)
        except ValueError:
            pass
    if ferme:
        pezzi.append("giro fermo da più di 8 giorni: " + ", ".join(ferme))
    if not pezzi:
        return ""
    return ("Sentinelle automatiche: " + " · ".join(pezzi)
            + " (dettagli: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aree.py --stato)")


def drift_report() -> list:
    """I drift-report disponibili (sincronizzati e del pacchetto), dal piu' recente."""
    out = {}
    for base in ((dir_runtime(),) if sincronizzata_valida() else ()) + (ROOT,):
        d = base / "wiki-studio" / "normativa" / "drift-reports"
        if d.is_dir():
            for p in d.glob("*.md"):
                out.setdefault(p.name, p)
    return [out[k] for k in sorted(out, reverse=True)]


def elenco_sincronizzati() -> list:
    """I file dell'Action presenti nella copia sincronizzata (percorsi relativi), se la copia vale."""
    if not sincronizzata_valida():
        return []
    base = dir_runtime()
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*")
                  if p.is_file() and dell_action(p.relative_to(base).as_posix()))


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Aree delle sentinelle: quale copia si legge.")
    ap.add_argument("--elenco", action="store_true", help="i file sincronizzati che si leggono al posto del pacchetto")
    ap.add_argument("--stato", action="store_true", help="lo stato dell'ultimo giro dell'Action")
    a = ap.parse_args(argv)
    if a.stato:
        print(json.dumps(stato_sentinelle(), ensure_ascii=False, indent=1))
        return 0
    sinc = elenco_sincronizzati()
    print(f"copia sincronizzata: {'in uso' if sincronizzata_valida() else 'non in uso'} ({dir_runtime()})")
    for rel in sinc:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
