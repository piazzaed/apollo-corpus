#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.43.2 — i numeri degli articoli, in UN posto solo (solo stdlib).

Gli articoli con suffisso latino si scrivevano con otto elenchi diversi sparsi negli script: l'estrattore delle claim si
fermava a «quaterdecies» e non conosceva il «.1», sicche' gli articoli piu' recenti del d.lgs. 231/2001
(25-quinquiesdecies … 25-vicies, 25-octies.1) non diventavano claim e uscivano dall'atto senza verifica. Qui la tabella dei
numerali (con le grafie che normattiva e le leggi alternano) e le espressioni che la usano.
"""
from __future__ import annotations

import re

#: i numerali latini degli articoli → valore (bis = 2 … vicies = 20), con le grafie alternative
NUMERALI = {"semel": 1, "bis": 2, "ter": 3, "quater": 4, "quinquies": 5, "sexies": 6, "septies": 7, "octies": 8,
            "novies": 9, "nonies": 9, "decies": 10, "undecies": 11, "duodecies": 12, "terdecies": 13, "tredecies": 13,
            "quaterdecies": 14, "quattuordecies": 14, "quinquiesdecies": 15, "quindecies": 15, "sexiesdecies": 16,
            "sexdecies": 16, "sedecies": 16, "septiesdecies": 17, "septdecies": 17, "septemdecies": 17,
            "octiesdecies": 18, "duodevicies": 18, "octodecies": 18, "noviesdecies": 19, "undevicies": 19,
            "novemdecies": 19, "vicies": 20}

#: alternanza dei suffissi, il piu' lungo prima («quaterdecies» prima di «quater»)
SUFFISSO = "(?:" + "|".join(sorted(NUMERALI, key=len, reverse=True)) + ")"

#: un numero d'articolo: «25», «25-bis», «25 octies.1», «4-quinquies.1», «132.1», «640-ter»
NUM_ART = (r"[0-9]{1,4}(?:\.[0-9]+(?![0-9]))?(?:[\s-]*" + SUFFISSO + r"\b)?(?:\.[0-9]+(?![0-9]))?")

_RX_INCOLLA = re.compile(r"(\d)\s*-?\s*(" + SUFFISSO + r")\b", re.I)


def normalizza(numero: str) -> str:
    """«25 octies.1» → «25-octies.1», «281 undecies» → «281-undecies», «nonies» → «novies»."""
    p = re.sub(r"\s*-\s*", "-", str(numero or "").strip())
    p = _RX_INCOLLA.sub(lambda m: f"{m.group(1)}-{m.group(2).lower()}", p)
    return p.replace("nonies", "novies")


def valore(suffisso: str) -> int:
    """Il valore del suffisso latino (0 se non c'e', 90 se non si riconosce): per ordinare gli articoli."""
    s = str(suffisso or "").lower()
    if not s:
        return 0
    return NUMERALI.get(s, 90)
