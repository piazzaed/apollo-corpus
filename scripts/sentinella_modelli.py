#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SENTINELLA DEI MODELLI D'ATTO — controllo mensile, deterministico, del catalogo (v0.29, D1). Solo stdlib.

PERCHE'
-------
I 206 modelli di `wiki-studio/modelli/civile/` (testi di febbraio 2026, in Markdown) sono il punto
di partenza di ogni atto. Fino alla v0.28 la loro «freschezza» si giudicava solo dalle date e da tre voci del
changelog: tutti FRESCHI oggi, tutti SCADUTI insieme nel 2027, e nessuno sguardo al TESTO delle norme citate.
Intanto il D.L. 19/2026 ha riscritto gli artt. 696 e 696-bis c.p.c., il D.Lgs. 164/2024 ha tolto il numero di
fax dall'art. 125, l'art. 475 non parla piu' di «formula esecutiva»… e i modelli dicevano ancora il contrario.
Questa sentinella legge ogni modello come lo leggerebbe un avvocato pignolo, una volta al mese.

COSA CONTROLLA (per modello, solo sul fac-simile e sulle norme_chiave)
 a) NORME CITATE: ogni «art. N <atto>» e' cercato nel corpus locale datato (codice_locale). Esiti: NON_TROVATA,
    ABROGATA, MODIFICATA (vigore_da dell'articolo successivo alla data di allineamento del modello, oppure testo
    cambiato fra due giri: impronte per articolo nello stato), con l'atto modificante (versioni AKN /
    changelog-auto). Se c'e' il testo alla data di allineamento (storico.py, cache permanente) si confronta il
    CORPO dell'articolo: cambiate solo le note di aggiornamento → ℹ️, non conta nel verdetto.
 b) REQUISITI PER TIPO: `requisiti-per-tipo.json` (163 n. 7, 480, 342, 281-undecies, D.M. 110/2023 art. 2…),
    tipo dal sidecar (`tipi_requisiti`) o dedotto dal catalogo.
 c) FORMULE OBSOLETE: `formule-obsolete.json` (formula esecutiva, 702-bis, fax del difensore…).
 d) CIFRE contro le TABELLE DATATE: contributo unificato (`parcella/contributo-unificato.json`), soglie di
    competenza del giudice di pace (`changelog-riforme.meta.json` → soglie_competenza); tabelle con la propria
    `prossima_verifica` passata.
 e) METADATI: frontmatter ↔ catalogo ↔ sidecar; tipo d'atto sbagliato («d.lgs. 132/2014» e' un D.L.), refusi
    d'anno («d.P.R. 115/2022»).
 f) DERIVA DEI MOTORI: i profili demo di `atto_giudiziario_docx.py` (e il demo del motore stragiudiziale) sono
    resi in una cartella temporanea e letti con le stesse regole. Un profilo che non si genera e' riportato.

VERDETTI: 🔴 ROSSO (qualcosa e' certamente sbagliato: non usare senza correggere) · 🟡 GIALLO (da rivedere) ·
🟢 VERDE. I rossi deterministici marcano il modello `da_ricontrollare` nel sidecar VIVO (`corpus.py
--patch-json`, mai nel bundle); quando il problema sparisce la marcatura della sentinella si toglie da sola.
Le marcature scritte a mano (sviluppo, avvocato) si tolgono solo con `--allinea` dopo il controllo.

DOVE SCRIVE (fuori dal bundle): `<stato_root>/modelli/report/AAAA-MM.md|.json` (delta: `AAAA-MM-GG-delta.*`),
stato e impronte in `<stato_root>/modelli/sentinella-stato.json`.

LA PARTE LLM (solo sul delta, tell-only): `commands/sentinella-modelli.md` +
`skills/sentinella-normativa/references/sentinella-modelli.md` — un agente per norma MODIFICATA o voce rossa
confronta testo vecchio/nuovo con il passo del modello e propone una correzione; si applica solo dopo il
«sì» dell'avvocato (`--allinea`, consolida-conoscenza).

CLI
  sentinella_modelli.py --giro [--offline] [--senza-motori] [--senza-patch] [--json]
  sentinella_modelli.py --se-scaduto [--quiet]         # fallback del router: gira solo se l'ultimo giro ha > 31 gg
  sentinella_modelli.py --solo-delta                   # solo i modelli toccati da righe nuove del changelog-auto
  sentinella_modelli.py --stato                        # una riga
  sentinella_modelli.py --allinea 114 --motivo "rivisto sul testo vigente, nessuna modifica" [--fonte avvocato]
Funzioni per il router: da_eseguire() -> bool, riga_router() -> str, avvia_in_background() -> bool.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
import zipfile
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8 (accenti, frecce, emoji)
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, WIKI, stato_root_persistente as stato_root  # noqa: E402  (v0.30: stato mensile persistente)

#: Cadenza: il giro e' dovuto quando l'ultimo ha piu' di questi giorni (scheduled task mensile + fallback).
GIORNI_GIRO = 31
#: Throttle del fallback in background: al piu' un avvio ogni N ore.
ORE_THROTTLE = 6

REL_CATALOGO = "modelli/catalogo.json"
REL_META = "modelli/modelli.meta.json"
REL_FORMULE = "modelli/formule-obsolete.json"
REL_REQUISITI = "modelli/requisiti-per-tipo.json"
REL_CU = "parcella/contributo-unificato.json"
REL_CHANGELOG_META = "normativa/changelog-riforme.meta.json"
#: Tabelle datate: se la loro `prossima_verifica` e' passata, i modelli che ne usano le cifre diventano 🟡.
TABELLE_DATATE = (
    ("parcella/contributo-unificato.json", "contributo unificato", "cu"),
    ("normativa/competenza-materia-gdp.json", "competenza per materia del giudice di pace", "gdp"),
    ("normativa/limiti-dm-110-2023.json", "limiti dimensionali D.M. 110/2023", "dm110"),
    ("normativa/pct-specifiche.json", "specifiche tecniche PCT", "pct"),
)
#: Codici completi: un articolo che non c'e' e' un errore del modello, non una lacuna del corpus.
CODICI_COMPLETI = {"cpc", "cc", "cp", "cost", "disp-att-cpc", "preleggi"}

ROSSO, GIALLO, INFO = "🔴", "🟡", "ℹ️"
VERDETTI = ("VERDE", "GIALLO", "ROSSO")
ICONA = {"VERDE": "🟢", "GIALLO": "🟡", "ROSSO": "🔴"}


# ============================================================ percorsi e I/O

def dir_sentinella() -> Path:
    return stato_root() / "modelli"


def file_stato() -> Path:
    return dir_sentinella() / "sentinella-stato.json"


def dir_report() -> Path:
    return dir_sentinella() / "report"


def _oggi() -> _dt.date:
    return _dt.date.today()


def _d(s):
    try:
        return _dt.date.fromisoformat(str(s)[:10]) if s else None
    except ValueError:
        return None


def leggi_json_vivo(rel: str) -> dict:
    """Il file-dati nella versione VIVA (bundle + patch del corpus vivo); il bundle se il corpus non c'e'."""
    try:
        import corpus as _cp
        return json.loads(_cp.risolvi(rel))
    except (Exception, SystemExit):
        pass
    p = WIKI / rel
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except ValueError:
        return {}


def _leggi_testo_modello(rel_file: str) -> str:
    """Testo della scheda: v0.36 la copia corretta dalle sentinelle automatiche (sincronizzata dal corpus pubblico) se
    vale, altrimenti il bundle; se manca (modello aggiunto nel corpus vivo) dal corpus."""
    try:
        import aree as _ar
        s = _ar.file_sincronizzato(rel_file)
        if s is not None:
            return s.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = ROOT / rel_file
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    try:
        import corpus as _cp
        return _cp.risolvi(rel_file.replace("wiki-studio/", "", 1))
    except (Exception, SystemExit):
        return ""


REL_STATO_SENTINELLE = "wiki-studio/sentinelle/modelli-stato.json"


def _quando(st: dict) -> str:
    return str(st.get("ultimo_giro_completo_il") or st.get("ultimo_giro") or "")


def stato() -> dict:
    """Lo stato del giro: quello locale o, v0.36, quello dell'ultimo giro delle sentinelle automatiche (copia del
    corpus pubblico), il piu' recente dei due."""
    p = file_stato()
    try:
        locale = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (ValueError, OSError):
        locale = {}
    try:
        import aree as _ar
        action = _ar.leggi_json(REL_STATO_SENTINELLE) or {}
    except Exception:
        action = {}
    return action if isinstance(action, dict) and _quando(action) > _quando(locale) else locale


def _salva_stato(st: dict) -> None:
    p = file_stato()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(p))


# ============================================================ lettura della scheda

_RX_FM = re.compile(r"^---\s*\n(\{.*?\})\s*\n---\s*\n", re.S)
_RX_FAC = re.compile(r"## Testo del modello[^\n]*\n```[^\n]*\n(.*?)\n```", re.S)


def scomponi_scheda(testo: str) -> dict:
    """{frontmatter, facsimile, errore}: il fac-simile e' il blocco ``` dopo «## Testo del modello»."""
    out = {"frontmatter": None, "facsimile": "", "errore": ""}
    m = _RX_FM.match(testo)
    if m:
        try:
            out["frontmatter"] = json.loads(m.group(1))
        except ValueError as e:
            out["errore"] = f"frontmatter JSON illeggibile ({e})"
    else:
        out["errore"] = "frontmatter assente"
    f = _RX_FAC.search(testo)
    if f:
        out["facsimile"] = f.group(1)
    else:
        out["errore"] = (out["errore"] + "; " if out["errore"] else "") + "sezione «Testo del modello» assente"
    return out


def data_base(meta: dict, fm: dict = None) -> str:
    """Data di ALLINEAMENTO del testo del modello alle norme: `norme_allineate_al` del sidecar; altrimenti il primo
    giorno del mese del testo (`data_formulario`); altrimenti `verificato_il`. Ogni modifica di norma successiva va guardata."""
    for k in ("norme_allineate_al",):
        if meta.get(k):
            return str(meta[k])[:10]
    df = (fm or {}).get("data_formulario") or meta.get("data_formulario")
    if df and re.match(r"^\d{4}-\d{2}$", str(df)):
        return f"{df}-01"
    if df and _d(df):
        return str(df)[:10]
    return str(meta.get("verificato_il") or "1900-01-01")[:10]


# ============================================================ ambito e tipi (requisiti)

def classifica_automatica(m: dict) -> tuple:
    """(ambito, tipi_requisiti) dedotti dal catalogo — solo per i modelli senza classificazione nel sidecar."""
    tipo = str(m.get("tipo_atto") or "").lower()
    rito = str(m.get("rito") or "").lower()
    titolo = str(m.get("titolo") or "").lower()
    documento = rito in ("n/a", "mediazione", "negoziazione assistita") or tipo in (
        "informativa", "procura", "clausola", "convenzione", "verbale", "piano genitoriale", "adesione")
    ambito = "documento" if documento else "giudiziario"
    tipi = []
    if ambito == "giudiziario":
        if "precetto" in tipo and "precetto" in titolo and "opposizione" not in titolo:
            tipi = ["precetto"]
        elif tipo in ("atto di citazione",) and "testimon" not in titolo and "nullit" not in titolo:
            tipi = ["citazione"]
        elif "appello" in tipo and titolo.startswith("appello"):
            tipi = ["appello"]
        elif "cassazione" in tipo and ("ricorso" in titolo or "controricorso" in titolo):
            tipi = ["cassazione"]
        elif "comparsa di costituzione" in tipo:
            tipi = ["comparsa"]
        elif tipo.startswith("ricorso"):
            tipi = ["ricorso-semplificato"] if rito.startswith("semplificato") else ["ricorso"]
        elif tipo == "memoria" and "difensiva" in titolo:
            tipi = ["memoria-difensiva"]
    return ambito, tipi


def classifica(m: dict, meta: dict) -> tuple:
    auto = classifica_automatica(m)
    ambito = meta.get("ambito") or auto[0]
    tipi = meta.get("tipi_requisiti") if isinstance(meta.get("tipi_requisiti"), list) else auto[1]
    return ambito, list(tipi)


# ============================================================ estrazione delle norme citate

_SUFF = (r"(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|nonies|decies|undecies|duodecies|terdecies|"
         r"quaterdecies|quinquiesdecies|sexiesdecies|septiesdecies|octiesdecies)")
_TOK = rf"\d+(?:\s*-?\s*{_SUFF}\b)?(?:\.\d+)?"
_TOKL = rf"{_TOK}(?!\s*°|\d)"
_RX_ART = re.compile(rf"\b(?:articol[oi]|artt?\.?)\s*(?:n\.\s*)?({_TOKL}(?:\s*(?:,|\be\b|\bed\b)\s*{_TOKL})*)", re.I)
_RX_RIEMPI = re.compile(
    r"^(?:\s*(?:,|;|\be\s+(?:segg?|ss)\.?|\bss\.|\bsegg?\.|(?:comma|co\.|c\.)\s*\d+[-\w]*(?:\s*,\s*\d+)*|"
    r"(?:n(?:\.|umero)|nn\.)\s*\d+[-\w]*\)?|lett(?:era|\.)?\s*[a-z]\)?|\d+°\s*comma|"
    r"(?:primo|secondo|terzo|quarto|quinto|sesto|settimo|ottavo|nono|decimo|ultimo)\s+(?:comma|periodo)|"
    r"(?:primo|secondo|terzo|quarto|ultimo)\s+periodo|periodo|del(?:la|lo|le|l'|l’)?|dei|degli|della|delle|cit\.|"
    r"\(\s*|\s+))*", re.I)
_TIPO_NUM = (r"d\.\s?lgs\.?|d\.\s?leg\.?|d\.\s?l\.?|d\.\s?p\.\s?r\.?|d\.\s?m\.?|l\.|legge|decreto\s+legislativo|"
             r"decreto[- ]legge|decreto\s+del\s+presidente\s+della\s+repubblica|decreto\s+ministeriale")
_RX_ATTO = re.compile(
    r"^(?:(?P<dispatt>disp(?:osizioni)?\.?\s*(?:di\s+|per\s+l'?\s*)?att(?:uazione|\.)?\s*(?:del\s+)?"
    r"(?:c\.\s?p\.\s?c\.?|cod\.\s?proc\.\s?civ\.?|codice\s+di\s+procedura\s+civile))"
    r"|(?P<dispattcc>disp(?:osizioni)?\.?\s*(?:di\s+|per\s+l'?\s*)?att(?:uazione|\.)?\s*(?:del\s+)?"
    r"(?:c\.\s?c\.?|cod\.\s?civ\.?|codice\s+civile))"
    r"|(?P<cpc>c\.\s?p\.\s?c\.?|cod\.\s?proc\.\s?civ\.?|codice\s+di\s+procedura\s+civile|cpc\b)"
    r"|(?P<cc>c\.\s?c\.?(?!\s?i)|cod\.\s?civ\.?|codice\s+civile)"
    r"|(?P<cp>c\.\s?p\.(?!\s?c)|cod\.\s?pen\.?|codice\s+penale)"
    r"|(?P<cost>cost\.|costituzione(?=\s*[,;.)]|\s*$))"
    rf"|(?P<num>(?P<tipo>{_TIPO_NUM})\s*(?:n\.\s*)?(?P<n>\d+)\s*/\s*(?P<a>\d{{4}}))"
    rf"|(?P<lungo>(?P<tipo2>{_TIPO_NUM})\s+\d{{1,2}}\s+[a-z]+\s+(?P<a2>\d{{4}}),?\s*n\.\s*(?P<n2>\d+))"
    r")", re.I)
_RX_ATTO_SOLO = re.compile(
    rf"\b(?P<tipo>{_TIPO_NUM})\s*(?:n\.\s*)?(?P<n>\d+)\s*/\s*(?P<a>\d{{4}})"
    rf"|\b(?P<tipo2>{_TIPO_NUM})\s+\d{{1,2}}\s+[a-z]+\s+(?P<a2>\d{{4}}),?\s*n\.\s*(?P<n2>\d+)", re.I)

_TIPI_CANON = {"dlgs": "d.lgs.", "dl": "d.l.", "dpr": "d.p.r.", "dm": "d.m.", "l": "l."}
_TIPI_NOME = {"dlgs": "D.Lgs.", "dl": "D.L.", "dpr": "d.P.R.", "dm": "D.M.", "l": "L."}


def _tipo_canonico(t: str) -> str:
    t = re.sub(r"\s+", " ", t.lower().strip())
    if t.startswith("decreto legislativo") or re.match(r"d\.\s?l(?:gs|eg)", t):
        return "dlgs"
    if t.startswith("decreto-legge") or t.startswith("decreto legge") or re.match(r"d\.\s?l\.?$", t):
        return "dl"
    if t.startswith("decreto del presidente") or re.match(r"d\.\s?p\.\s?r", t):
        return "dpr"
    if t.startswith("decreto ministeriale") or re.match(r"d\.\s?m", t):
        return "dm"
    return "l"


def _norm_token(t: str) -> str:
    s = re.sub(r"\s+", "-", t.lower().strip())
    s = re.sub(r"-+", "-", s)
    s = re.sub(r"(\d)(" + _SUFF + r")", r"\1-\2", s)
    return s.replace("nonies", "novies")


def _alias() -> dict:
    try:
        import codice_locale as cl
        return dict(cl.ALIAS), set(cl.CODICI)
    except Exception:
        return {}, set()


class FonteNorme:
    """Accesso al corpus locale datato e allo storico. Nei test si sostituisce con un finto (stessi metodi)."""

    def __init__(self, offline: bool = False):
        self.offline = offline
        self._rete_ko = False
        self._atti = {}
        self.alias, self.slugs = _alias()

    # -- risoluzione dell'atto
    def slug_numerato(self, tipo: str, n: str, anno: str):
        chiave = f"{_TIPI_CANON[tipo]} {int(n)}/{anno}"
        if chiave in self.alias:
            return self.alias[chiave]
        s = f"{tipo}-{int(n)}-{anno}"
        return s if s in self.slugs else None

    # -- snapshot
    def atto(self, slug: str):
        """{"meta", "articoli": {token: {"testo","rubrica","vigore_da"}}} o None (una lettura per atto)."""
        if slug in self._atti:
            return self._atti[slug]
        out = None
        try:
            import codice_locale as cl
            base, dati = cl._indice(slug)
            if dati:
                arts = dati.get("articoli") or {}
                files = list((dati.get("_meta") or {}).get("file") or []) or sorted({v.get("file") for v in arts.values() if v.get("file")})
                testi = {}
                rx = re.compile(r"^### Art\. (\S+)(?: — [^\n]*)?\n(?:<!--[^\n]*-->\n)?\n?(.*?)(?=^### Art\. |\Z)", re.M | re.S)
                for f in files:
                    p = Path(base) / f
                    if p.exists():
                        for m in rx.finditer(p.read_text(encoding="utf-8")):
                            testi[m.group(1)] = m.group(2).strip()
                articoli = {t: {"testo": testi.get(t, ""), "rubrica": v.get("rubrica", ""), "vigore_da": v.get("vigore_da") or ""}
                            for t, v in arts.items()}
                out = {"meta": dati.get("_meta") or {}, "articoli": articoli, "dati": dati}
        except Exception:
            out = None
        self._atti[slug] = out
        return out

    def atto_modificante(self, slug: str, data: str):
        a = self.atto(slug)
        if not a or not data:
            return None
        try:
            import codice_locale as cl
            v = cl.versione_alla_data(slug, data, a["dati"])
            return (v or {}).get("atto_modificante")
        except Exception:
            return None

    def sigla(self, slug: str) -> str:
        fisse = {"cpc": "c.p.c.", "cc": "c.c.", "cp": "c.p.", "disp-att-cpc": "disp. att. c.p.c.", "cost": "Cost."}
        if slug in fisse:
            return fisse[slug]
        for k, v in self.alias.items():
            if v == slug and re.search(r"\d+/\d{4}", k):
                return k
        return slug

    def testo_storico(self, slug: str, token: str, data: str):
        """(testo, motivo): il testo dell'articolo in vigore a `data` (cache permanente; rete una volta)."""
        try:
            import storico as st
            r = st.recupera(f"art. {token} {self.sigla(slug)}", data, offline=(self.offline or self._rete_ko), slug=slug)
        except Exception as e:  # pragma: no cover - difensivo
            return None, f"storico non disponibile ({e.__class__.__name__})"
        if r.get("verdetto") == "OK":
            return r.get("testo") or "", ""
        motivo = str(r.get("motivo") or "")
        if "fetch fallito" in motivo:
            self._rete_ko = True   # interruttore: una rete giu' non fa aspettare N timeout
        return None, motivo


def estrai_norme(testo: str, fonte: FonteNorme) -> list:
    """[{rif, slug, art|None, n, anno, tipo, atto_txt}] citati nel testo (articoli con atto esplicito + atti numerati)."""
    out, visti = [], set()
    for m in _RX_ART.finditer(testo):
        coda = testo[m.end(): m.end() + 160]
        r = _RX_RIEMPI.match(coda)
        resto = coda[r.end():] if r else coda
        a = _RX_ATTO.match(resto)
        if not a:
            continue
        tok_list = [t for t in re.split(r"\s*(?:,|\be\b|\bed\b)\s*", m.group(1), flags=re.I) if t.strip()]
        slug, tipo, n, anno = None, None, None, None
        if a.group("dispatt"):
            slug = "disp-att-cpc"
        elif a.group("dispattcc"):
            slug = "disp-att-cc"
        elif a.group("cpc"):
            slug = "cpc"
        elif a.group("cc"):
            slug = "cc"
        elif a.group("cp"):
            slug = "cp"
        elif a.group("cost"):
            slug = "cost"
        else:
            tipo = _tipo_canonico(a.group("tipo") or a.group("tipo2"))
            n = a.group("n") or a.group("n2")
            anno = a.group("a") or a.group("a2")
            slug = fonte.slug_numerato(tipo, n, anno)
        for t in tok_list:
            tok = _norm_token(t)
            chiave = (slug or f"{tipo}:{n}/{anno}", tok)
            if chiave in visti:
                continue
            visti.add(chiave)
            out.append({"rif": f"art. {tok} {a.group(0).strip()}", "slug": slug, "art": tok, "tipo": tipo,
                        "n": n, "anno": anno, "atto_txt": a.group(0).strip()})
    for m in _RX_ATTO_SOLO.finditer(testo):
        tipo = _tipo_canonico(m.group("tipo") or m.group("tipo2"))
        n, anno = m.group("n") or m.group("n2"), m.group("a") or m.group("a2")
        slug = fonte.slug_numerato(tipo, n, anno)
        chiave = (slug or f"{tipo}:{n}/{anno}", None)
        if chiave in visti:
            continue
        visti.add(chiave)
        out.append({"rif": m.group(0).strip(), "slug": slug, "art": None, "tipo": tipo, "n": n, "anno": anno,
                    "atto_txt": m.group(0).strip()})
    return out


#: Leggi, decreti-legge, decreti legislativi e d.P.R. condividono UNA numerazione annuale (Raccolta ufficiale):
#: se il corpus ha il D.L. 132/2014, un «D.Lgs. 132/2014» e' certamente un errore di tipo. I D.M. hanno numeri propri.
_TIPI_NUMERAZIONE_UNICA = ("dlgs", "dl", "l", "dpr")


def _atto_errato(r: dict, fonte: FonteNorme):
    """(gravita, messaggio) per un atto numerato fuori corpus: tipo sbagliato (🟡, certo) o anno forse sbagliato
    (ℹ️: l'atto citato puo' esistere davvero fuori dal corpus; 🟡 solo se l'anno e' impossibile). None se nulla."""
    if not r.get("tipo") or r.get("slug"):
        return None
    if r["tipo"] in _TIPI_NUMERAZIONE_UNICA:
        for t in _TIPI_NUMERAZIONE_UNICA:
            if t != r["tipo"] and fonte.slug_numerato(t, r["n"], r["anno"]):
                return (GIALLO, f"«{r['atto_txt']}»: il n. {r['n']}/{r['anno']} e' un {_TIPI_NOME[t]} (numerazione unica "
                                f"della Raccolta ufficiale), non un {_TIPI_NOME[r['tipo']]}")
    impossibile = not (1861 <= int(r["anno"]) <= _oggi().year)
    for anno in range(1940, _oggi().year + 1):
        a = str(anno)
        if a != r["anno"] and sum(1 for x, y in zip(a, r["anno"]) if x != y) == 1 and fonte.slug_numerato(r["tipo"], r["n"], a):
            return (GIALLO if impossibile else INFO,
                    f"«{r['atto_txt']}»: " + ("anno impossibile, " if impossibile else "atto fuori corpus; ") +
                    f"nel corpus c'e' {_TIPI_NOME[r['tipo']]} {r['n']}/{a}: se era questo, correggere l'anno")
    if impossibile:
        return (GIALLO, f"«{r['atto_txt']}»: anno impossibile")
    return None


# ============================================================ corpo di un articolo e impronte

def _norm_testo(t: str) -> str:
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower().replace("’", "'").replace("'", "")
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())


def corpo_articolo(testo: str, rubrica: str = "") -> str:
    """Il CORPO normalizzato (senza intestazione, rubrica, numerazione dei commi, note di aggiornamento e marcatori
    di modifica): uguale fra testo locale AKN («e'», commi senza numero) e storico HTML («è», «1.», «a)»)."""
    rub = _norm_testo(rubrica) if rubrica else ""
    righe = []
    for i, r in enumerate(str(testo or "").splitlines()):
        if re.match(r"^\s*-{5,}", r) or re.match(r"^\s*AGGIORNAMENTO\s*\(", r) or re.match(r"^\s*articolo precedente", r, re.I):
            break
        # intestazione «Art. N.» e rubrica «(…)» dello storico HTML: mai un paragrafo «((…))» di modifica
        if i < 4 and (re.match(r"^\s*Art\.\s*\S+\s*$", r) or re.match(r"^\s*\((?!\()[^()]{1,160}\)\.?\s*$", r)
                      or (rub and _norm_testo(r) == rub)):
            continue
        r = re.sub(r"^\s*(?:\d+(?:-[a-z]+)?\.(?!\d)|[a-z](?:-[a-z]+)?\))\s+", "", r)
        righe.append(r)
    t = "\n".join(righe)
    t = re.sub(r"\(\(\s*\d{1,3}[a-z]?\s*\)\)|\(\s*\d{1,3}[a-z]?\s*\)", " ", t)
    t = t.replace("((", " ").replace("))", " ")
    return _norm_testo(t)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _note(testo: str) -> str:
    m = re.search(r"AGGIORNAMENTO\s*\(\d+\)(.*)$", str(testo or ""), re.S)
    return " ".join(m.group(0).split())[-400:] if m else ""


def _diff_breve(a: str, b: str, massimo: int = 360) -> str:
    import difflib
    wa, wb = a.split(), b.split()
    pezzi = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        tolto, messo = " ".join(wa[i1:i2]), " ".join(wb[j1:j2])
        pezzi.append((f"− «{tolto[:140]}» " if tolto else "") + (f"+ «{messo[:200]}»" if messo else ""))
    s = " · ".join(pezzi)
    return s[:massimo] + ("…" if len(s) > massimo else "")


# ============================================================ regole

def carica_regole() -> dict:
    return {"formule": leggi_json_vivo(REL_FORMULE), "requisiti": leggi_json_vivo(REL_REQUISITI),
            "cu": leggi_json_vivo(REL_CU), "changelog": leggi_json_vivo(REL_CHANGELOG_META)}


def _issue(regola: str, gravita: str, messaggio: str, **extra) -> dict:
    d = {"regola": regola, "gravita": gravita, "messaggio": messaggio}
    d.update({k: v for k, v in extra.items() if v not in (None, "", [])})
    return d


def _estratto(testo: str, m) -> str:
    a, b = max(0, m.start() - 50), min(len(testo), m.end() + 50)
    return " ".join(testo[a:b].split())


def controlla_formule(testo: str, ambito: str, formule: dict, oggi: _dt.date) -> list:
    out = []
    for v in (formule or {}).get("voci", []):
        if ambito not in (v.get("si_applica_a") or []):
            continue
        dal = _d(v.get("dal"))
        if dal and dal > oggi:
            continue
        try:
            m = re.search(v.get("regex") or "(?!)", testo, re.I)
        except re.error:
            continue
        if m:
            out.append(_issue("formula:" + str(v.get("id")), v.get("gravita") or GIALLO,
                              f"formula superata «{' '.join(m.group(0).split())}» ({v.get('norma')}, dal {v.get('dal')})",
                              correzione=v.get("sostituire_con"), estratto=_estratto(testo, m), norma=v.get("norma")))
    return out


def controlla_requisiti(testo: str, tipi: list, requisiti: dict) -> list:
    out = []
    per_tipo = (requisiti or {}).get("tipi") or {}
    visti = set()
    for t in tipi:
        for r in per_tipo.get(t) or []:
            if r.get("id") in visti:
                continue
            visti.add(r.get("id"))
            try:
                ok = re.search(r.get("regex") or "(?!)", testo, re.I | re.S)
            except re.error:
                continue
            if not ok:
                out.append(_issue("requisito:" + str(r.get("id")), r.get("gravita") or GIALLO,
                                  f"manca: {r.get('descrizione')} ({r.get('norma')})", norma=r.get("norma"),
                                  articolo=r.get("articolo"), tipo=t))
    return out


def _euro(s: str):
    s = s.strip().rstrip(".,")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.match(r"^\d{1,3}(?:\.\d{3})+$", s):
        s = s.replace(".", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def _fmt(x) -> str:
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def controlla_cifre(testo: str, tipi: list, regole: dict) -> list:
    """Cifre del contributo unificato e soglie del giudice di pace contro le tabelle datate."""
    out = []
    cu = regole.get("cu") or {}
    scaglioni = cu.get("scaglioni") or []
    valori_cu = {round(float(s["cu"]), 2) for s in scaglioni if s.get("cu") is not None}
    if valori_cu:
        # righe di tabella «fino a € X … € a» (primo grado)
        for m in re.finditer(r"fino\s+a\s+€\s*([\d.]+(?:,\d{2})?)\s+€\s*([\d.]+(?:,\d{2})?)", testo, re.I):
            lim, imp = _euro(m.group(1)), _euro(m.group(2))
            giusto = next((s for s in scaglioni if s.get("a") is not None and round(float(s["a"]), 2) == lim), None)
            if giusto and imp is not None and round(float(giusto["cu"]), 2) != imp:
                out.append(_issue("cifre:cu-scaglione", ROSSO, f"C.U. per valore fino a € {_fmt(lim)}: il modello dice € {_fmt(imp)}, "
                                  f"la tabella € {_fmt(float(giusto['cu']))} (art. 13 co. 1 d.P.R. 115/2002)", estratto=_estratto(testo, m)))
        # righe con tre importi: primo grado, impugnazione (+ metà), cassazione (doppio) — art. 13 co. 1-bis
        for m in re.finditer(r"(?=€\s*([\d.]+,\d{2})\s+€\s*([\d.]+,\d{2})\s+€\s*([\d.]+,\d{2}))", testo):
            a, b, c = (_euro(m.group(i)) for i in (1, 2, 3))
            if a in valori_cu:
                if b != round(a * 1.5, 2):
                    out.append(_issue("cifre:cu-impugnazione", ROSSO, f"C.U. impugnazione per € {_fmt(a)}: il modello dice € {_fmt(b)}, "
                                      f"dovuto € {_fmt(round(a * 1.5, 2))} (aumento della metà, art. 13 co. 1-bis)", estratto=_estratto(testo, m)))
                if c != round(a * 2, 2):
                    out.append(_issue("cifre:cu-cassazione", ROSSO, f"C.U. cassazione per € {_fmt(a)}: il modello dice € {_fmt(c)}, "
                                      f"dovuto € {_fmt(round(a * 2, 2))} (raddoppio, art. 13 co. 1-bis)", estratto=_estratto(testo, m)))
        ind = (cu.get("indeterminabile") or {}).get("cu")
        m = re.search(r"valore\s+indeterminabile\s+€\s*([\d.]+,\d{2})", testo, re.I)
        if ind and m and _euro(m.group(1)) != round(float(ind), 2):
            out.append(_issue("cifre:cu-indeterminabile", ROSSO, f"C.U. valore indeterminabile: il modello dice € {m.group(1)}, "
                              f"la tabella € {_fmt(float(ind))}", estratto=_estratto(testo, m)))
        rid = cu.get("riduzioni") or {}
        fissi = (("esecuzione\\s+immobiliare", (rid.get("esecuzione_immobiliare") or {}).get("cu_fisso"), "esecuzione immobiliare"),
                 ("opposizione\\s+agli\\s+atti\\s+esecutivi", (rid.get("opposizione_atti_esecutivi") or {}).get("cu_fisso"), "opposizione agli atti esecutivi"))
        for rx, atteso, nome in fissi:
            if atteso is None:
                continue
            for m in re.finditer(rx + r"[^€\n]{0,40}€\s*([\d.]+,\d{2})", testo, re.I):
                if _euro(m.group(1)) != round(float(atteso), 2):
                    out.append(_issue("cifre:cu-fisso", ROSSO, f"C.U. {nome}: il modello dice € {m.group(1)}, la tabella € {_fmt(float(atteso))} "
                                      "(art. 13 co. 2 d.P.R. 115/2002)", estratto=_estratto(testo, m)))
        # dichiarazione valore + C.U. in un atto compilato (motori): lo scaglione deve tornare
        mv = re.search(r"valore[^€\n]{0,60}€\s*([\d.]+(?:,\d{2})?)", testo, re.I)
        mc = re.search(r"contributo\s+unificato[^€\n]{0,60}€\s*([\d.]+(?:,\d{2})?)", testo, re.I)
        if mv and mc:
            val, dich = _euro(mv.group(1)), _euro(mc.group(1))
            s = next((s for s in scaglioni if val is not None and float(s["da"]) <= val and (s.get("a") is None or val <= float(s["a"]))), None)
            if s and dich is not None:
                base = round(float(s["cu"]), 2)
                ammessi = {base}
                if "ridotto" in tipi:
                    ammessi.add(round(base / 2, 2))
                if "appello" in tipi:
                    ammessi = {round(base * 1.5, 2)}
                if "cassazione" in tipi:
                    ammessi = {round(base * 2, 2)}
                if dich not in ammessi:
                    out.append(_issue("cifre:cu-dichiarato", ROSSO, f"C.U. dichiarato € {_fmt(dich)} per un valore di € {_fmt(val)}: "
                                      f"scaglione lett. {s.get('lettera')}) = € {_fmt(base)} (art. 13 d.P.R. 115/2002)",
                                      estratto=_estratto(testo, mc)))
    soglie = (regole.get("changelog") or {}).get("soglie_competenza") or {}
    for chiave, contesto in (("giudice_di_pace_valore_generale_eur", r"beni\s+mobili|competenza\s+(?:per\s+valore\s+)?del\s+giudice\s+di\s+pace"),
                             ("giudice_di_pace_rc_auto_eur", r"circolazione|sinistr")):
        s = soglie.get(chiave) or {}
        if not s.get("previgente_eur"):
            continue
        prev = float(s["previgente_eur"])
        for m in re.finditer(r"giudice\s+di\s+pace[^.;\n]{0,160}?(?:euro|€)\s*([\d.]+(?:,\d{2})?)", testo, re.I):
            v = _euro(m.group(1))
            if v == prev and re.search(contesto, testo[max(0, m.start() - 200): m.end() + 200], re.I):
                out.append(_issue("cifre:soglia-gdp", ROSSO, f"soglia di competenza del giudice di pace previgente (€ {_fmt(prev)}): "
                                  f"vigente € {_fmt(float(s['valore']))} dal {s.get('vigente_da')} ({s.get('fonte')})",
                                  estratto=_estratto(testo, m)))
    return out


def usa_tabelle(testo: str) -> set:
    t = testo.lower()
    usate = set()
    if re.search(r"contributo\s+unificato[^\n]{0,80}€\s*\d|€\s*\d[\d.]*,\d{2}\s+€\s*\d", t):
        usate.add("cu")
    if re.search(r"giudice\s+di\s+pace[^.\n]{0,160}(?:euro|€)\s*\d", t):
        usate.add("gdp")
    return usate


def tabelle_scadute(oggi: _dt.date) -> list:
    out = []
    for rel, nome, sigla in TABELLE_DATATE:
        d = leggi_json_vivo(rel)
        meta = d.get("_meta") if isinstance(d, dict) else None
        if not isinstance(meta, dict):
            continue
        pv = _d(meta.get("prossima_verifica"))
        if pv and pv < oggi:
            out.append({"tabella": rel, "nome": nome, "sigla": sigla, "prossima_verifica": pv.isoformat(),
                        "verificato_il": meta.get("verificato_il")})
    return out


# ============================================================ norme citate

def controlla_norme(refs: list, dove: str, base: str, fonte: FonteNorme, stato_art: dict, cl_auto: list) -> tuple:
    """(issue, norme[]) — esito di ogni riferimento del modello."""
    issue, norme = [], []
    for r in refs:
        slug, art = r.get("slug"), r.get("art")
        rec = {"rif": r["rif"], "slug": slug, "art": art, "dove": dove}
        if not slug:
            errato = _atto_errato(r, fonte)
            if errato:
                rec["esito"] = "ATTO_ERRATO" if errato[0] == GIALLO else "FUORI_CORPUS"
                issue.append(_issue("norme:atto-errato", errato[0], errato[1], dove=dove))
            else:
                rec["esito"] = "FUORI_CORPUS"
            norme.append(rec)
            continue
        if not art:
            rec["esito"] = "ATTO_OK" if fonte.atto(slug) else "FUORI_CORPUS"
            norme.append(rec)
            continue
        atto = fonte.atto(slug)
        if not atto:
            rec["esito"] = "FUORI_CORPUS"
            norme.append(rec)
            continue
        voce = atto["articoli"].get(art)
        if voce is None:
            rec["esito"] = "NON_TROVATA"
            grav = ROSSO if (slug in CODICI_COMPLETI and dove == "facsimile") else GIALLO
            issue.append(_issue("norme:non-trovata", grav, f"{r['rif']}: articolo inesistente nel corpus ({atto['meta'].get('nome') or slug}, "
                                f"snapshot {atto['meta'].get('snapshot')})", dove=dove, norma=r["rif"]))
            norme.append(rec)
            continue
        testo = voce.get("testo") or ""
        rec["vigore_da"] = voce.get("vigore_da") or ""
        if re.match(r"^\(?\(?\s*ARTICOLO\s+ABROGATO", testo.strip(), re.I):
            rec["esito"] = "ABROGATA"
            issue.append(_issue("norme:abrogata", ROSSO if dove == "facsimile" else GIALLO,
                                f"{r['rif']}: ARTICOLO ABROGATO ({' '.join(testo.split())[:160]})", dove=dove, norma=r["rif"]))
            norme.append(rec)
            continue
        chiave = f"{slug}:{art}"
        sa = stato_art.get(chiave) or {}
        cambi = [x for x in (rec["vigore_da"], sa.get("cambiato_il")) if x]
        modifica = max(cambi) if cambi else ""
        if modifica and modifica > base:
            rec["esito"] = "MODIFICATA"
            am = None
            righe_auto = [x for x in cl_auto if x.get("slug") == slug and x.get("articolo") == art]
            if righe_auto:
                am = righe_auto[0].get("atto_modificante")
            am = am or fonte.atto_modificante(slug, rec["vigore_da"] or modifica)
            rec.update({"modifica_dal": modifica, "atto_modificante": am})
            vecchio, motivo = fonte.testo_storico(slug, art, base)
            if vecchio is not None:
                a, b = corpo_articolo(vecchio, voce.get("rubrica") or ""), corpo_articolo(testo, voce.get("rubrica") or "")
                if a == b:
                    rec["esito"] = "MODIFICATA_SOLO_NOTE"
                    rec["nota"] = _note(testo)[:300]
                    issue.append(_issue("norme:solo-note", INFO, f"{r['rif']}: cambiate solo le note di aggiornamento "
                                        f"({am or 'atto non indicato'}, dal {modifica}); corpo dell'articolo identico al {base}",
                                        dove=dove, norma=r["rif"]))
                else:
                    rec["diff"] = _diff_breve(a, b)
                    issue.append(_issue("norme:modificata", GIALLO, f"{r['rif']}: testo cambiato dopo il modello ({am or 'atto non indicato'}, "
                                        f"in vigore dal {modifica}; modello allineato al {base})", dove=dove, norma=r["rif"],
                                        diff=rec["diff"], atto_modificante=am))
            else:
                rec["storico"] = motivo[:160]
                issue.append(_issue("norme:modificata", GIALLO, f"{r['rif']}: articolo modificato dopo il modello ({am or 'atto non indicato'}, "
                                    f"in vigore dal {modifica}; modello allineato al {base}); testo precedente non disponibile "
                                    "(storico offline): confrontare a mano", dove=dove, norma=r["rif"], atto_modificante=am))
        else:
            rec["esito"] = "OK"
        norme.append(rec)
    return issue, norme


def aggiorna_impronte(fonte: FonteNorme, chiavi: set, stato_art: dict, oggi: _dt.date) -> dict:
    """Impronte del CORPO di ogni articolo citato: un corpo diverso dal giro precedente = `cambiato_il` oggi."""
    nuovo = dict(stato_art)
    for chiave in sorted(chiavi):
        slug, art = chiave.split(":", 1)
        atto = fonte.atto(slug)
        voce = (atto or {}).get("articoli", {}).get(art) if atto else None
        if not voce:
            continue
        sha = _sha(corpo_articolo(voce.get("testo") or "", voce.get("rubrica") or ""))
        prec = stato_art.get(chiave) or {}
        rec = {"sha": sha, "vigore_da": voce.get("vigore_da") or "", "visto_il": oggi.isoformat(),
               "snapshot": (atto.get("meta") or {}).get("snapshot"), "cambiato_il": prec.get("cambiato_il")}
        if prec.get("sha") and prec["sha"] != sha:
            rec["cambiato_il"] = oggi.isoformat()
            rec["sha_prima"] = prec["sha"]
        nuovo[chiave] = rec
    return nuovo


# ============================================================ metadati

CAMPI_FM_CAT = ("titolo", "tipo_atto", "rito", "fase", "materia", "norme_chiave", "changelog_deps", "volatilita")


def controlla_metadati(m: dict, fm: dict, meta: dict, fonte: FonteNorme) -> list:
    out = []
    if not meta:
        out.append(_issue("metadati:sidecar", ROSSO, "modello assente da modelli.meta.json (freschezza non tracciata)"))
    if fm:
        for k in CAMPI_FM_CAT:
            a, b = fm.get(k), m.get(k)
            if k == "norme_chiave":
                a, b = sorted(a or []), sorted(b or [])
            if a != b and not (a in (None, "", []) and b in (None, "", [])):
                out.append(_issue("metadati:incoerenza", GIALLO, f"campo «{k}» diverso fra frontmatter ({str(a)[:60]}) e catalogo ({str(b)[:60]})"))
        if str(fm.get("id")) != str(m.get("id")):
            out.append(_issue("metadati:incoerenza", GIALLO, f"id del frontmatter {fm.get('id')} ≠ catalogo {m.get('id')}"))
    if meta:
        for k in ("titolo", "file"):
            if meta.get(k) and m.get(k) and meta.get(k) != m.get(k):
                out.append(_issue("metadati:incoerenza", GIALLO, f"campo «{k}» diverso fra sidecar ({str(meta.get(k))[:60]}) e catalogo ({str(m.get(k))[:60]})"))
        if sorted(meta.get("changelog_deps") or []) != sorted(m.get("changelog_deps") or []):
            out.append(_issue("metadati:incoerenza", GIALLO, "changelog_deps diverse fra sidecar e catalogo"))
    for nc in (m.get("norme_chiave") or []):
        for r in estrai_norme(nc, fonte):
            e = _atto_errato(r, fonte)
            if e:
                out.append(_issue("metadati:norme-chiave", e[0], f"norme_chiave: {e[1]}"))
    return out


# ============================================================ un modello

def valuta_modello(m: dict, meta: dict, regole: dict, fonte: FonteNorme, stato_art: dict, cl_auto: list,
                   oggi: _dt.date, scadute: list) -> dict:
    testo = _leggi_testo_modello(m.get("file") or "")
    sch = scomponi_scheda(testo) if testo else {"frontmatter": None, "facsimile": "", "errore": "file della scheda mancante"}
    fac, fm = sch["facsimile"], sch["frontmatter"] or {}
    ambito, tipi = classifica(m, meta)
    base = data_base(meta, fm)
    issue = []
    if sch["errore"]:
        issue.append(_issue("scheda:struttura", ROSSO, sch["errore"]))
    # (a) norme citate: fac-simile, poi norme_chiave (quelle non gia' nel fac-simile)
    refs_fac = estrai_norme(fac, fonte)
    visti = {(r.get("slug"), r.get("art")) for r in refs_fac}
    refs_nc = [r for nc in (m.get("norme_chiave") or []) for r in estrai_norme(nc, fonte) if (r.get("slug"), r.get("art")) not in visti]
    i1, n1 = controlla_norme(refs_fac, "facsimile", base, fonte, stato_art, cl_auto)
    i2, n2 = controlla_norme(refs_nc, "norme_chiave", base, fonte, stato_art, cl_auto)
    issue += i1 + i2
    # (b) requisiti, (c) formule, (d) cifre
    issue += controlla_requisiti(fac, tipi, regole.get("requisiti"))
    issue += controlla_formule(fac, ambito, regole.get("formule"), oggi)
    ridotto = re.search(r"monitori|cautelar|lavoro|sfratt|possessori|opposizione\s+a\s+decreto", " ".join(
        [str(m.get("rito") or ""), str(m.get("titolo") or ""), str(m.get("materia") or "")]), re.I)
    issue += controlla_cifre(fac, tipi + (["ridotto"] if ridotto else []), regole)
    usate = usa_tabelle(fac)
    for t in scadute:
        if t["sigla"] in usate:
            issue.append(_issue("tabelle:scaduta", GIALLO, f"cifre dalla tabella «{t['nome']}», da riverificare dal {t['prossima_verifica']} ({t['tabella']})"))
    # (e) metadati
    issue += controlla_metadati(m, sch["frontmatter"], meta, fonte)
    # marcatura manuale ancora aperta (sviluppo/avvocato): conta come rosso finche' non la si chiude con --allinea
    dr = meta.get("da_ricontrollare")
    if dr and isinstance(dr, dict) and dr.get("fonte") != "sentinella":
        issue.append(_issue("sidecar:da-ricontrollare", ROSSO, f"da ricontrollare ({dr.get('fonte') or 'manuale'}, dal {dr.get('dal')}): {dr.get('motivo')}"))
    elif dr and isinstance(dr, str):
        issue.append(_issue("sidecar:da-ricontrollare", ROSSO, f"da ricontrollare: {dr}"))
    uniche, visti_i = [], set()
    for i in issue:
        k = (i["regola"], i["messaggio"])
        if k not in visti_i:
            visti_i.add(k)
            uniche.append(i)
    issue = uniche
    return {"id": m.get("id"), "titolo": m.get("titolo"), "file": m.get("file"), "ambito": ambito, "tipi": tipi,
            "base": base, "verdetto": verdetto(issue), "issue": issue, "norme": n1 + n2,
            "chiavi_articoli": sorted({f"{x['slug']}:{x['art']}" for x in n1 + n2 if x.get("slug") and x.get("art")})}


def verdetto(issue: list) -> str:
    g = {i.get("gravita") for i in issue}
    return "ROSSO" if ROSSO in g else ("GIALLO" if GIALLO in g else "VERDE")


def motivi_brevi(r: dict, n: int = 3) -> list:
    ordine = {ROSSO: 0, GIALLO: 1, INFO: 2}
    return [i["messaggio"][:180] for i in sorted(r.get("issue") or [], key=lambda i: ordine.get(i.get("gravita"), 3))
            if i.get("gravita") in (ROSSO, GIALLO)][:n]


# ============================================================ (f) motori

#: Profili dei motori → tipi di requisiti. I profili cambiano con i motori: si deduce dal NOME del profilo.
def tipi_profilo(nome: str) -> tuple:
    """(tipi_requisiti, contributo_ridotto, rito_previgente) per un profilo demo di atto_giudiziario_docx."""
    n = nome.lower()
    previgente = bool(re.search(r"183_6|702bis|previgent", n))
    ridotto = bool(re.search(r"opposizione_di|opposto_di|monitori|cautelar|669|lavoro|sfratt|possessori", n))
    if "conclusional" in n or "replica" in n or "127ter" in n or "171ter" in n or previgente:
        tipi = []
    elif "citazione" in n:
        tipi = ["citazione"]
    elif "appello" in n:
        tipi = ["appello"]
    elif "semplificat" in n:
        tipi = ["ricorso-semplificato"]
    elif "cassazione" in n:
        tipi = ["cassazione"]
    elif "precetto" in n:
        tipi = ["precetto"]
    elif "comparsa" in n:
        tipi = ["comparsa"]
    elif "ricorso" in n or "cautelar" in n:
        tipi = ["ricorso"]
    elif "memoria_costituzione" in n:
        tipi = ["memoria-difensiva"]
    else:
        tipi = []
    return tipi, ridotto, previgente


def testo_docx(path: str) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return ""
    paragrafi = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        t = "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", p))
        if t.strip():
            paragrafi.append(t)
    from html import unescape
    return unescape("\n".join(paragrafi))


def controlla_motori(regole: dict, oggi: _dt.date) -> list:
    """Rende i profili demo dei motori in una cartella temporanea e applica formule, requisiti, cifre."""
    out = []
    try:
        import atto_giudiziario_docx as ag
    except Exception as e:
        return [{"motore": "atto_giudiziario_docx", "profilo": "*", "verdetto": "ROSSO",
                 "issue": [_issue("motori:import", ROSSO, f"motore non importabile ({e.__class__.__name__}: {str(e)[:120]})")]}]
    try:
        profili = {"citazione": ag._demo_atto()}
        profili.update(ag._demo_minimi())
    except Exception as e:
        return [{"motore": "atto_giudiziario_docx", "profilo": "*", "verdetto": "ROSSO",
                 "issue": [_issue("motori:demo", ROSSO, f"profili demo non leggibili ({e.__class__.__name__})")]}]
    with tempfile.TemporaryDirectory(prefix="sentinella-motori-") as tmp:
        for nome, dati in profili.items():
            dest = str(Path(tmp) / f"atto-{nome}-demo.docx")
            try:
                ag.genera_atto(dati, dest)
            except BaseException as e:  # il motore puo' anche uscire con SystemExit
                out.append({"motore": "atto_giudiziario_docx", "profilo": nome, "verdetto": "ROSSO",
                            "issue": [_issue("motori:genera", ROSSO, f"il profilo non si genera: {' '.join(str(e).split())[:260]}")]})
                continue
            testo = testo_docx(dest)
            tipi, ridotto, previgente = tipi_profilo(nome)
            iss = [] if previgente else controlla_formule(testo, "giudiziario", regole.get("formule"), oggi)
            iss += controlla_requisiti(testo, tipi, regole.get("requisiti"))
            iss += controlla_cifre(testo, tipi + (["ridotto"] if ridotto else []), regole)
            if previgente:
                iss.append(_issue("motori:previgente", INFO, "profilo del rito previgente (procedimenti pendenti al 28/02/2023): "
                                  "formule superate non applicate"))
            out.append({"motore": "atto_giudiziario_docx", "profilo": nome, "verdetto": verdetto(iss), "issue": iss})
        try:
            import documento_stragiudiziale_docx as ds
            dest = str(Path(tmp) / "documento-demo.docx")
            ds.genera_documento(ds._demo(), dest)
            testo = testo_docx(dest)
            iss = controlla_formule(testo, "documento", regole.get("formule"), oggi) + controlla_formule(testo, "lettera", regole.get("formule"), oggi)
            out.append({"motore": "documento_stragiudiziale_docx", "profilo": "demo", "verdetto": verdetto(iss), "issue": iss})
        except BaseException as e:
            out.append({"motore": "documento_stragiudiziale_docx", "profilo": "demo", "verdetto": "ROSSO",
                        "issue": [_issue("motori:genera", ROSSO, f"il demo non si genera: {' '.join(str(e).split())[:200]}")]})
    return out


# ============================================================ regole da riallineare

def regole_da_riallineare(regole: dict, fonte: FonteNorme, cl_auto: list) -> list:
    """Regole dei due JSON il cui articolo e' cambiato dopo l'aggiornamento del file: vanno rilette."""
    out = []
    req = regole.get("requisiti") or {}
    agg = str((req.get("_meta") or {}).get("aggiornato_il") or "")[:10]
    visti = set()
    for tipo, lista in (req.get("tipi") or {}).items():
        for r in lista or []:
            a = str(r.get("articolo") or "")
            if ":" not in a or a in visti:
                continue
            visti.add(a)
            slug, art = a.split(":", 1)
            atto = fonte.atto(slug)
            voce = (atto or {}).get("articoli", {}).get(art) if atto else None
            vd = (voce or {}).get("vigore_da") or ""
            auto = [x for x in cl_auto if x.get("slug") == slug and x.get("articolo") == art and (x.get("snapshot_dopo") or "") > agg]
            if (vd and agg and vd > agg) or auto:
                out.append({"articolo": a, "regole": [x.get("id") for t2, l2 in (req.get("tipi") or {}).items() for x in l2 if x.get("articolo") == a],
                            "vigore_da": vd, "aggiornato_il": agg})
    return out


# ============================================================ giro

def _changelog_auto() -> list:
    try:
        import corpus_diff as cd
        return cd.leggi_changelog()
    except Exception:
        return []


def _meta_per_id(meta_dati: dict) -> dict:
    return {str(x.get("id")): x for x in (meta_dati or {}).get("modelli", []) if isinstance(x, dict)}


# ============================================================ v0.30: segnalazioni a runtime (corpus → modelli)

REL_NORME_CITATE = "modelli/norme-citate.json"


def esporta_norme_citate(fonte: FonteNorme = None, scrivi: bool = True) -> dict:
    """Mappa modello → articoli citati nel fac-simile, calcolata offline dal corpus locale. Si genera nel repo
    (prima del bundle) e viaggia col plugin: a runtime basta incrociarla col changelog del corpus sincronizzato."""
    fonte = fonte or FonteNorme(offline=True)
    meta_id = _meta_per_id(leggi_json_vivo(REL_META))
    out = {}
    for m in leggi_json_vivo(REL_CATALOGO).get("modelli", []):
        ident = str(m.get("id"))
        sch = scomponi_scheda(_leggi_testo_modello(str(m.get("file") or "")))
        refs = estrai_norme(sch["facsimile"], fonte) if sch["facsimile"] else []
        norme = sorted({f"{r['slug']}:{r['art']}" for r in refs if r.get("slug") and r.get("art")})
        out[ident] = {"data_base": data_base(meta_id.get(ident) or {}, sch["frontmatter"]), "norme": norme}
    dati = {"_meta": {"generato_il": _oggi().isoformat(), "descrizione": (
        "Articoli citati nel fac-simile di ogni modello (slug:articolo) e data di allineamento del modello. "
        "Generato da sentinella_modelli.py --esporta; a runtime flag_runtime() lo incrocia con il changelog del "
        "corpus sincronizzato e con gli atti in movimento.")}, "modelli": out}
    if scrivi:
        p = WIKI / REL_NORME_CITATE
        p.write_text(json.dumps(dati, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return dati


def _righe_changelog_tutte() -> list:
    """Changelog del corpus: quello sincronizzato (cartella di stato) unito a quello del bundle."""
    righe, viste = [], set()
    try:
        import corpus_diff as cd
        fonti = [cd.leggi_changelog(), cd.leggi_changelog(WIKI / "normativa")]
    except Exception:
        fonti = []
    for lista in fonti:
        for r in lista or []:
            k = (r.get("slug"), r.get("articolo"), r.get("snapshot_dopo"), r.get("tipo"))
            if k not in viste:
                viste.add(k)
                righe.append(r)
    return righe


def flag_runtime(mappa: dict = None, righe: list = None, manifest: dict = None) -> dict:
    """{id: [segnalazione]} dei modelli che citano articoli cambiati DOPO la loro data di allineamento
    (changelog del corpus) o toccati da leggi in G.U. non ancora consolidate (atti in movimento).
    abrogato/rimosso → ROSSO; modificato/aggiunto → GIALLO; in movimento → GIALLO. Le sole note redazionali
    e le date di vigenza non segnalano un modello."""
    if mappa is None:
        try:
            mappa = json.loads((WIKI / REL_NORME_CITATE).read_text(encoding="utf-8")).get("modelli") or {}
        except (OSError, ValueError):
            mappa = {}
    righe = _righe_changelog_tutte() if righe is None else righe
    if manifest is None:
        try:
            import codice_locale as cl
            manifest = cl.manifest_corpus()
        except Exception:
            manifest = {}
    per_art = {}
    for r in righe:
        if r.get("tipo") not in ("modificato", "aggiunto", "abrogato", "rimosso"):
            continue
        per_art.setdefault(f"{r.get('slug')}:{r.get('articolo')}", []).append(r)
    movimento = {s: [str(a) for a in (v.get("articoli_in_movimento") or ["*"])]
                 for s, v in ((manifest or {}).get("atti") or {}).items() if v.get("in_movimento")}
    out = {}
    for ident, voce in (mappa or {}).items():
        base = str(voce.get("data_base") or "1900-01-01")
        segn = []
        for chiave in voce.get("norme") or []:
            for r in per_art.get(chiave, []):
                quando = str(r.get("vigore_da_dopo") or r.get("snapshot_dopo") or "")
                if quando and quando > base:
                    segn.append({"norma": chiave, "tipo": r.get("tipo"), "quando": quando,
                                 "atto_modificante": r.get("atto_modificante"),
                                 "verdetto": "ROSSO" if r.get("tipo") in ("abrogato", "rimosso") else "GIALLO"})
            slug, _, art = chiave.partition(":")
            arts = movimento.get(slug)
            if arts and ("*" in arts or art in arts):
                segn.append({"norma": chiave, "tipo": "in_movimento", "quando": None, "atto_modificante": None,
                             "verdetto": "GIALLO"})
        if segn:
            out[ident] = segn
    return out


def giro(oggi: _dt.date = None, fonte: FonteNorme = None, solo_ids=None, motori: bool = True,
         patch: bool = True, tipo: str = "giro", scrivi: bool = True) -> dict:
    """Il giro completo (o ristretto a `solo_ids`). Ritorna il risultato e, con `scrivi`, aggiorna report e stato."""
    oggi = oggi or _oggi()
    fonte = fonte or FonteNorme()
    st = stato()
    stato_art = st.get("articoli") or {}
    regole = carica_regole()
    catalogo = leggi_json_vivo(REL_CATALOGO).get("modelli", [])
    meta_id = _meta_per_id(leggi_json_vivo(REL_META))
    cl_auto = _changelog_auto()
    scadute = tabelle_scadute(oggi)
    scelti = [m for m in catalogo if solo_ids is None or str(m.get("id")) in solo_ids]
    # 1a passata: impronte degli articoli citati, cosi' un corpo cambiato si vede gia' in questo giro
    chiavi = set()
    for m in scelti:
        sch = scomponi_scheda(_leggi_testo_modello(m.get("file") or ""))
        for r in estrai_norme(sch["facsimile"], fonte) + [x for nc in (m.get("norme_chiave") or []) for x in estrai_norme(nc, fonte)]:
            if r.get("slug") and r.get("art"):
                chiavi.add(f"{r['slug']}:{r['art']}")
    nuovo_art = aggiorna_impronte(fonte, chiavi, stato_art, oggi)
    # 2a passata: i verdetti
    risultati = [valuta_modello(m, meta_id.get(str(m.get("id"))) or {}, regole, fonte, nuovo_art, cl_auto, oggi, scadute)
                 for m in scelti]
    motori_res = controlla_motori(regole, oggi) if motori else []
    conteggi = {v: sum(1 for r in risultati if r["verdetto"] == v) for v in VERDETTI}
    snap, avvisi = {}, []
    for s in ("cpc", "cc"):
        a = fonte.atto(s)
        if a:
            snap[s] = (a.get("meta") or {}).get("snapshot")
    if "cpc" not in snap:
        avvisi.append("corpus locale non leggibile (codice di procedura civile assente): il controllo delle norme citate "
                      "NON e' stato fatto — verificare codice_locale.py --stato prima di fidarsi dei verdi")
    elif _d(snap["cpc"]) and (oggi - _d(snap["cpc"])).days > 45:
        avvisi.append(f"snapshot del c.p.c. vecchio ({snap['cpc']}): lanciare /aggiorna-corpus e ripetere il giro")
    if fonte._rete_ko:
        avvisi.append("rete non disponibile per lo storico: alcune norme modificate restano «da confrontare»")
    res = {"giro": oggi.isoformat(), "tipo": tipo, "generato_il": _dt.datetime.now().isoformat(timespec="seconds"),
           "modelli_valutati": len(risultati), "conteggi": conteggi, "snapshot_corpus": snap,
           "avvisi": avvisi, "tabelle_scadute": scadute, "regole_da_riallineare": regole_da_riallineare(regole, fonte, cl_auto),
           "motori": motori_res, "modelli": risultati, "patch": []}
    if patch:
        res["patch"] = applica_patch(risultati, meta_id, oggi)
    if scrivi:
        scrivi_report(res)
        verdetti = {} if (tipo == "giro" and solo_ids is None) else dict(st.get("verdetti") or {})
        for r in risultati:
            verdetti[str(r["id"])] = {"verdetto": r["verdetto"], "motivi": motivi_brevi(r),
                                      "rossi": sum(1 for i in r["issue"] if i["gravita"] == ROSSO),
                                      "gialli": sum(1 for i in r["issue"] if i["gravita"] == GIALLO), "giro": oggi.isoformat()}
        tot = {v: sum(1 for x in verdetti.values() if x.get("verdetto") == v) for v in VERDETTI}
        nuovo = dict(st)
        nuovo.update({"versione": 1, "articoli": nuovo_art, "verdetti": verdetti, "conteggi": tot,
                      "ultimo_giro_tipo": tipo, "report": res.get("report")})
        if tipo == "giro" and solo_ids is None:
            nuovo["ultimo_giro"] = oggi.isoformat()
            nuovo["ultimo_giro_completo_il"] = res["generato_il"]
        nuovo["changelog_auto_visto"] = max([x.get("registrato_il") or "" for x in cl_auto] + [st.get("changelog_auto_visto") or ""])
        nuovo["motori"] = [{"profilo": x["profilo"], "motore": x["motore"], "verdetto": x["verdetto"]} for x in motori_res] or st.get("motori", [])
        nuovo["avvisi"] = avvisi
        _salva_stato(nuovo)
    return res


def ids_delta(st: dict = None) -> tuple:
    """(ids dei modelli toccati dalle righe NUOVE del changelog-auto, righe nuove)."""
    st = st if st is not None else stato()
    visto = st.get("changelog_auto_visto") or ""
    nuove = [x for x in _changelog_auto() if (x.get("registrato_il") or "") > visto]
    toccati = {f"{x.get('slug')}:{x.get('articolo')}" for x in nuove}
    ids = set()
    if toccati:
        # le chiavi citate per modello non stanno nello stato: si ricalcolano (estrazione veloce, niente corpus)
        fonte = FonteNorme(offline=True)
        cat = leggi_json_vivo(REL_CATALOGO).get("modelli", [])
        for m in cat:
            sch = scomponi_scheda(_leggi_testo_modello(m.get("file") or ""))
            refs = estrai_norme(sch["facsimile"], fonte) + [r for nc in (m.get("norme_chiave") or []) for r in estrai_norme(nc, fonte)]
            if {f"{r.get('slug')}:{r.get('art')}" for r in refs} & toccati:
                ids.add(str(m.get("id")))
    return ids, nuove


# ============================================================ patch del sidecar vivo

def _motivo_sentinella(r: dict) -> str:
    rossi = [i["messaggio"] for i in r["issue"] if i["gravita"] == ROSSO and i["regola"] != "sidecar:da-ricontrollare"]
    return "; ".join(sorted(rossi))[:600]


def applica_patch(risultati: list, meta_id: dict, oggi: _dt.date) -> list:
    """Rossi deterministici → `da_ricontrollare` (fonte sentinella) nel sidecar VIVO; rossi spariti → marcatura tolta.
    Idempotente: si scrive solo quando il valore vivo e' diverso."""
    fatte = []
    try:
        import corpus as _cp
    except Exception:
        return fatte
    for r in risultati:
        meta = meta_id.get(str(r["id"])) or {}
        if not meta:
            continue
        dr = meta.get("da_ricontrollare")
        motivo = _motivo_sentinella(r)
        campi = None
        if motivo:
            if not (isinstance(dr, dict) and dr.get("fonte") == "sentinella" and dr.get("motivo") == motivo) and not (
                    isinstance(dr, dict) and dr.get("fonte") not in (None, "sentinella")):
                campi = {"stato": "da_ricontrollare",
                         "da_ricontrollare": {"motivo": motivo, "dal": oggi.isoformat(), "fonte": "sentinella"}}
        elif isinstance(dr, dict) and dr.get("fonte") == "sentinella":
            campi = {"stato": "congelato", "da_ricontrollare": None}
        if campi is None:
            continue
        try:
            _cp.patch_json(REL_META, campi, "modelli", "id", str(r["id"]), fonte=f"sentinella-modelli {oggi.isoformat()}",
                           data=oggi.isoformat())
            fatte.append({"id": r["id"], "set": campi})
        except (Exception, SystemExit):
            continue
    return fatte


def allinea(ident: str, motivo: str, fonte_nome: str = "avvocato", oggi: _dt.date = None) -> dict:
    """Chiusura del controllo di un modello (dopo il «sì» dell'avvocato): baseline delle norme e verifica a oggi,
    marcatura tolta. Scrive nel corpus vivo, mai nel bundle."""
    oggi = oggi or _oggi()
    import corpus as _cp
    campi = {"norme_allineate_al": oggi.isoformat(), "verificato_il": oggi.isoformat(),
             "prossima_verifica": (oggi + _dt.timedelta(days=365)).isoformat(), "stato": "congelato",
             "da_ricontrollare": None, "ultimo_allineamento": {"data": oggi.isoformat(), "fonte": fonte_nome, "motivo": motivo}}
    return _cp.patch_json(REL_META, campi, "modelli", "id", str(ident), fonte=f"allineamento {fonte_nome} {oggi.isoformat()}",
                          data=oggi.isoformat())


# ============================================================ report

def _rel_report(res: dict) -> str:
    g = _d(res["giro"]) or _oggi()
    return f"{g.strftime('%Y-%m')}" if res.get("tipo") == "giro" else f"{g.isoformat()}-delta"


def render_md(res: dict) -> str:
    c = res["conteggi"]
    r = [f"# Sentinella dei modelli d'atto — {res['giro'][:7]} ({'giro completo' if res['tipo'] == 'giro' else 'solo delta'} del {res['giro']})",
         "",
         f"{res['modelli_valutati']} modelli · 🔴 {c.get('ROSSO', 0)} · 🟡 {c.get('GIALLO', 0)} · 🟢 {c.get('VERDE', 0)} · "
         f"corpus: " + ", ".join(f"{k} {v}" for k, v in (res.get("snapshot_corpus") or {}).items()),
         "",
         "> Controllo deterministico (`scripts/sentinella_modelli.py`): norme citate contro il corpus locale datato,",
         "> requisiti per tipo, formule superate, cifre contro le tabelle, metadati, motori. **Tell-only**: i rossi",
         "> marcano il modello `da_ricontrollare` nel sidecar vivo; le correzioni del testo le approva l'avvocato.",
         ""]
    for a in res.get("avvisi") or []:
        r.append(f"> ⚠️ {a}")
    if res.get("avvisi"):
        r.append("")
    rossi = [x for x in res["modelli"] if x["verdetto"] == "ROSSO"]
    gialli = [x for x in res["modelli"] if x["verdetto"] == "GIALLO"]
    r.append(f"## 🔴 Da non usare senza correggere ({len(rossi)})")
    r.append("")
    for x in rossi:
        r.append(f"- **{x['id']}** · {x['titolo']}")
        for i in x["issue"]:
            if i["gravita"] == ROSSO:
                r.append(f"  - {i['messaggio']}" + (f" → {i['correzione']}" if i.get("correzione") else ""))
    if not rossi:
        r.append("_nessuno_")
    r.append("")
    r.append(f"## 🟡 Da rivedere ({len(gialli)})")
    r.append("")
    per_regola = {}
    for x in res["modelli"]:
        for i in x["issue"]:
            if i["gravita"] == GIALLO:
                per_regola.setdefault(i["regola"].split(":")[0] + ":" + i["regola"].split(":")[-1], []).append((x["id"], i))
    for regola, voci in sorted(per_regola.items(), key=lambda kv: -len(kv[1])):
        ids = sorted({v[0] for v in voci})
        r.append(f"- `{regola}` — {len(ids)} modelli: {', '.join(ids[:30])}{' …' if len(ids) > 30 else ''}")
        r.append(f"  - es.: {voci[0][1]['messaggio'][:220]}")
    if not per_regola:
        r.append("_nessuno_")
    r.append("")
    mod = {}
    for x in res["modelli"]:
        for n in x["norme"]:
            if n.get("esito") in ("MODIFICATA", "MODIFICATA_SOLO_NOTE"):
                k = (n["slug"], n["art"])
                mod.setdefault(k, {"n": n, "ids": set()})["ids"].add(x["id"])
    if mod:
        r.append("## Norme citate cambiate dopo i modelli")
        r.append("")
        r.append("| articolo | esito | in vigore dal | atto modificante | modelli |")
        r.append("|---|---|---|---|---|")
        for (slug, art), v in sorted(mod.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or "")):
            n = v["n"]
            esito = "solo note" if n["esito"] == "MODIFICATA_SOLO_NOTE" else ("testo cambiato" if n.get("diff") else "da confrontare")
            r.append(f"| art. {art} ({slug}) | {esito} | {n.get('modifica_dal') or '—'} | {n.get('atto_modificante') or '—'} | "
                     f"{', '.join(sorted(v['ids']))} |")
        r.append("")
    if res.get("tabelle_scadute"):
        r.append("## Tabelle da riverificare")
        r.append("")
        for t in res["tabelle_scadute"]:
            r.append(f"- {t['nome']} (`{t['tabella']}`): prossima verifica {t['prossima_verifica']} passata")
        r.append("")
    if res.get("regole_da_riallineare"):
        r.append("## Regole della sentinella da rileggere (articolo cambiato dopo la regola)")
        r.append("")
        for x in res["regole_da_riallineare"]:
            r.append(f"- {x['articolo']} (vigore_da {x['vigore_da']}, regole aggiornate al {x['aggiornato_il']}): {', '.join(x['regole'])}")
        r.append("")
    if res.get("motori"):
        r.append("## Motori (profili demo)")
        r.append("")
        for x in res["motori"]:
            gravi = [i["messaggio"][:160] for i in x["issue"] if i["gravita"] in (ROSSO, GIALLO)]
            info = [i["messaggio"][:120] for i in x["issue"] if i["gravita"] == INFO]
            r.append(f"- {ICONA.get(x['verdetto'], '?')} {x['motore']} · {x['profilo']}"
                     + (": " + "; ".join(gravi)[:500] if gravi else (f" ({info[0]})" if info else "")))
        r.append("")
    if res.get("patch"):
        r.append(f"## Sidecar vivo aggiornato ({len(res['patch'])} modelli)")
        r.append("")
        r.append(", ".join(f"{p['id']} → {p['set'].get('stato')}" for p in res["patch"]))
        r.append("")
    r.append("## Prossimi passi")
    r.append("")
    r.append("1. Per ogni 🔴 e per ogni norma «testo cambiato»: `/sentinella-modelli` (un agente per voce propone la correzione, tell-only).")
    r.append("2. Dopo il sì dell'avvocato: correzione del modello nel corpus vivo (consolida-conoscenza) e "
             "`sentinella_modelli.py --allinea <id> --motivo \"…\"`.")
    return "\n".join(r) + "\n"


def scrivi_report(res: dict) -> dict:
    d = dir_report()
    d.mkdir(parents=True, exist_ok=True)
    nome = _rel_report(res)
    pj, pm = d / f"{nome}.json", d / f"{nome}.md"
    res["report"] = {"json": str(pj), "md": str(pm)}
    pj.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    pm.write_text(render_md(res), encoding="utf-8")
    return res["report"]


# ============================================================ router e stato

def da_eseguire(oggi: _dt.date = None) -> bool:
    """True se non c'e' un giro completo registrato o se l'ultimo ha piu' di GIORNI_GIRO giorni."""
    oggi = oggi or _oggi()
    ultimo = _d(stato().get("ultimo_giro"))
    return ultimo is None or (oggi - ultimo).days > GIORNI_GIRO


def riga_router(oggi: _dt.date = None) -> str:
    """Una riga per il router: vuota se l'ultimo giro e' recente e tutto e' verde."""
    oggi = oggi or _oggi()
    st = stato()
    ultimo = st.get("ultimo_giro")
    if not ultimo:
        return "Sentinella modelli: nessun giro registrato → /sentinella-modelli (o attendi il giro automatico mensile)"
    c = st.get("conteggi") or {}
    motori_rossi = sum(1 for x in st.get("motori") or [] if x.get("verdetto") == "ROSSO")
    scaduto = da_eseguire(oggi)
    if not scaduto and not c.get("ROSSO") and not c.get("GIALLO") and not motori_rossi and not st.get("avvisi"):
        return ""
    pezzi = [f"{c.get('ROSSO', 0)}🔴", f"{c.get('GIALLO', 0)}🟡"]
    if motori_rossi:
        pezzi.append(f"motori {motori_rossi}🔴")
    coda = (" · giro scaduto" if scaduto else "") + (" · ⚠️ " + st["avvisi"][0][:60] if st.get("avvisi") else "")
    return f"Sentinella modelli (ultimo giro {ultimo}): {' '.join(pezzi)}{coda} → /sentinella-modelli"


def riga_stato(oggi: _dt.date = None) -> str:
    oggi = oggi or _oggi()
    st = stato()
    if not st.get("ultimo_giro"):
        return "Sentinella modelli: mai eseguita (python3 scripts/sentinella_modelli.py --giro)"
    c = st.get("conteggi") or {}
    tot = sum(c.values())
    prossimo = (_d(st["ultimo_giro"]) + _dt.timedelta(days=GIORNI_GIRO + 1)).isoformat()
    return (f"Sentinella modelli: ultimo giro {st['ultimo_giro']} · {tot} modelli · 🟢 {c.get('VERDE', 0)} · 🟡 {c.get('GIALLO', 0)} · "
            f"🔴 {c.get('ROSSO', 0)} · prossimo giro dovuto dal {prossimo}" + (" (SCADUTO)" if da_eseguire(oggi) else "")
            + (f" · report {st.get('report', {}).get('md')}" if st.get("report") else ""))


def verdetti_modelli() -> dict:
    """{id: {verdetto, motivi, giro}} dall'ultimo giro (per modello_seleziona e freshness)."""
    return stato().get("verdetti") or {}


def _marca_avvio() -> Path:
    return dir_sentinella() / "sentinella-ultimo-avvio"


def avvia_in_background(oggi: _dt.date = None) -> bool:
    """Fallback del router: se il giro e' scaduto lancia `--se-scaduto --quiet` in background (throttle 6 ore)."""
    try:
        import subprocess
        if os.environ.get("STUDIO_NO_PREFETCH"):
            return False
        if not da_eseguire(oggi):
            return False
        marca = _marca_avvio()
        try:
            if marca.exists():
                ultimo = _dt.datetime.fromisoformat(marca.read_text(encoding="utf-8").strip())
                if (_dt.datetime.now() - ultimo) < _dt.timedelta(hours=ORE_THROTTLE):
                    return False
        except (ValueError, OSError):
            pass
        marca.parent.mkdir(parents=True, exist_ok=True)
        marca.write_text(_dt.datetime.now().isoformat(timespec="seconds"), encoding="utf-8")
        extra = {} if os.name == "nt" else {"start_new_session": True}
        subprocess.Popen([sys.executable or "python3", str(Path(__file__).resolve()), "--se-scaduto", "--quiet"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **extra)
        return True
    except Exception:
        return False


# ============================================================ CLI

def _stampa_sintesi(res: dict) -> None:
    c = res["conteggi"]
    print(f"SENTINELLA MODELLI {res['giro']} ({res['tipo']}): {res['modelli_valutati']} modelli · 🔴 {c['ROSSO']} · 🟡 {c['GIALLO']} · 🟢 {c['VERDE']}")
    for x in [x for x in res["modelli"] if x["verdetto"] == "ROSSO"][:25]:
        print(f"  🔴 {x['id']} {str(x['titolo'])[:50]} — {'; '.join(motivi_brevi(x, 2))[:200]}")
    mr = [x for x in res.get("motori") or [] if x["verdetto"] != "VERDE"]
    for x in mr:
        print(f"  {ICONA.get(x['verdetto'])} motore {x['profilo']}: {'; '.join(i['messaggio'] for i in x['issue'] if i['gravita'] in (ROSSO, GIALLO))[:200]}")
    if res.get("patch"):
        print(f"  sidecar vivo: {len(res['patch'])} patch ({', '.join(str(p['id']) for p in res['patch'][:15])})")
    if res.get("report"):
        print(f"  report: {res['report']['md']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Sentinella dei modelli d'atto (controllo mensile deterministico del catalogo).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--giro", action="store_true", help="giro completo")
    g.add_argument("--se-scaduto", action="store_true", help="gira solo se l'ultimo giro ha piu' di 31 giorni (fallback del router)")
    g.add_argument("--solo-delta", action="store_true", help="solo i modelli toccati dalle righe nuove del changelog-auto")
    g.add_argument("--stato", action="store_true", help="una riga di stato")
    g.add_argument("--allinea", metavar="ID", help="chiude il controllo del modello (dopo l'approvazione dell'avvocato)")
    g.add_argument("--esporta", action="store_true", help="v0.30: rigenera modelli/norme-citate.json (prima del bundle)")
    g.add_argument("--segnalazioni", action="store_true", help="v0.30: modelli che citano articoli cambiati (corpus sincronizzato)")
    ap.add_argument("--motivo", default="", help="con --allinea: cosa e' stato controllato")
    ap.add_argument("--fonte", default="avvocato", help="con --allinea: chi ha approvato (avvocato|sviluppo)")
    ap.add_argument("--id", action="append", default=None, help="restringe il giro a questi modelli (ripetibile)")
    ap.add_argument("--offline", action="store_true", help="niente rete per i testi storici (solo cache)")
    ap.add_argument("--senza-motori", action="store_true", help="salta il rendering dei profili demo dei motori")
    ap.add_argument("--senza-patch", action="store_true", help="non scrivere il sidecar vivo")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--oggi", default=None, help="data ISO (test)")
    a = ap.parse_args(argv)
    oggi = _d(a.oggi) if a.oggi else _oggi()

    if a.stato:
        print(riga_stato(oggi))
        return 0
    if a.esporta:
        d = esporta_norme_citate()
        n = sum(len(v["norme"]) for v in d["modelli"].values())
        print(f"norme-citate.json: {len(d['modelli'])} modelli, {n} articoli citati")
        return 0
    if a.segnalazioni:
        f = flag_runtime()
        if a.json:
            print(json.dumps(f, ensure_ascii=False, indent=1))
        else:
            print(f"MODELLI SEGNALATI dal corpus: {len(f)}" + ("" if f else " — nessun articolo citato e' cambiato"))
            for ident, segn in sorted(f.items()):
                print(f"  {ident}: " + "; ".join(f"{ICONA[x['verdetto']]} {x['norma']} {x['tipo']}"
                                                  + (f" ({x['atto_modificante']})" if x.get("atto_modificante") else "")
                                                  for x in segn))
        return 0
    if a.allinea:
        if not a.motivo.strip():
            print("--allinea richiede --motivo (cosa e' stato controllato e da chi)")
            return 2
        v = allinea(a.allinea, a.motivo.strip(), a.fonte, oggi)
        print(f"ALLINEATO {a.allinea}: norme_allineate_al/verificato_il = {oggi.isoformat()} nel sidecar vivo"
              + (" (patch gia' presente)" if v.get("duplicata") else ""))
        return 0
    if a.se_scaduto and not da_eseguire(oggi):
        if not a.quiet:
            print(riga_stato(oggi) + " — giro non dovuto")
        return 0
    fonte = FonteNorme(offline=a.offline)
    if a.solo_delta:
        ids, nuove = ids_delta()
        if not ids:
            if not a.quiet:
                print(f"SENTINELLA MODELLI: nessun modello toccato da righe nuove del changelog-auto ({len(nuove)} righe nuove)")
            st = stato()
            if nuove:
                st["changelog_auto_visto"] = max(x.get("registrato_il") or "" for x in nuove)
                _salva_stato(st)
            return 0
        res = giro(oggi, fonte, solo_ids=ids, motori=False, patch=not a.senza_patch, tipo="solo-delta")
    else:
        res = giro(oggi, fonte, solo_ids=set(a.id) if a.id else None, motori=not a.senza_motori,
                   patch=not a.senza_patch, tipo="giro")
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    elif not a.quiet:
        _stampa_sintesi(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
