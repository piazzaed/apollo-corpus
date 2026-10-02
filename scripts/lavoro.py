#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L'AREA «LAVORO» DEL CORPUS (v0.36): dove stanno l'indice dei CCNL, l'indice della prassi, i numeri annuali e le
schede del memento, e come si leggono.

Due copie, come per il resto del corpus: il seme nel pacchetto del plugin (`wiki-studio/lavoro/`) e la copia
sincronizzata dal corpus pubblico (`<stato>/lavoro/`, scritta da corpus_sync.py). Si legge la sincronizzata se
c'e', altrimenti il seme. Ogni percorso relativo deve rispettare RX_REL: e' anche il filtro che il client del
corpus applica ai nomi che arrivano dal manifest (niente «..», niente sottocartelle inattese).

Solo stdlib, Python 3.9. Nessun import pesante: lo usano anche gli hook.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import WIKI, stato_root  # noqa: E402

CARTELLA = "lavoro"
#: i file dell'area: ccnl/…, prassi/…, dati/…, memento/… (solo .json e .md, nomi semplici)
RX_REL = re.compile(r"^(ccnl|prassi|dati|memento)/[a-z0-9][a-z0-9._-]{0,80}\.(json|md)$")
_CACHE: dict = {}


def dir_seed() -> Path:
    return WIKI / CARTELLA


def dir_runtime() -> Path:
    return stato_root() / CARTELLA


def rel_valido(rel: str) -> bool:
    return bool(RX_REL.match(str(rel or ""))) and ".." not in str(rel)


def file(rel: str):
    """Il file dell'area (prima la copia sincronizzata, poi il seme), o None."""
    if not rel_valido(rel):
        return None
    for base in (dir_runtime(), dir_seed()):
        p = base / rel
        if p.is_file():
            return p
    return None


def leggi_json(rel: str):
    """Il JSON dell'area, in cache per (percorso, mtime, dimensione); None se manca o e' illeggibile."""
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


def elenco(sotto: str) -> list:
    """I percorsi relativi presenti (seme e sincronizzati, senza doppioni) in una sottocartella dell'area."""
    out = set()
    for base in (dir_runtime(), dir_seed()):
        d = base / sotto
        if d.is_dir():
            for p in d.iterdir():
                rel = f"{sotto}/{p.name}"
                if p.is_file() and rel_valido(rel):
                    out.add(rel)
    return sorted(out)
