#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LE PROVE DELLE SENTINELLE (v0.36): una notizia normativa vale solo se lo script la ritrova sulla fonte ufficiale.

Nell'Action «sentinelle» Claude cerca (WebSearch, WebFetch) e consegna, per ogni esito, la PROVA:
`{"url": …, "estremi": ["n. 137", "28 luglio 2026"], "citazione": "…almeno 40 caratteri copiati dalla pagina…"}`.
Questo modulo la controlla senza fidarsi di nessuno: l'indirizzo dev'essere https di un dominio ufficiale, lo script
riscarica la pagina (HTML o PDF), e nel testo normalizzato devono comparire ogni estremo e la citazione. Ciò che non
passa non si pubblica: resta «da ricontrollare», con una issue.

Uso da riga di comando (anche per Claude, per provare una prova prima di consegnarla):
  python3 scripts/sentinelle_prove.py --prova --url URL --estremi "n. 137" "28 luglio 2026" --citazione "…"
Solo stdlib (pdftotext facoltativo per i PDF), Python 3.9.
"""
from __future__ import annotations

import argparse
import hashlib
import html as _html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (corpus-normativo sentinelle)"
TIMEOUT = 40
#: citazione minima: abbastanza lunga da non trovarsi per caso
CITAZIONE_MIN = 40
#: domini delle fonti ufficiali (e dei siti istituzionali di chi pubblica il dato); un sottodominio vale
DOMINI_UFFICIALI = (
    "gazzettaufficiale.it", "normattiva.it", "eur-lex.europa.eu", "europa.eu", "ecb.europa.eu",
    "mef.gov.it", "finanze.gov.it", "agenziaentrate.gov.it", "giustizia.it", "consiglionazionaleforense.it",
    "cortecostituzionale.it", "cortedicassazione.it", "bancaditalia.it", "istat.it", "inps.it", "inail.it",
    "lavoro.gov.it", "ispettorato.gov.it", "cassaforense.it", "camera.it", "senato.it", "governo.it",
    "garanteprivacy.it", "geonetwork.it",
)


def dominio_ammesso(url: str) -> bool:
    try:
        u = urlparse(str(url or ""))
    except ValueError:
        return False
    host = (u.hostname or "").lower()
    return u.scheme == "https" and any(host == d or host.endswith("." + d) for d in DOMINI_UFFICIALI)


def normalizza(testo: str) -> str:
    """Testo confrontabile: entità e tag HTML via, Unicode NFKC, apostrofi e virgolette uniformi, a capo e trattini
    di sillabazione tolti, spazi compressi, minuscole."""
    t = _html.unescape(str(testo or ""))
    t = unicodedata.normalize("NFKC", t)
    t = t.replace("­", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("«", '"') \
        .replace("»", '"').replace("–", "-").replace("—", "-").replace(" ", " ")
    t = re.sub(r"-\s*\n\s*", "", t)                      # sillabazione a fine riga nei PDF
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


def _da_html(h: str) -> str:
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h or "")
    h = re.sub(r"(?s)<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>", "\n", h)
    return re.sub(r"(?s)<[^>]+>", " ", h)


def _da_pdf(dati: bytes) -> str:
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("pdftotext non disponibile per leggere il PDF")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.pdf"
        p.write_bytes(dati)
        r = subprocess.run([exe, "-layout", str(p), "-"], capture_output=True, timeout=120)
        return r.stdout.decode("utf-8", "replace")


def scarica(url: str) -> tuple:
    """(testo, sha256 dei byte, tipo) della pagina o del PDF."""
    with urlopen(Request(url, headers={"User-Agent": UA, "Accept-Language": "it"}), timeout=TIMEOUT) as r:
        dati = r.read()
        tipo = str(r.headers.get("Content-Type") or "").lower()
    sha = hashlib.sha256(dati).hexdigest()
    if "pdf" in tipo or dati[:5] == b"%PDF-":
        return _da_pdf(dati), sha, "pdf"
    return _da_html(dati.decode("utf-8", "replace")), sha, "html"


def _estremo_presente(estremo: str, testo_norm: str) -> bool:
    e = normalizza(estremo)
    if not e:
        return False
    if e in testo_norm:
        return True
    # tolleranza minima di grafia: «n. 137» = «n.137», «art. 19» = «art.19»; nient'altro
    compatto = re.sub(r"\s+", "", e)
    return compatto in re.sub(r"\s+", "", testo_norm)


def verifica_prova(prova: dict, get=None) -> dict:
    """{esito: OK|KO, motivi, url, sha256} — `get(url) -> (testo, sha, tipo)` per i test."""
    prova = prova or {}
    url = str(prova.get("url") or "").strip()
    estremi = [str(x) for x in (prova.get("estremi") or []) if str(x).strip()]
    citazione = str(prova.get("citazione") or "")
    motivi = []
    if not dominio_ammesso(url):
        motivi.append(f"indirizzo non ammesso (serve https di una fonte ufficiale): {url[:120] or '(vuoto)'}")
    if not estremi:
        motivi.append("nessun estremo indicato")
    if len(normalizza(citazione)) < CITAZIONE_MIN:
        motivi.append(f"citazione troppo corta (servono almeno {CITAZIONE_MIN} caratteri copiati dalla fonte)")
    if motivi:
        return {"esito": "KO", "motivi": motivi, "url": url, "sha256": None}
    try:
        testo, sha, _tipo = (get or scarica)(url)
    except Exception as e:  # noqa: BLE001 — una fonte che non risponde non prova niente
        return {"esito": "KO", "motivi": [f"fonte non scaricabile ({e.__class__.__name__}: {str(e)[:120]})"], "url": url, "sha256": None}
    tn = normalizza(testo)
    for e in estremi:
        if not _estremo_presente(e, tn):
            motivi.append(f"l'estremo «{e}» non compare nella fonte")
    if normalizza(citazione) not in tn:
        motivi.append("la citazione non compare nella fonte")
    return {"esito": "KO" if motivi else "OK", "motivi": motivi, "url": url, "sha256": sha}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Controlla una prova (url, estremi, citazione) come la controlla l'Action.")
    ap.add_argument("--prova", action="store_true", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--estremi", nargs="+", default=[])
    ap.add_argument("--citazione", default="")
    a = ap.parse_args(argv)
    r = verifica_prova({"url": a.url, "estremi": a.estremi, "citazione": a.citazione})
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["esito"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
