#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STRUMENTI COMUNI DELLE SENTINELLE AUTOMATICHE (v0.36): git, file, corpus, rapporto, issue, stato del giro.

Le aree (dati, normativa, successioni, modelli) girano nel repo pubblico del corpus dentro l'Action «sentinelle», con lo
stesso schema dell'area lavoro: passi deterministici → (Claude, se serve) → controllo meccanico → pubblicazione.
Qui stanno i pezzi che servono a tutte: leggere e scrivere JSON conservando la formattazione del file, sapere quali
file sono cambiati e rimetterli com'erano, leggere il manifest e il changelog del corpus, tenere il rapporto e la issue,
aggiornare `wiki-studio/sentinelle/stato.json`.

Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT  # noqa: E402

import aree  # noqa: E402

#: tipi di riga del changelog-auto che dicono «il testo e' cambiato» (le «note» e le «datazioni» no)
TIPI_CAMBIO = ("modificato", "abrogato", "rimosso", "aggiunto")


def oggi() -> _dt.date:
    return _dt.date.today()


def adesso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


# ----------------------------------------------------------------------------------------------- file

def leggi_json(p: Path, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _rientro(p: Path) -> int:
    try:
        for riga in Path(p).read_text(encoding="utf-8").splitlines()[1:6]:
            m = re.match(r"^( +)\S", riga)
            if m:
                return len(m.group(1))
    except OSError:
        pass
    return 1


def scrivi_json(p: Path, dati) -> None:
    """Scrive il JSON con il rientro che il file ha gia' (1 o 2 spazi), cosi' i diff restano leggibili."""
    p = Path(p)
    rientro = _rientro(p) if p.exists() else 1
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dati, ensure_ascii=False, indent=rientro) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------- riservatezza

#: le stesse impronte di `corpus_contribuisci.VIETATI_SHA` (nomi che il repo pubblico non deve contenere): un test le
#: tiene allineate. Si confrontano parole e coppie di parole, mai il testo in chiaro.
VIETATI_SHA = frozenset({
    "1a60c5f2167e15c29a9be3496b45e8839c7021896e616e5a6529ab10382ab116",
    "f1817f7333892539d54f0bc58653999a31d6c7274f806e45080c6255c63a6333",
    "ffe138c1680e8e3c824daa5c3eeba673825b9a0092866608b1f4f3e3212378d1",
    "13cbfd2790348c84875ada40c7a7ada348e74d7766b49d03aa4d69c779fc0581",
})
_RX_PERSONALI = (
    ("codice fiscale", re.compile(r"\b[A-Z]{6}\d{2}[A-EHLMPR-T]\d{2}[A-Z]\d{3}[A-Z]\b")),
    ("IBAN", re.compile(r"\bIT\d{2}[A-Z]\d{10}[0-9A-Z]{12}\b")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", re.I)),
    ("telefono", re.compile(r"(?<![\w/.,])(?:\+39[\s.]?)?0\d{1,3}[\s.]?\d{6,8}(?![\w/.,])")),
)


def _parole(testo: str) -> list:
    import unicodedata
    s = unicodedata.normalize("NFKD", testo or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.findall(r"[a-z0-9]+", s)


def nomi_vietati(testo: str, extra: set = frozenset()) -> list:
    """Le parole (o coppie di parole) vietate presenti nel testo (impronte, o parole in chiaro di `extra`)."""
    import hashlib
    ws = _parole(testo)
    trovati = set()
    for i, w in enumerate(ws):
        for forma in (w, f"{w} {ws[i + 1]}" if i + 1 < len(ws) else None):
            if forma and (hashlib.sha256(forma.encode("utf-8")).hexdigest() in VIETATI_SHA or forma in extra):
                trovati.add(forma)
    return sorted(trovati)


#: recapiti istituzionali (uffici pubblici): non sono dati personali
DOMINI_ISTITUZIONALI = ("agenziaentrate", "gov.it", "giustizia.it", "inps.it", "inail.it", "istat.it", "bancaditalia.it",
                        "cortecostituzionale.it", "cortedicassazione.it", "camera.it", "senato.it",
                        "noreply.github.com")


def dati_personali(testo: str, telefoni_istituzionali: bool = False) -> list:
    """[(tipo, valore)] dei dati personali riconoscibili (codice fiscale, IBAN, email, telefono). Le email di uffici pubblici
    non contano; i telefoni non contano dove il file e' un elenco di uffici pubblici (`telefoni_istituzionali`)."""
    out = []
    for nome, rx in _RX_PERSONALI:
        if nome == "telefono" and telefoni_istituzionali:
            continue
        for m in rx.finditer(testo or ""):
            v = m.group(0)
            if nome == "email" and (any(d in v.lower().split("@", 1)[-1] for d in DOMINI_ISTITUZIONALI)
                                    or re.search(r"\.{3,}|_{2,}|…", v.split("@", 1)[0])):
                continue                     # ufficio pubblico, o segnaposto di un modello («avv.......@pec.it»)
            out.append((nome, v))
    return out


# ----------------------------------------------------------------------------------------------- git

def git(radice: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(radice), *args], capture_output=True, text=True, encoding="utf-8")


def toccati(radice: Path) -> list:
    """[(stato git, percorso)] dei file modificati o nuovi rispetto all'ultimo commit."""
    r = git(radice, "status", "--porcelain", "--untracked-files=all")
    out = []
    for riga in r.stdout.splitlines():
        if len(riga) > 3:
            rel = riga[3:].strip().strip('"')
            if " -> " in rel:
                rel = rel.split(" -> ", 1)[1]
            out.append((riga[:2], rel))
    return out


def ripristina(radice: Path, stato: str, rel: str) -> None:
    if "?" in stato:
        try:
            (Path(radice) / rel).unlink()
        except OSError:
            pass
    else:
        git(radice, "checkout", "--", rel)


def ripristina_fuori_da(radice: Path, ammessi) -> list:
    """Rimette com'era ogni file toccato che non rispetta `ammessi(rel)`: ritorna i percorsi ripristinati."""
    out = []
    for st, rel in toccati(radice):
        if not ammessi(rel):
            ripristina(radice, st, rel)
            out.append(rel)
    return out


# ----------------------------------------------------------------------------------------------- corpus

def manifest_corpus(radice: Path = ROOT) -> dict:
    """Il manifest del corpus: `manifest.json` nel repo pubblico, `corpus-manifest.json` nel plugin."""
    radice = Path(radice)
    for p in (radice / "manifest.json", radice / "wiki-studio" / "normativa" / "corpus-manifest.json"):
        d = leggi_json(p)
        if isinstance(d, dict) and d.get("atti"):
            return d
    return {}


def codici(radice: Path = ROOT) -> dict:
    return (leggi_json(Path(radice) / "wiki-studio" / "normativa" / "codici.json", {}) or {}).get("atti") or {}


def changelog_auto(radice: Path = ROOT) -> list:
    return (leggi_json(Path(radice) / "wiki-studio" / "normativa" / "changelog-auto.json", {}) or {}).get("modifiche") or []


def cambi_dopo(righe: list, slug: str, dal: str, articoli=None) -> list:
    """Le righe del changelog-auto che cambiano il testo di `slug` (e degli `articoli`, se dati) registrate dopo `dal`."""
    arts = {str(a).lower() for a in (articoli or [])}
    return [r for r in righe if r.get("slug") == slug and r.get("tipo") in TIPI_CAMBIO
            and str(r.get("registrato_il") or "")[:10] > str(dal or "")[:10]
            and (not arts or str(r.get("articolo") or "").lower() in arts)]


_RX_ESTREMI = re.compile(r"\b(\d{1,4})\s*/\s*(\d{4})\b")


def slug_da_estremi(estremi: str, radice: Path = ROOT) -> list:
    """Gli atti del corpus che corrispondono agli estremi «N/AAAA» (numero e anno nell'URN di codici.json)."""
    out = []
    coppie = {(n.lstrip("0") or "0", a) for n, a in _RX_ESTREMI.findall(str(estremi or ""))}
    if not coppie:
        return out
    for slug, cfg in codici(radice).items():
        m = re.match(r"urn:nir:[^:]+:[^:]+:(\d{4})-\d{2}-\d{2};(\d+)", str(cfg.get("urn") or ""))
        if m and (m.group(2).lstrip("0") or "0", m.group(1)) in coppie:
            out.append(slug)
    return sorted(set(out))


def stato_atto(manifest: dict, slug: str) -> dict:
    return ((manifest or {}).get("atti") or {}).get(slug) or {}


# ----------------------------------------------------------------------------------------------- rapporto e issue

class Giro:
    """Il resoconto di un giro di un'area: righe del rapporto (Step Summary), righe della issue, voci da ricontrollare."""

    def __init__(self, area: str):
        self.area = area
        self.rapporto: list = []
        self.issue: list = []
        self.da_ricontrollare: list = []
        self.esito = "ok"
        self.dati: dict = {}

    def riga(self, testo: str) -> None:
        self.rapporto.append(testo)

    def problema(self, testo: str, ricontrollare: str = "") -> None:
        self.issue.append(testo)
        if ricontrollare and ricontrollare not in self.da_ricontrollare:
            self.da_ricontrollare.append(ricontrollare)

    def parziale(self) -> None:
        self.esito = "parziale"

    def markdown(self) -> str:
        testa = f"### Sentinelle — {self.area} ({self.esito})"
        return "\n".join([testa, ""] + [f"- {r}" for r in self.rapporto] + [""])


def scrivi_rapporto(giro: Giro, percorso: str = "") -> None:
    if percorso:
        with open(percorso, "a", encoding="utf-8") as f:
            f.write(giro.markdown() + "\n")


def scrivi_issue(giri: list, percorso: str) -> int:
    righe = []
    for g in giri:
        if g.issue:
            righe.append(f"## {g.area}")
            righe += [f"- {x}" for x in g.issue]
            righe.append("")
    if percorso:
        Path(percorso).write_text("\n".join(righe), encoding="utf-8")
    return sum(len(g.issue) for g in giri)


def aggiorna_stato(radice: Path, giro: Giro, extra: dict = None) -> dict:
    """`wiki-studio/sentinelle/stato.json`: per area, data dell'ultimo giro, esito, voci da ricontrollare."""
    p = Path(radice) / aree.STATO
    st = leggi_json(p, {}) or {}
    st.setdefault("_meta", {})["descrizione"] = ("Stato dell'ultimo giro delle sentinelle automatiche (GitHub Action «sentinelle» "
                                                 "del corpus pubblico), per area.")
    st["_meta"]["aggiornato_il"] = adesso()
    voce = {"ultimo_giro": oggi().isoformat(), "esito": giro.esito, "da_ricontrollare": sorted(giro.da_ricontrollare)}
    voce.update(extra or {})
    st.setdefault("aree", {})[giro.area] = voce
    scrivi_json(p, st)
    return st


def github_output(percorso: str, **coppie) -> None:
    if percorso:
        with open(percorso, "a", encoding="utf-8") as f:
            for k, v in coppie.items():
                f.write(f"{k}={v}\n")
