#!/usr/bin/env python3
"""COMUNI ITALIANI dall'ISTAT (v0.53) — codice catastale (Belfiore), denominazione, provincia: tabella LOCALE (solo stdlib).

PERCHE'
-------
Il generatore del `.suc` vuole comune E provincia di nascita di ogni soggetto, il codice catastale del comune di ogni
immobile, e il controllo del codice fiscale confronta il comune di nascita col codice nelle posizioni 12-15. Fino alla v0.52
il plugin aveva una tabella di poche decine di capoluoghi (`anagrafica.COMUNI_CATASTALI`) e la provincia la scriveva il
modello. Qui c'e' l'elenco ufficiale ISTAT dei comuni vigenti (≈ 7.900) con il codice catastale, piu' i comuni soppressi
(per nome, con il comune in cui sono confluiti: l'ISTAT non ne pubblica il codice catastale). Serve anche alla tabella
nazionale degli uffici competenti (`uffici_competenza.py`), che ha come chiave il codice catastale: i comuni omonimi
(Livo, Peglio, Samone, Calliano, Castro…) non si confondono.

Fonti: ISTAT, «Elenco dei comuni italiani» (CSV) e «Elenco dei comuni soppressi» (zip con CSV), pagine stabili sotto
https://www.istat.it/storage/codici-unita-amministrative/ — aggiornate dall'ISTAT a ogni variazione territoriale.

Uso:
  python3 scripts/comuni_istat.py --aggiorna [--nel-repo]        # riscarica e riscrive dati/comuni-italiani.json
  python3 scripts/comuni_istat.py --codice L219                  # → TORINO (TO)
  python3 scripts/comuni_istat.py --nome "Calliano"               # tutti i codici con quel nome (omonimi)
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import re
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

ROOT = Path(__file__).resolve().parents[1]
DATI = ROOT / "dati" / "comuni-italiani.json"
URL_VIGENTI = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
URL_SOPPRESSI = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-soppressi.zip"
#: sotto questo numero di comuni vigenti la tabella nuova non sostituisce la vecchia (pagina ISTAT cambiata o troncata)
MIN_COMUNI = 7800

_CACHE: dict = {}


def norm(nome: str) -> str:
    """«Agliè» → «AGLIE», «Castell'Arquato» → «CASTELL ARQUATO»: la chiave per nome (maiuscole, senza accenti)."""
    t = unicodedata.normalize("NFKD", str(nome or ""))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip().upper()


def _scarica(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (studio; tabella comuni)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def _csv(dati: bytes) -> list:
    for enc in ("utf-8-sig", "cp1252", "latin1"):
        try:
            testo = dati.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return list(csv.reader(io.StringIO(testo), delimiter=";"))


def costruisci(vigenti: bytes, soppressi: bytes | None = None) -> dict:
    righe = _csv(vigenti)
    testa = [re.sub(r"\s+", " ", h).strip().lower() for h in righe[0]]

    def col(*parole):
        for i, h in enumerate(testa):
            if all(p in h for p in parole):
                return i
        raise ValueError(f"colonna {parole} non trovata nell'elenco ISTAT")
    i_cat, i_nome, i_sigla = col("codice catastale"), col("denominazione in italiano"), col("sigla automobilistica")
    i_istat, i_reg = col("codice comune formato alfanumerico"), col("denominazione regione")
    comuni = {}
    for r in righe[1:]:
        if len(r) <= max(i_cat, i_nome, i_sigla, i_istat, i_reg) or not r[i_cat].strip():
            continue
        comuni[r[i_cat].strip().upper()] = [r[i_nome].strip(), r[i_sigla].strip().upper(), r[i_istat].strip(), r[i_reg].strip()]
    soppr = {}
    if soppressi:
        with zipfile.ZipFile(io.BytesIO(soppressi)) as z:
            nome_csv = next((n for n in z.namelist() if n.lower().endswith(".csv")), None)
            if nome_csv:
                rs = _csv(z.read(nome_csv))
                th = [re.sub(r"\s+", " ", h).strip().lower() for h in rs[0]]
                j_nome = next(i for i, h in enumerate(th) if h.startswith("denominazione comune") and "associato" not in h)
                j_sigla = next(i for i, h in enumerate(th) if h.startswith("sigla automobilistica") and "associata" not in h)
                j_data = next(i for i, h in enumerate(th) if h.startswith("data evento"))
                j_in = next(i for i, h in enumerate(th) if h.startswith("denominazione comune associato"))
                for r in rs[1:]:
                    if len(r) > max(j_nome, j_sigla, j_data, j_in) and r[j_nome].strip():
                        soppr[f"{norm(r[j_nome])}|{r[j_sigla].strip().upper()}"] = [r[j_nome].strip(), r[j_sigla].strip().upper(),
                                                                                   r[j_data].strip(), r[j_in].strip()]
    return {"_meta": {"fonte": [URL_VIGENTI, URL_SOPPRESSI], "scaricato_il": _dt.date.today().isoformat(),
                      "comuni": len(comuni), "soppressi": len(soppr),
                      "formato": "comuni: {codice catastale: [nome, sigla provincia, codice ISTAT, regione]} · "
                                 "soppressi: {NOME|SIGLA: [nome, sigla, data dell'evento, comune in cui e' confluito]}"},
            "comuni": dict(sorted(comuni.items())), "soppressi": dict(sorted(soppr.items()))}


def carica() -> dict:
    if "dati" not in _CACHE:
        try:
            _CACHE["dati"] = json.loads(DATI.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _CACHE["dati"] = {"comuni": {}, "soppressi": {}}
        per_nome: dict = {}
        for cod, (nome, sigla, *_r) in _CACHE["dati"].get("comuni", {}).items():
            per_nome.setdefault(norm(nome), []).append(cod)
        _CACHE["per_nome"] = per_nome
    return _CACHE["dati"]


def da_codice(codice: str) -> dict | None:
    """{codice, nome, provincia, istat, regione} o None (codici esteri «Z…» compresi: None, provincia EE altrove)."""
    v = carica().get("comuni", {}).get(str(codice or "").strip().upper())
    return {"codice": str(codice).upper(), "nome": v[0], "provincia": v[1], "istat": v[2], "regione": v[3]} if v else None


def da_nome(nome: str, provincia: str = "") -> list:
    """Tutti i comuni vigenti con quel nome (gli omonimi sono piu' d'uno: la provincia scioglie)."""
    carica()
    codici = _CACHE["per_nome"].get(norm(nome), [])
    out = [da_codice(c) for c in codici]
    if provincia:
        out = [c for c in out if c and c["provincia"] == provincia.strip().upper()] or out
    return [c for c in out if c]


def soppresso(nome: str, provincia: str = "") -> dict | None:
    s = carica().get("soppressi", {})
    for k, v in s.items():
        if k.split("|")[0] == norm(nome) and (not provincia or v[1] == provincia.strip().upper()):
            return {"nome": v[0], "provincia": v[1], "data": v[2], "confluito_in": v[3]}
    return None


def aggiorna(dest: Path = DATI) -> dict:
    nuovi = costruisci(_scarica(URL_VIGENTI), _scarica(URL_SOPPRESSI))
    if nuovi["_meta"]["comuni"] < MIN_COMUNI:
        raise RuntimeError(f"elenco ISTAT con {nuovi['_meta']['comuni']} comuni (< {MIN_COMUNI}): tabella invariata")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(nuovi, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    _CACHE.clear()
    return nuovi


def main() -> int:
    ap = argparse.ArgumentParser(description="Comuni italiani (ISTAT): codice catastale, nome, provincia")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--nel-repo", action="store_true", help="(compatibilita') la tabella vive comunque in dati/")
    ap.add_argument("--codice")
    ap.add_argument("--nome")
    ap.add_argument("--provincia", default="")
    a = ap.parse_args()
    if a.aggiorna:
        d = aggiorna()
        print(f"📝 {DATI}: {d['_meta']['comuni']} comuni vigenti, {d['_meta']['soppressi']} soppressi ({d['_meta']['scaricato_il']})")
        return 0
    if a.codice:
        c = da_codice(a.codice)
        print(json.dumps(c, ensure_ascii=False) if c else f"{a.codice}: non è un comune vigente (estero «Z…» o soppresso)")
        return 0 if c else 1
    if a.nome:
        cc = da_nome(a.nome, a.provincia)
        s = soppresso(a.nome, a.provincia)
        print(json.dumps({"vigenti": cc, "soppresso": s}, ensure_ascii=False, indent=1))
        return 0 if cc or s else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
