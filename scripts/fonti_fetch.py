# -*- coding: utf-8 -*-
"""Fetch diretto delle fonti primarie SENZA browser (solo stdlib).

Le lenti L1 (fonti primarie) e L3 (giurisprudenza) lo chiamano via Bash PRIMA di aprire il
browser: per le NORME costruisce il permalink URN di normattiva.it (e' la ricerca della UI a
essere JS-heavy, non il permalink) e scarica il testo vigente ALLA data-evento; per le
SENTENZE la verifica resta SEMPRE live (nucleo-verifica §3-ter: "giurisprudenza sempre LIVE"),
ma lo script prepara query e URL pronti per la lente.

Contratto di output (prima riga = verdetto, sempre exit 0):
  OK        -> testo trovato: seguono FONTE/VIGENTE AL/TESTO. La lente lo usa come conferma
               di fonte primaria (stesso sito, stesso testo che avrebbe letto nel browser).
  VAI_LIVE  -> il fetch diretto non basta: la lente procede come oggi (browser/WebSearch,
               regola di degrado §5 invariata). Il motivo e' sulla stessa riga.

Cache su disco DATATA (default <cartella di stato>/fonti-cache/, TTL 24h, solo NORME): un secondo
giro sulla stessa norma nella stessa giornata legge il testo gia' scaricato, con data dichiarata.
La cartella e' ASSOLUTA dalla v0.15 (prima era outputs/.fonti-cache, relativa alla CWD: processi
lanciati da cartelle diverse — l'hook di prefetch e la Bash della lente — non si vedevano).
La giurisprudenza NON si cachea mai.

Cache PRE-WARM (sentinella): con --prewarm il testo si salva in wiki-studio/normativa/cache/
(TTL 168h). A runtime, se la cache di sessione manca, lo script serve il testo pre-warmato
DICHIARANDOLO nel log ("da cache pre-warm del ..."): per il congelato-first (nucleo §3-ter,
modalita' conservativo) vale come ground truth datato — le claim FONDANTI restano live comunque.

RESOLVER FUORI NORMATTIVA (v0.16, scripts/resolver_fonti.py): lo stesso comando legge anche
  EUR-Lex (via CELLAR, con la versione CONSOLIDATA vigente alla data-evento), i provvedimenti del
  Garante privacy (per doc. web o per numero+data, validati sul testo) e la Gazzetta Ufficiale
  (testo ORIGINARIO di un atto per articolo, o il sommario di un numero). Il dispatch e' automatico
  dai marcatori del riferimento; `--fonte` lo forza (es. il testo G.U. di un atto che normattiva
  conosce). Stesso contratto di output, stessa cache datata, stessi VAI_LIVE dichiarati.

Esempi:
  python3 scripts/fonti_fetch.py --riferimento "art. 163 c.p.c." --data-evento 2024-01-14
  python3 scripts/fonti_fetch.py --riferimento "art. 35 D.Lgs. 149/2022"
  python3 scripts/fonti_fetch.py --riferimento "art. 33 D.Lgs. 206/2005" --json
  python3 scripts/fonti_fetch.py --sentenza "Cass. civ. sez. III 12/03/2025 n. 7890"
  python3 scripts/fonti_fetch.py --riferimento "art. 281-undecies c.p.c." --dry-run   # solo URN
  python3 scripts/fonti_fetch.py --riferimento "art. 660 c.p.c." --prewarm            # pass sentinella
  python3 scripts/fonti_fetch.py --riferimento "art. 5 Reg. (UE) 2016/679" --data-evento 2025-03-01
  python3 scripts/fonti_fetch.py --riferimento "art. 50 AI Act"                         # alias -> CELEX
  python3 scripts/fonti_fetch.py --riferimento "provv. Garante n. 556 del 23 luglio 2026"
  python3 scripts/fonti_fetch.py --riferimento "doc. web n. 10277005" --integrale
  python3 scripts/fonti_fetch.py --riferimento "art. 2 L. 137/2026" --fonte gu          # testo G.U. originario
  python3 scripts/fonti_fetch.py --riferimento "GU n. 194 del 22 agosto 2026"           # sommario del numero
  python3 scripts/fonti_fetch.py --riferimento "art. 12 disp. prel. c.c." --offline      # v0.29: solo locale, zero rete

v0.29 — instradamento: preleggi («disp. prel.», «preleggi», «disposizioni sulla legge in generale») e disp. att.
c.c. riconosciute; forme lunghe («decreto legislativo 28/2010», «legge n. 689 del 1981», «D.M. 10/03/2014 n. 55»)
e anni a due cifre («L. 431/98») portate alla descrizione canonica; articoli col punto («art. 132.1 CAP»);
`--offline` arriva anche ai resolver fuori normattiva; snapshot locale oltre la vita massima servito con
«SNAPSHOT NON CONFERMATO dal …» se normattiva non risponde. Per cercare una norma per ARGOMENTO:
scripts/corpus_cerca.py.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, socket, sys, time, unicodedata
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8 (accenti, frecce, emoji)
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (corpus-normativo fonti_fetch; +https://www.normattiva.it)"

#: Timeout del singolo fetch. v0.15: sceso da 20s a 12s. Il ragionamento e' che normattiva o
#: risponde in pochi secondi o non risponde: i 20s servivano solo a far aspettare l'avvocato
#: prima di un VAI_LIVE che sarebbe arrivato comunque. Override con $FONTI_TIMEOUT.
TIMEOUT = float(os.environ.get("FONTI_TIMEOUT") or 12)

#: Attese (secondi) prima dei retry sui guasti transitori di normattiva (HTTP 5xx/429,
#: timeout, reset). Un 500 intermittente che finiva in VAI_LIVE faceva degradare al browser
#: TUTTE e cinque le lenti: due retry evitano quella cascata. v0.15: backoff (2,5) -> (1,3),
#: perche' il caso che ci interessa e' il 500 intermittente, che rientra subito.
RETRY_ATTESE = (1, 3)

#: Budget di retry ridotto per i fetch che girano DENTRO il pool (dossier_fonti.py): li' le
#: norme sono molte e in parallelo, e una singola norma morta non deve poter allungare la coda
#: oltre il deadline del round. Una norma che non risponde e' un VAI_LIVE, non un'attesa.
RETRY_ATTESE_POOL = (1,)


def cache_dir_default() -> Path:
    """Cartella della cache di sessione — ASSOLUTA, non relativa alla CWD.

    Fino alla v0.14 era `outputs/.fonti-cache`, cioe' RELATIVA alla cartella di lavoro: due
    processi lanciati da CWD diverse (l'hook di prefetch e la Bash della lente) scrivevano e
    leggevano cache diverse, e il pre-scaldamento non serviva a niente. Ora vive accanto al
    ledger, nella cartella di stato. Override con $FONTI_CACHE.
    """
    env = os.environ.get("FONTI_CACHE")
    if env:
        return Path(env)
    try:
        from paths import stato_root
        return stato_root() / "fonti-cache"
    except Exception:
        return Path.home() / ".fonti-cache"


#: Vecchia cartella (relativa alla CWD): si legge ancora, cosi' le voci gia' scaricate dalle
#: sessioni precedenti non vengono buttate via. Non ci si scrive piu'.
CACHE_LEGACY = Path("outputs/.fonti-cache")
CACHE_DEFAULT = CACHE_LEGACY  # compat storica: alcuni help/testi la citano

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from paths import WIKI  # noqa: E402
    PREWARM_DIR = WIKI / "normativa" / "cache"
except Exception:  # pragma: no cover - paths.py sempre presente nel plugin
    PREWARM_DIR = None
PREWARM_TTL_ORE = 168.0  # una settimana: la sentinella rinfresca a ogni giro

# ---------------------------------------------------------------- riferimenti

# Codici e testi noti -> URN normattiva (base, senza articolo). Le varianti con ":1"/":2"
# (allegato) si tentano in fallback: alcune codificazioni storiche le richiedono.
CODICI = {
    "c.p.c.":  ("urn:nir:stato:regio.decreto:1940-10-28;1443", [":1"]),
    "disp. att. c.p.c.": ("urn:nir:stato:regio.decreto:1941-12-18;1368", [":1"]),
    # R.D. 262/1942: «:1» sono le PRELEGGI, «:2» il codice civile. Fino alla v0.28 il c.c. tentava
    # anche «:1» e per gli artt. 1-31 c.c. il fetch live poteva servire le preleggi (verificato il
    # 23/09/2026: ;262:1~art12 = «Interpretazione della legge»).
    "c.c.":    ("urn:nir:stato:regio.decreto:1942-03-16;262", [":2"]),
    "preleggi": ("urn:nir:stato:regio.decreto:1942-03-16;262", [":1"]),
    "disp. att. c.c.": ("urn:nir:stato:regio.decreto:1942-03-30;318", [":1"]),
    "c.p.":    ("urn:nir:stato:regio.decreto:1930-10-19;1398", [":1"]),
    "c.p.p.":  ("urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447", [":1"]),
    "cost.":   ("urn:nir:stato:costituzione:1947-12-27", []),
    "cciv":    ("urn:nir:stato:regio.decreto:1942-03-16;262", [":2"]),
}
ALIAS_CODICI = {
    "cpc": "c.p.c.", "c.p.c": "c.p.c.", "codice di procedura civile": "c.p.c.",
    "cc": "c.c.", "c.c": "c.c.", "cod. civ.": "c.c.", "codice civile": "c.c.",
    "cp": "c.p.", "c.p": "c.p.", "codice penale": "c.p.", "cod. pen.": "c.p.",
    "cpp": "c.p.p.", "c.p.p": "c.p.p.", "codice di procedura penale": "c.p.p.",
    "cost": "cost.", "costituzione": "cost.",
    "disp att cpc": "disp. att. c.p.c.", "disp. att. cpc": "disp. att. c.p.c.",
    "disp att cc": "disp. att. c.c.", "disp. att. cod. civ.": "disp. att. c.c.",
    "disp. att. e trans. c.c.": "disp. att. c.c.", "disp. att. codice civile": "disp. att. c.c.",
    # v0.29 — le preleggi (artt. 1-31 disp. prel. c.c.) erano nel corpus ma irraggiungibili:
    # «art. 12 disp. prel. c.c.» si risolveva sull'art. 12 c.c. (ARTICOLO ABROGATO), cioe' su un ALTRO atto.
    # Qui la forma lunga batte «c.c.» perche' compare prima nel riferimento.
    "disp. prel.": "preleggi", "disp. prel. c.c.": "preleggi", "disp. prel. cod. civ.": "preleggi",
    "disp. prel. al c.c.": "preleggi", "disp. prel. al codice civile": "preleggi", "disp prel": "preleggi",
    "disposizioni preliminari": "preleggi", "disposizioni preliminari al codice civile": "preleggi",
    "disposizioni sulla legge in generale": "preleggi", "disp. sulla legge in generale": "preleggi",
    "prel.": "preleggi",
}
TIPI_ATTO = {
    "d.lgs.": "decreto.legislativo", "dlgs": "decreto.legislativo",
    "d. lgs.": "decreto.legislativo", "decreto legislativo": "decreto.legislativo",
    "l.": "legge", "legge": "legge",
    "d.l.": "decreto.legge", "dl": "decreto.legge", "decreto legge": "decreto.legge",
    "decreto-legge": "decreto.legge", "decreto-legislativo": "decreto.legislativo",       # v0.32: forma ufficiale col trattino
    "decreto del presidente della repubblica": "decreto.del.presidente.della.repubblica",
    "d.p.r.": "decreto.del.presidente.della.repubblica", "dpr": "decreto.del.presidente.della.repubblica",
    "r.d.": "regio.decreto", "rd": "regio.decreto", "regio decreto": "regio.decreto",
    "d.m.": "decreto", "dm": "decreto", "decreto ministeriale": "decreto",
    "d.m. giustizia": "decreto",
}

#: Decreti ministeriali: l'URN non e' «stato» ma il ministero emanante, e va cablato per
#: atto (non e' deducibile dal riferimento). Solo quelli nel corpus locale (codici.json).
URN_SPECIALI = {
    ("decreto", "55", "2014"): ("urn:nir:ministero.giustizia:decreto:2014-03-10;55", []),
    ("decreto", "147", "2022"): ("urn:nir:ministero.giustizia:decreto:2022-08-13;147", []),
    # Fase G (Piano v3 §11): fonti di secondo livello del PCT nel corpus locale
    ("decreto", "44", "2011"): ("urn:nir:ministero.giustizia:decreto:2011-02-21;44", []),
    ("decreto", "110", "2023"): ("urn:nir:ministero.giustizia:decreto:2023-08-07;110", []),
}

#: Sigle e nomi correnti di atti numerati -> (tipo URN, numero, anno). Le claim card scrivono
#: «art. 125-bis TUB», «art. 33 Cod. consumo», «art. 2086 c.c.»: senza questa mappa il parser
#: non trovava l'atto (o, peggio, prendeva quello citato dopo fra parentesi). v0.25.
SIGLE_ATTI = {
    "tub": ("decreto.legislativo", "385", "1993"), "t.u.b.": ("decreto.legislativo", "385", "1993"),
    "testo unico bancario": ("decreto.legislativo", "385", "1993"),
    "tuf": ("decreto.legislativo", "58", "1998"), "t.u.f.": ("decreto.legislativo", "58", "1998"),
    "codice del consumo": ("decreto.legislativo", "206", "2005"), "cod. consumo": ("decreto.legislativo", "206", "2005"),
    "cod. cons.": ("decreto.legislativo", "206", "2005"), "codice consumo": ("decreto.legislativo", "206", "2005"),
    "c. cons.": ("decreto.legislativo", "206", "2005"), "cod. cons": ("decreto.legislativo", "206", "2005"),
    "tus": ("decreto.legislativo", "346", "1990"), "t.u.s.": ("decreto.legislativo", "346", "1990"),
    "tuel": ("decreto.legislativo", "267", "2000"),
    "ccii": ("decreto.legislativo", "14", "2019"), "c.c.i.i.": ("decreto.legislativo", "14", "2019"),
    "codice della crisi": ("decreto.legislativo", "14", "2019"),
    "cds": ("decreto.legislativo", "285", "1992"), "codice della strada": ("decreto.legislativo", "285", "1992"),
    "cap": ("decreto.legislativo", "209", "2005"), "codice delle assicurazioni": ("decreto.legislativo", "209", "2005"),
    "tuir": ("decreto.del.presidente.della.repubblica", "917", "1986"),
    "tusg": ("decreto.del.presidente.della.repubblica", "115", "2002"),
    "t.u. spese di giustizia": ("decreto.del.presidente.della.repubblica", "115", "2002"),
    "statuto dei lavoratori": ("legge", "300", "1970"), "stat. lav.": ("legge", "300", "1970"),
    "legge fallimentare": ("regio.decreto", "267", "1942"), "l. fall.": ("regio.decreto", "267", "1942"),
    "t.u. immigrazione": ("decreto.legislativo", "286", "1998"), "tui": ("decreto.legislativo", "286", "1998"),
    "testo unico immigrazione": ("decreto.legislativo", "286", "1998"),
    "codice antimafia": ("decreto.legislativo", "159", "2011"),
    "codice privacy": ("decreto.legislativo", "196", "2003"),
    "cad": ("decreto.legislativo", "82", "2005"),
    # v0.29 — atti entrati nel corpus locale, con i nomi con cui si citano davvero
    "codice della privacy": ("decreto.legislativo", "196", "2003"), "cod. privacy": ("decreto.legislativo", "196", "2003"),
    "codice dell'amministrazione digitale": ("decreto.legislativo", "82", "2005"),
    "testo unico della finanza": ("decreto.legislativo", "58", "1998"),
    "t.u.i.r.": ("decreto.del.presidente.della.repubblica", "917", "1986"),
    "t.u. edilizia": ("decreto.del.presidente.della.repubblica", "380", "2001"),
    "testo unico edilizia": ("decreto.del.presidente.della.repubblica", "380", "2001"),
    "testo unico dell'edilizia": ("decreto.del.presidente.della.repubblica", "380", "2001"),
    "legge gelli": ("legge", "24", "2017"), "legge gelli-bianco": ("legge", "24", "2017"),
    "legge sul divorzio": ("legge", "898", "1970"), "l. div.": ("legge", "898", "1970"),
    "legge cirinnà": ("legge", "76", "2016"), "legge cirinna": ("legge", "76", "2016"),
    "legge professionale forense": ("legge", "247", "2012"), "ordinamento forense": ("legge", "247", "2012"),
    "l.p.f.": ("legge", "247", "2012"),
    "legge sull'equo compenso": ("legge", "49", "2023"),
    "legge pinto": ("legge", "89", "2001"),
    "legge antitrust": ("legge", "287", "1990"),
    "riforma cartabia": ("decreto.legislativo", "149", "2022"),
    "regole tecniche pct": ("decreto", "44", "2011"),
    "correttivo cartabia": ("decreto.legislativo", "164", "2024"),
    # v0.36 — leggi del lavoro entrate nel corpus, con i nomi univoci con cui si citano («jobs act»,
    # «collegato lavoro», «Fornero» restano fuori: ciascuno indica piu' atti)
    "testo unico sicurezza": ("decreto.legislativo", "81", "2008"),
    "t.u. sicurezza": ("decreto.legislativo", "81", "2008"),
    "testo unico sulla sicurezza": ("decreto.legislativo", "81", "2008"),
    "testo unico salute e sicurezza": ("decreto.legislativo", "81", "2008"),
    "t.u.s.l.": ("decreto.legislativo", "81", "2008"),
    "testo unico maternità": ("decreto.legislativo", "151", "2001"),
    "testo unico maternita": ("decreto.legislativo", "151", "2001"),
    "t.u. maternità": ("decreto.legislativo", "151", "2001"), "t.u. maternita": ("decreto.legislativo", "151", "2001"),
    "codice delle pari opportunità": ("decreto.legislativo", "198", "2006"),
    "codice delle pari opportunita": ("decreto.legislativo", "198", "2006"),
    "codice pari opportunità": ("decreto.legislativo", "198", "2006"),
    "codice pari opportunita": ("decreto.legislativo", "198", "2006"),
    "t.u.p.i.": ("decreto.legislativo", "165", "2001"),
    "testo unico pubblico impiego": ("decreto.legislativo", "165", "2001"),
    "testo unico del pubblico impiego": ("decreto.legislativo", "165", "2001"),
    "decreto dignità": ("decreto.legge", "87", "2018"), "decreto dignita": ("decreto.legge", "87", "2018"),
    "decreto trasparenza": ("decreto.legislativo", "104", "2022"),
    "decreto whistleblowing": ("decreto.legislativo", "24", "2023"),
    "statuto del lavoro autonomo": ("legge", "81", "2017"),
    "decreto salario giusto": ("decreto.legge", "62", "2026"),
}

#: Atti numerati il cui URN anno-only risolve male su normattiva: serve la forma DATATA
#: (AAAA-MM-GG al posto dell'anno) ed eventualmente la variante allegato, come per i codici.
#: Voce -> (data completa, varianti allegato da tentare in fallback). Debito sentinella #19.
DATE_TESTI_UNICI = {
    ("decreto.legislativo", "346", "1990"): ("1990-10-31", [":1"]),  # T.U. successioni e donazioni
}

_MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
         "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}


def _urn_atto(tipo: str, numero: str, anno: str):
    """URN di un atto numerato, con la forma datata per i testi unici censiti."""
    speciale = DATE_TESTI_UNICI.get((tipo, numero, anno))
    if speciale:
        data, varianti = speciale
        return f"urn:nir:stato:{tipo}:{data};{numero}", list(varianti)
    urn_sp = URN_SPECIALI.get((tipo, numero, anno))
    if urn_sp:
        return urn_sp[0], list(urn_sp[1])
    return f"urn:nir:stato:{tipo}:{anno};{numero}", []


def _clean(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    return " ".join(s.split()).strip()


def _art_token(art: str) -> str:
    """'163' -> 'art163'; '281-undecies' -> 'art281undecies'; '196 quater' -> 'art196quater'."""
    a = _clean(art).lower().replace("-", "").replace(" ", "")
    return "art" + a


_RX_ART = re.compile(
    r"artt?\.?\s*([0-9]+(?:\.[0-9]+(?![0-9]))?(?:[\s-]*(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|nonies|"
    r"decies|undecies|duodecies|terdecies|quaterdecies|quinquiesdecies|sexiesdecies|"
    r"septiesdecies|octiesdecies|noviesdecies|vicies|semel)\b)*(?:\.[0-9]+(?![0-9]))?)")
# v0.29: «art. 132.1 CAP», «art. 4-quinquies.1 TUF», «art. 69.1 TUB» — articoli col punto, che il
# corpus ora porta. Prima la regex si fermava a «132» e si leggeva l'articolo SBAGLIATO.


def _anno4(aa: str) -> str:
    """'98' → '1998', '22' → '2022' (pivot sull'anno corrente); le quattro cifre restano."""
    aa = str(aa)
    if len(aa) != 2:
        return aa
    corrente = datetime.now().year % 100
    return ("20" if int(aa) <= corrente else "19") + aa


def _art_norm(grezzo: str) -> str:
    return grezzo.replace("nonies", "novies")


def _senza_parentesi(low: str) -> str:
    """Le parentesi di una claim card contengono l'atto MODIFICANTE o un alias («(come
    modificato dal D.Lgs. 149/2022)», «(Codice del consumo)»): non sono l'atto citato.
    Si sostituiscono con spazi a parita' di lunghezza, cosi' le posizioni restano quelle."""
    return re.sub(r"\([^()]*\)", lambda m: " " * len(m.group(0)), low)


def _candidati_atto(low: str) -> list:
    """Tutti gli atti riconoscibili nel testo, con la POSIZIONE in cui compaiono:
    [(pos, urn_base, varianti, descr)]. Chi chiama sceglie per posizione."""
    out = []
    # 1) codici noti (c.p.c., c.c., ...) e loro alias
    for alias in sorted(list(CODICI) + list(ALIAS_CODICI), key=len, reverse=True):
        canon = ALIAS_CODICI.get(alias, alias)
        pattern = re.escape(alias.rstrip(".")).replace(r"\.", r"\.?\s*")
        for m in re.finditer(r"(?:^|[\s,;])(" + pattern + r"\.?)(?=$|[\s,;)])", low):
            urn, varianti = CODICI[canon]
            out.append((m.start(1), urn, varianti, canon))
    # 2) sigle e nomi correnti (TUB, Cod. consumo, CCII, ...)
    for sigla in sorted(SIGLE_ATTI, key=len, reverse=True):
        pattern = re.escape(sigla.rstrip(".")).replace(r"\.", r"\.?\s*")
        for m in re.finditer(r"(?:^|[\s,;(])(" + pattern + r"\.?)(?=$|[\s,;).])", low):
            tipo, numero, anno = SIGLE_ATTI[sigla]
            urn, varianti = _urn_atto(tipo, numero, anno)
            out.append((m.start(1), urn, varianti, f"{_alias_tipo(tipo)} {numero}/{anno}"))
    # 3) atti numerati: "D.Lgs. 149/2022", "legge 241/1990", "L. 27 luglio 2000 n. 212",
    #    "D.Lgs. 4 marzo 2010, n. 28", "L. 431/98" (anno a due cifre), "legge n. 689 del 1981".
    #    v0.29: la descrizione e' CANONICA («d.lgs. 28/2010» anche da «decreto legislativo 28/2010»):
    #    il corpus locale la riconosce comunque la si scriva — prima la forma lunga andava in rete.
    for alias in sorted(TIPI_ATTO, key=len, reverse=True):
        pattern = re.escape(alias.rstrip(".")).replace(r"\.", r"\.?\s*")
        sigla = _alias_tipo(TIPI_ATTO[alias])
        for m2 in re.finditer(r"(?:^|[\s,;(])(" + pattern + r"\.?\s*(?:n\.?\s*)?([0-9]{1,4})\s*/\s*([0-9]{4}|[0-9]{2})(?![0-9])(?![/.\-][0-9]))", low):
            numero, anno = str(int(m2.group(2))), _anno4(m2.group(3))
            urn, varianti = _urn_atto(TIPI_ATTO[alias], numero, anno)
            out.append((m2.start(1), urn, varianti, f"{sigla} {numero}/{anno}"))
        for m3 in re.finditer(r"(?:^|[\s,;(])(" + pattern + r"\.?\s*([0-9]{1,2})\s+([a-z]+)\s+([0-9]{4})\s*,?\s*n\.?\s*([0-9]{1,4}))", low):
            anno, numero = m3.group(4), str(int(m3.group(5)))
            urn, varianti = _urn_atto(TIPI_ATTO[alias], numero, anno)
            out.append((m3.start(1), urn, varianti, f"{sigla} {numero}/{anno}"))
        for m4 in re.finditer(r"(?:^|[\s,;(])(" + pattern + r"\.?\s*n\.?\s*([0-9]{1,4})\s+del(?:l')?\s*([0-9]{4})(?![0-9]))", low):
            numero, anno = str(int(m4.group(2))), m4.group(3)
            urn, varianti = _urn_atto(TIPI_ATTO[alias], numero, anno)
            out.append((m4.start(1), urn, varianti, f"{sigla} {numero}/{anno}"))
        for m5 in re.finditer(r"(?:^|[\s,;(])(" + pattern + r"\.?\s*[0-9]{1,2}[/.][0-9]{1,2}[/.]([0-9]{4})\s*,?\s*n\.?\s*([0-9]{1,4}))", low):
            anno, numero = m5.group(2), str(int(m5.group(3)))      # «D.M. 10/03/2014 n. 55»
            urn, varianti = _urn_atto(TIPI_ATTO[alias], numero, anno)
            out.append((m5.start(1), urn, varianti, f"{sigla} {numero}/{anno}"))
    # a parita' di posizione vince il match piu' lungo (gia' garantito dall'ordine per lunghezza)
    visti, dedup = set(), []
    for c in sorted(out, key=lambda c: c[0]):
        if c[0] in visti:
            continue
        visti.add(c[0])
        dedup.append(c)
    return dedup


def _alias_tipo(tipo: str) -> str:
    for alias, t in TIPI_ATTO.items():
        if t == tipo and alias.endswith("."):
            return alias
    return tipo


def parse_riferimento(rif: str):
    """Ritorna (urn_base, varianti_allegato, art|None, descrizione) oppure None.

    v0.25 — l'atto e' quello citato PER PRIMO nel riferimento, fuori dalle parentesi. Il bug
    misurato il 17/09/2026: per «art. 5, comma 1, D.Lgs. 4 marzo 2010, n. 28 (come modificato
    dal D.Lgs. 149/2022)» il parser provava prima la forma «N/AAAA» e trovava il 149/2022: tre
    lenti hanno letto l'art. 5 del decreto sbagliato, in entrambi i round.
    """
    r = _clean(rif)
    low = r.lower().rstrip(".") + "."
    art = None
    m = _RX_ART.search(low)
    if m:
        art = _art_norm(m.group(1))
    pulito = _senza_parentesi(low)
    cands = _candidati_atto(pulito) or _candidati_atto(low)
    if not cands:
        return None
    _, urn, varianti, descr = cands[0]
    return urn, list(varianti), art, descr


def parse_riferimenti_multipli(rif: str) -> list:
    """Tutte le norme citate in un riferimento composto («art. 210 c.p.c. e art. 119, co. 4, TUB»,
    «artt. 2033 e 2946 c.c.»): lista di (urn_base, varianti, art, descr), nell'ordine del testo.
    Ogni «art. N» prende l'atto citato per primo DOPO di se' (e prima del successivo «art.»);
    se dopo non c'e' nulla, l'atto che lo precede. Le parentesi non contano (atto modificante).
    Usato dal Livello 0 per verificare separatamente le parti di una claim composta.
    """
    r = _clean(rif)
    low = _senza_parentesi(r.lower().rstrip(".") + ".")
    atti = _candidati_atto(low)
    if not atti:
        return []
    arts = []
    for m in _RX_ART.finditer(low):
        arts.append((m.start(), m.end(), _art_norm(m.group(1))))
        # «artt. 2033 e 2946»: i numeri che seguono senza «art.» appartengono allo stesso atto
        coda = low[m.end():]
        for mm in re.finditer(r"^(?:\s*(?:,|e|ed)\s*)([0-9]+(?:\.[0-9]+(?![0-9]))?(?:[\s-]*(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|nonies|decies|undecies|duodecies)\b)*)", coda):
            arts.append((m.end() + mm.start(1), m.end() + mm.end(1), _art_norm(mm.group(1))))
            coda = coda[mm.end():]
            break
    if not arts:
        urn, varianti, descr = atti[0][1], atti[0][2], atti[0][3]
        return [(urn, list(varianti), None, descr)]
    out = []
    for i, (a0, a1, art) in enumerate(arts):
        limite = arts[i + 1][0] if i + 1 < len(arts) else len(low)
        dopo = [c for c in atti if a1 <= c[0] < limite]
        prima = [c for c in atti if c[0] < a0]
        scelto = dopo[0] if dopo else (prima[-1] if prima else atti[0])
        out.append((scelto[1], list(scelto[2]), art, scelto[3]))
    return out


def costruisci_url(urn_base: str, suffisso_allegato: str, art, vig) -> str:
    urn = urn_base + suffisso_allegato
    if art:
        urn += "~" + _art_token(art)
    urn += "!vig=" + (vig or "")
    return "https://www.normattiva.it/uri-res/N2Ls?" + urn


# ---------------------------------------------------------------- estrazione

class _Testo(HTMLParser):
    """Estrae il testo dei blocchi 'bodyTesto' (corpo dell'articolo su normattiva)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._dentro = 0
        self._buf = []

    def handle_starttag(self, tag, attrs):
        klass = dict(attrs).get("class", "") or ""
        if self._dentro or "bodytesto" in klass.lower().replace(" ", ""):
            self._dentro += 1

    def handle_endtag(self, tag):
        if self._dentro:
            self._dentro -= 1

    def handle_data(self, data):
        if self._dentro:
            self._buf.append(data)

    def testo(self) -> str:
        righe = [" ".join(x.split()) for x in "".join(self._buf).splitlines()]
        return "\n".join([r for r in righe if r]).strip()


def _strip_all(html: str) -> str:
    txt = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    return " ".join(txt.split())


def estrai_testo_norma(html: str) -> str:
    p = _Testo()
    try:
        p.feed(html)
    except Exception:
        return ""
    testo = p.testo()
    if len(testo) >= 40:
        return testo
    # fallback: pagina intera spogliata, cerca l'attacco dell'articolo
    piatto = _strip_all(html)
    m = re.search(r"Art\.\s*[0-9]", piatto)
    if m and len(piatto) - m.start() > 80:
        return piatto[m.start(): m.start() + 4000]
    return ""


def _valida_articolo(testo: str, art) -> bool:
    """True se il testo estratto e' davvero l'articolo richiesto (non il preambolo dell'atto).

    Trappola nota: per i codici (c.p.c., c.c., ...) l'URN senza suffisso allegato puo' risolvere
    sul R.D. di approvazione e restituire l'art. 1 del decreto invece dell'articolo del codice.

    L'intestazione si cerca A INIZIO RIGA (o a inizio testo): il preambolo di un decreto puo'
    citare inline proprio l'articolo cercato ("Visto l'art. 17, terzo comma, della legge...")
    e un match ovunque-nel-testo lo scambiava per l'intestazione — falso OK sul testo sbagliato
    (visto succedere con art. 17 D.Lgs. 346/1990). Meglio un VAI_LIVE in piu' che un testo falso.
    """
    if not art:
        return True
    m = re.match(r"([0-9]+)(.*)", _clean(art).lower())
    if not m:
        return True
    numero, resto = m.group(1), m.group(2)
    mp = re.match(r"\.([0-9]+)", resto)
    if mp:   # «132.1»: il punto e il sottonumero fanno parte del numero (l'art. 132 e' un ALTRO articolo)
        numero, resto = numero + r"\." + mp.group(1), resto[mp.end():]
    suffissi = re.findall(r"(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies|terdecies)",
                          resto)
    pat = r"(?m)^\s*\(?\(?[Aa]rt\.?\s*\(?\(?" + numero
    for s in suffissi:
        pat += r"[\s.\-]*" + s
    pat += r"(?![0-9])(?!\.[0-9])" + ("" if suffissi else r"(?![\s.\-]*(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies|terdecies))")
    return re.search(pat, testo) is not None


_TITOLI_TIPO = {
    "decreto.legislativo": ("decreto legislativo",),
    "legge": ("legge",),
    "decreto.legge": ("decreto-legge", "decreto legge"),
    "decreto.del.presidente.della.repubblica": ("decreto del presidente della repubblica", "d.p.r."),
    "regio.decreto": ("regio decreto",),
    "costituzione": ("costituzione",),
    "decreto": ("decreto",),
}


def titolo_atto(html: str):
    """Il titolo dell'atto dalla pagina normattiva («DECRETO LEGISLATIVO 4 marzo 2010, n. 28»), o None."""
    m = re.search(r"(?is)<title>\s*(.*?)\s*</title>", html or "")
    if not m:
        return None
    t = " ".join(m.group(1).split())
    t = re.sub(r"\s*-\s*Normattiva\s*$", "", t, flags=re.I).strip()
    return t or None


def _estremi_urn(urn_base: str):
    """(tipo, numero, anno) da un URN normattiva, con o senza data completa e suffisso allegato."""
    m = re.search(r"urn:nir:[^:]+:([a-z.]+):(\d{4})(?:-\d{2}-\d{2})?(?:;(\d+))?", urn_base or "")
    if not m:
        return None, None, None
    return m.group(1), m.group(3), m.group(2)


def _valida_atto(html: str, urn_base: str) -> bool:
    """La pagina scaricata e' davvero l'ATTO richiesto?

    Difesa contro il bug del 17/09/2026 (art. 5 del D.Lgs. 149/2022 servito per l'art. 5 del
    D.Lgs. 28/2010): il titolo della pagina («DECRETO LEGISLATIVO 4 marzo 2010, n. 28») deve
    portare lo stesso tipo, numero e anno dell'URN. Senza titolo non si puo' validare e non
    si blocca (il chiamante lo dichiara con atto_validato=False). Meglio un VAI_LIVE in piu'
    che il testo di un altro atto.
    """
    titolo = titolo_atto(html)
    if not titolo:
        return True
    tipo, numero, anno = _estremi_urn(urn_base)
    if not tipo:
        return True
    t = titolo.lower()
    parole = _TITOLI_TIPO.get(tipo)
    if parole:
        if tipo == "legge":
            if not t.startswith("legge"):
                return False
        elif tipo == "decreto":
            if not t.startswith("decreto") or t.startswith(("decreto legislativo", "decreto-legge", "decreto legge",
                                                            "decreto del presidente")):
                return False
        elif not any(t.startswith(pw) for pw in parole):
            return False
    if numero:
        mn = re.search(r"\bn\.?\s*(\d+)", t)
        if mn and mn.group(1) != str(int(numero)):
            return False
    if anno:
        ma = re.search(r"\b(1[89]\d{2}|20\d{2})\b", t)
        if ma and ma.group(1) != anno:
            return False
    return True


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "it"})
    with urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _errore_transitorio(e: Exception) -> bool:
    """Vale la pena ritentare? 5xx/429 e guasti di rete intermittenti si'.

    DNS irrisolvibile (= si e' offline) e 4xx no: ritentare li' non recupera niente e
    allunga solo il tempo del degrado VAI_LIVE, che deve restare immediato.
    """
    if isinstance(e, HTTPError):
        return e.code >= 500 or e.code == 429
    if isinstance(e, URLError) and isinstance(getattr(e, "reason", None), socket.gaierror):
        return False
    return True


def fetch_con_retry(url: str, attese=RETRY_ATTESE):
    """Ritorna (html, tentativi_fatti). Rilancia l'eccezione se anche i retry falliscono."""
    tentativi = 0
    while True:
        tentativi += 1
        try:
            return fetch(url), tentativi
        except Exception as e:
            if tentativi > len(attese) or not _errore_transitorio(e):
                raise
            time.sleep(attese[tentativi - 1])


# ---------------------------------------------------------------- cache

def _cache_key(urn_url: str) -> str:
    return hashlib.sha1(urn_url.encode("utf-8")).hexdigest()[:20]


def cache_get(cache_dir: Path, url: str, ttl_ore: float):
    f = cache_dir / (_cache_key(url) + ".json")
    if not f.exists():
        return None
    try:
        dati = json.loads(f.read_text(encoding="utf-8"))
        quando = datetime.fromisoformat(dati["fetched_at"])
    except Exception:
        return None
    if datetime.now() - quando > timedelta(hours=ttl_ore):
        return None
    return dati


def cache_put(cache_dir: Path, url: str, dati: dict):
    cache_dir.mkdir(parents=True, exist_ok=True)
    f = cache_dir / (_cache_key(url) + ".json")
    f.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- esiti

def _stampa_ok(dati: dict, as_json: bool):
    if as_json:
        print(json.dumps({"verdetto": "OK", **dati}, ensure_ascii=False, indent=2))
        return
    print(f"OK {dati.get('riferimento', '')}".rstrip())
    print(f"FONTE: {dati['url']}")
    if dati.get("fonte"):
        print(f"FONTE-TIPO: {dati['fonte']}" + (f"  (fetch: {dati['url_fetch']})" if dati.get("url_fetch") and dati["url_fetch"] != dati["url"] else ""))
    if dati.get("versione"):
        print(f"VERSIONE: {dati['versione']}")
        if dati.get("vig"):
            print(f"DATA-EVENTO: {dati['vig']}")
    else:
        print(f"VIGENTE AL: {dati.get('vig') or 'testo vigente a oggi'}")
    if dati.get("snapshot_oltre_vita"):
        print(f"SNAPSHOT NON CONFERMATO dal {dati.get('snapshot_confermato_il') or str(dati.get('fetched_at') or '')[:10]}"
              + (f" — {dati['motivo_rete']}" if dati.get("motivo_rete") else ""))
    if dati.get("avvertenza"):
        print(f"AVVERTENZA: {dati['avvertenza']}")
    if dati.get("troncato"):
        print(f"TRONCATO: si' ({dati.get('caratteri_totali')} caratteri totali; --integrale per tutto)")
    if dati.get("da_codice_locale"):
        nota = f"  ({dati.get('fonte_locale', 'codice locale datato')})"
    elif dati.get("da_storico"):
        nota = "  (testo storico: cache permanente per versione)" if dati.get("da_cache") else "  (testo storico: scaricato ora, ora in cache permanente)"
    elif dati.get("da_prewarm"):
        nota = "  (da cache pre-warm sentinella — per claim FONDANTI conferma comunque live, nucleo §3-ter)"
    elif dati.get("da_cache"):
        nota = "  (da cache di giornata)"
    else:
        nota = ""
    print(f"SCARICATO: {dati['fetched_at']}" + nota)
    print("TESTO:")
    print(dati["testo"])


def _vai_live(motivo: str, as_json: bool, extra: dict | None = None):
    if as_json:
        print(json.dumps({"verdetto": "VAI_LIVE", "motivo": motivo, **(extra or {})},
                         ensure_ascii=False, indent=2))
    else:
        print(f"VAI_LIVE {motivo}")
        for k, v in (extra or {}).items():
            print(f"{k.upper()}: {v}")
    sys.exit(0)


# ---------------------------------------------------------------- main

def recupera_norma(riferimento: str, data_evento: str = "", *, cache_dir=None,
                   ttl_ore: float = 24.0, no_cache: bool = False,
                   prewarm: bool = False, attese=None, fonte: str = "auto",
                   max_chars=None, usa_locale: bool = True, solo_locale: bool = False) -> dict:
    """Recupera il testo di una norma. NON stampa e NON esce: ritorna un dict.

    E' il cuore riusabile del fetch, estratto dalla CLI perche' anche dossier_fonti.py
    (pool di fonti condiviso, nucleo §3-sexies) ne ha bisogno: cosi' la logica di URN,
    cache e validazione dell'articolo vive in UN posto solo.

    Ritorna sempre un dict con almeno {'verdetto': 'OK'|'VAI_LIVE', 'riferimento': ...}.
    Con verdetto OK ci sono anche url / vig / fetched_at / testo (+ da_cache, da_prewarm).
    Con VAI_LIVE c'e' 'motivo' e, quando costruibile, 'url_tentato'.
    """
    # -1) RESOLVER FUORI NORMATTIVA (v0.16): EUR-Lex/CELLAR, Garante, Gazzetta Ufficiale.
    #     Competenza decisa dai marcatori del riferimento (o forzata con `fonte`); se nessuno
    #     e' competente si prosegue con normattiva esattamente come prima. Un errore
    #     IMPREVISTO del resolver non deve mai rompere il fetch: degrada a normattiva/VAI_LIVE
    #     (con $FONTI_DEBUG lo si vede su stderr).
    fonte = (fonte or "auto").lower()
    try:
        import resolver_fonti as _rf
        kw = dict(fonte=fonte, cache_dir=cache_dir, ttl_ore=ttl_ore, no_cache=no_cache,
                  prewarm=prewarm, attese=attese)
        if max_chars is not None:
            kw["max_chars"] = max_chars
        if solo_locale:
            # v0.29: `--offline` arriva anche ai resolver fuori normattiva. Prima un «art. 6 GDPR» in
            # modalita' offline apriva comunque EUR-Lex: su Cowork, con l'egress bloccato, un'attesa
            # di timeout e retry per una risposta che non poteva arrivare.
            kw["offline"] = True
        esito_r = _rf.recupera(riferimento, data_evento or "", **kw)
        if esito_r is not None:
            return esito_r
    except Exception as e:
        if os.environ.get("FONTI_DEBUG"):
            import traceback
            traceback.print_exc(file=sys.stderr)
        if fonte not in ("auto", "normattiva"):
            return {"verdetto": "VAI_LIVE", "riferimento": riferimento,
                    "motivo": f"resolver {fonte} fallito ({e.__class__.__name__}: {e}) — procedi live"}

    parsed = parse_riferimento(riferimento)
    if not parsed:
        return {"verdetto": "VAI_LIVE", "riferimento": riferimento,
                "motivo": f"riferimento non riconosciuto: {riferimento!r} (procedi live)"}

    urn_base, varianti, art, descr = parsed
    vig = data_evento or ""

    # 0) CODICI LOCALI DATATI (v0.16) — prima ancora della cache. Per c.p.c., c.c.,
    #    disp. att., preleggi e Costituzione il testo ufficiale normattiva vive gia' su
    #    disco (scripts/codice_locale.py, export Akoma Ntoso, snapshot datato): millisecondi
    #    invece di secondi, e funziona anche offline. Il modulo rifiuta DA SOLO i casi in
    #    cui il locale non basta — snapshot oltre vita utile, o data-evento anteriore
    #    all'ultima modifica dell'articolo (tempus regit actum) — e allora si prosegue
    #    esattamente come prima: cache, rete, VAI_LIVE.
    motivo_locale = ""
    locale_scaduto = None      # testo locale oltre la vita massima: si serve solo se la rete non risponde
    urn_corpus = ""
    slug = ""
    try:
        import codice_locale as _cl
        slug = _cl.slug_da_riferimento(descr, urn_base)
        urn_corpus = _cl.urn_permalink(slug) if slug else ""
    except Exception as e:
        _cl = None
        motivo_locale = f"corpus locale non consultabile ({e.__class__.__name__})"
    if art and usa_locale and _cl is not None:
        try:
            if slug:
                loc = _cl.articolo(art, slug, vig)
                if loc.get("verdetto") == "OK":
                    esito_loc = {
                        "verdetto": "OK", "da_codice_locale": True, "atto_validato": True,
                        "riferimento": riferimento, "descrizione": descr, "codice_locale": slug,
                        "url": (costruisci_url(urn_corpus, "", art, vig) if urn_corpus else
                                costruisci_url(urn_base, varianti[0] if varianti else "", art, vig)),
                        "vig": vig or None,
                        "fetched_at": loc["snapshot"] + "T00:00:00",
                        "fonte_locale": loc["fonte"], "vigore_da": loc.get("vigore_da"),
                        "datazione": loc.get("datazione"), "abrogato": loc.get("abrogato", False),
                        "rubrica": loc.get("rubrica", ""),
                        "snapshot_oltre_vita": bool(loc.get("snapshot_oltre_vita")),
                        "verificato_il": loc.get("verificato_il"), "in_movimento": bool(loc.get("in_movimento")),
                        "testo": (f"Art. {loc['token']}.\n"
                                  + (f"({loc['rubrica']}).\n" if loc.get("rubrica") else "")
                                  + loc["testo"]),
                    }
                    if loc.get("vigore_a"):
                        esito_loc["vigore_a"] = loc["vigore_a"]
                    if not loc.get("snapshot_oltre_vita"):
                        return esito_loc
                    # v0.29: oltre la vita massima il locale NON tace piu'. Con la rete si preferisce
                    # normattiva (cache di giornata o live); senza rete (Cowork, --offline) si serve il
                    # locale DICHIARANDOLO: il Livello 0 tratta come residue le claim fondanti.
                    esito_loc["snapshot_confermato_il"] = loc.get("snapshot_confermato_il")
                    esito_loc["avvertenza"] = loc.get("avviso")
                    if solo_locale:
                        return esito_loc
                    locale_scaduto = esito_loc
                    motivo_locale = "snapshot locale oltre la vita massima: provo normattiva"
                else:
                    motivo_locale = loc.get("motivo", "")
            else:
                motivo_locale = f"atto «{descr}» non nel corpus locale"
        except Exception as e:
            motivo_locale = f"corpus locale non consultabile ({e.__class__.__name__})"
    # 0-bis) TESTO STORICO (v0.25, Fase 4 — D5.4). Il locale ha taciuto e la claim e' datata nel
    #        passato: prima del live si passa da storico.py, che serve dalla cache PERMANENTE per
    #        versione (un testo storico non cambia) e, se manca, scarica UNA volta il permalink
    #        URN datato. In `solo_locale` (Livello 0 offline, pool) si legge solo la cache.
    #        Misurato sulla pratica di riferimento: 9 claim su 22 erano rifiuti «data anteriore
    #        alla versione vigente», rifatti live a ogni round.
    if art and usa_locale and vig and fonte in ("auto", "normattiva") and locale_scaduto is None:
        try:
            import storico as _st
            if _st.e_storico(vig):
                es = _st.recupera(riferimento, vig, offline=solo_locale)
                if es.get("verdetto") == "OK":
                    testo = es["testo"]
                    return {
                        "verdetto": "OK", "da_storico": True, "da_cache": bool(es.get("da_cache")),
                        "atto_validato": True, "riferimento": riferimento, "descrizione": descr,
                        "codice_locale": es.get("codice_locale"), "url": es["url"], "vig": vig,
                        "fetched_at": es.get("fetched_at"), "fonte": es.get("fonte"),
                        "versione": es.get("versione"), "vigore_da": es.get("versione_da"),
                        "vigore_a": es.get("versione_a"), "atto_titolo": es.get("atto_titolo"),
                        "abrogato": bool(re.match(r"^\s*(?:art\.[^\n]*\n)?\(?\(?\s*ARTICOLO ABROGATO", testo.strip(), re.I)),
                        "file": es.get("file"), "testo": testo,
                    }
                motivo_locale = (motivo_locale + "; " if motivo_locale else "") + "storico: " + str(es.get("motivo", ""))
        except Exception as e:
            if os.environ.get("FONTI_DEBUG"):
                import traceback
                traceback.print_exc(file=sys.stderr)
            motivo_locale = (motivo_locale + "; " if motivo_locale else "") + f"storico non consultabile ({e.__class__.__name__})"
    if solo_locale:
        return {"verdetto": "VAI_LIVE", "riferimento": riferimento, "descrizione": descr,
                "motivo": motivo_locale or "solo_locale: articolo non nel corpus",
                "url_tentato": costruisci_url(urn_corpus or urn_base, "", art, vig)}
    if prewarm and PREWARM_DIR is not None:
        dir_cache = PREWARM_DIR
    else:
        dir_cache = Path(cache_dir) if cache_dir else cache_dir_default()
    # URN da tentare, nell'ordine: quello DATATO del corpus (codici.json: data completa e suffisso di
    # allegato giusto, un solo fetch invece di preambolo + varianti), poi base e varianti dedotte.
    urn_tentativi = []
    for u in ([urn_corpus] if urn_corpus else []) + [urn_base + suff for suff in [""] + varianti]:
        if u and u not in urn_tentativi:
            urn_tentativi.append(u)

    # 1) prima TUTTE le cache, in ordine di freschezza decrescente: sessione condivisa ->
    #    vecchia cartella relativa alla CWD (sola lettura, compat) -> pre-warm sentinella.
    if not no_cache:
        altre = [] if prewarm else [(CACHE_LEGACY, ttl_ore, False)]
        if not prewarm and PREWARM_DIR is not None:
            altre.append((PREWARM_DIR, PREWARM_TTL_ORE, True))
        for urn_t in urn_tentativi:
            url = costruisci_url(urn_t, "", art, vig)
            hit = cache_get(dir_cache, url, ttl_ore)
            if hit:
                return {"verdetto": "OK", "da_cache": True, **hit}
            for altra_dir, altro_ttl, e_prewarm in altre:
                hit = cache_get(altra_dir, url, altro_ttl)
                if hit:
                    esito = {"verdetto": "OK", "da_cache": True, **hit}
                    if e_prewarm:
                        esito["da_prewarm"] = True
                    return esito

    # 2) poi i fetch live (con retry sui guasti transitori: un 500 intermittente non deve
    #    costare il degrado al browser di tutte e cinque le lenti)
    ultimo_errore = "testo non estraibile dalla pagina"
    fetch_fatti = 0
    attese = RETRY_ATTESE if attese is None else tuple(attese)
    for urn_t in urn_tentativi:
        url = costruisci_url(urn_t, "", art, vig)
        try:
            html, n = fetch_con_retry(url, attese)
            fetch_fatti += n
        except Exception as e:  # rete assente, timeout, HTTP error (anche dopo i retry)
            fetch_fatti += 1 + (len(attese) if _errore_transitorio(e) else 0)
            ultimo_errore = f"fetch fallito ({e.__class__.__name__})"
            if not isinstance(e, HTTPError):
                # rete giu' (DNS, proxy che rifiuta, timeout): gli altri URN stanno sullo stesso host,
                # ritentarli moltiplica solo l'attesa (Cowork con egress bloccato)
                break
            continue
        testo = estrai_testo_norma(html)
        if not testo:
            ultimo_errore = "pagina scaricata ma testo non estraibile"
            continue
        if not _valida_articolo(testo, art):
            ultimo_errore = f"la pagina risolta non contiene l'art. {art} (probabile preambolo dell'atto)"
            continue
        titolo = titolo_atto(html)
        if not _valida_atto(html, urn_base):
            ultimo_errore = (f"la pagina risolta e' un ALTRO atto («{titolo}») rispetto a «{descr}»: "
                             "URN non risolto da normattiva")
            continue
        dati = {
            "riferimento": riferimento, "descrizione": descr, "url": url,
            "vig": vig or None, "fetched_at": datetime.now().isoformat(timespec="seconds"),
            "testo": testo, "atto_validato": bool(titolo),
        }
        if titolo:
            dati["atto_titolo"] = titolo
        if not no_cache:
            cache_put(dir_cache, url, dati)
        esito = {"verdetto": "OK", **dati}
        if fetch_fatti > 1:
            esito["tentativi"] = fetch_fatti
        return esito

    if locale_scaduto is not None:
        locale_scaduto["motivo_rete"] = f"{ultimo_errore} (normattiva non raggiungibile: servito lo snapshot locale)"
        return locale_scaduto
    esito = {"verdetto": "VAI_LIVE", "riferimento": riferimento,
             "motivo": f"{ultimo_errore} — conferma su normattiva via browser (degrado §5)",
             "url_tentato": costruisci_url(urn_corpus or urn_base, "", art, vig)}
    if fetch_fatti > 1:
        esito["tentativi"] = fetch_fatti
    return esito


def gestisci_norma(args):
    """Wrapper CLI sottile su recupera_norma(): tutta la logica sta li'."""
    if args.dry_run:
        try:
            import resolver_fonti as _rf
            ric = _rf.riconosci(args.riferimento, args.fonte)
        except Exception:
            ric = None
        if ric:
            print("DRY_RUN")
            print(json.dumps(ric, ensure_ascii=False))
            if ric.get("resolver") == "eurlex" and ric.get("celex"):
                print(_rf.EURLEX + ric["celex"] + "   (testo via " + _rf.CELLAR + ric["celex"] + ")")
            elif ric.get("resolver") == "garante" and ric.get("docweb"):
                print(_rf.GARANTE_DOCWEB + ric["docweb"])
            elif ric.get("resolver") == "garante" and ric.get("data"):
                print(_rf.url_ricerca_garante("", ric["data"], ric["data"]))
            elif ric.get("resolver") == "gu" and ric.get("modo") == "sommario" and ric.get("data") and ric.get("numero_gu"):
                print(_rf.url_sommario_gu(ric["data"], ric["numero_gu"]))
            elif ric.get("resolver") == "gu" and ric.get("modo") == "atto":
                print("https://www.normattiva.it/uri-res/N2Ls?" + ric["urn"] + "   (-> codice redazionale -> ELI G.U.)")
            return
        parsed = parse_riferimento(args.riferimento)
        if not parsed:
            _vai_live(f"riferimento non riconosciuto: {args.riferimento!r} (procedi live)", args.json)
        urn_base, varianti, art, _ = parsed
        print("DRY_RUN")
        for suff in [""] + varianti:
            print(costruisci_url(urn_base, suff, art, args.data_evento or ""))
        return

    esito = recupera_norma(args.riferimento, args.data_evento or "",
                           cache_dir=args.cache_dir, ttl_ore=args.ttl_ore,
                           no_cache=args.no_cache, prewarm=args.prewarm,
                           fonte=args.fonte, max_chars=(0 if args.integrale else None),
                           solo_locale=bool(getattr(args, "offline", False)))

    try:  # delta v3 C-2: il richiamo della norma finisce in telemetria (R8 lo pretende)
        import norma as _norma
        _norma.registra_richiamo(args.riferimento, esito=str((esito or {}).get('verdetto') or ''), script='fonti_fetch')
    except Exception:
        pass
    if esito["verdetto"] == "OK":
        _stampa_ok(esito, args.json)
        return
    extra = {k: v for k, v in esito.items() if k in ("url_tentato", "ricerca", "websearch", "candidati")}
    if isinstance(extra.get("candidati"), list):
        extra["candidati"] = "; ".join(f"doc. web {c['docweb']} — {c['titolo']}" + (f" (Registro n. {c['registro_n']})" if c.get("registro_n") else "")
                                       for c in extra["candidati"]) if not args.json else extra["candidati"]
    _vai_live(esito["motivo"], args.json, extra or None)


def domini_giurisprudenza() -> list:
    """La allowlist di wiki-studio/fonti/domini-giurisprudenza.json (piano v0.25, D6), in ordine."""
    try:
        from paths import WIKI as _W
        d = json.loads((_W / "fonti" / "domini-giurisprudenza.json").read_text(encoding="utf-8"))
        return [k for k, v in d.get("domini", {}).items() if v.get("tipo") != "professionale"]
    except Exception:
        return ["italgiure.giustizia.it", "cortecostituzionale.it", "brocardi.it", "altalex.com"]


def gestisci_sentenza(args):
    """Giurisprudenza (v0.25): gli ESTREMI si leggono dallo script — cache permanente e SentenzeWeb
    della Cassazione (cassazione_locale.py, 0,2 s) — e per il resto (attualita', massima, pronunce
    fuori copertura) si preparano le query pronte SULLA ALLOWLIST. L'attualita' resta all'agente."""
    s = _clean(args.sentenza)
    domini = domini_giurisprudenza()
    site = " OR ".join(f"site:{d}" for d in domini[:8])
    websearch = f"{s} ({site})"
    esiti = []
    try:
        import cassazione_locale as _cs
        for e in _cs.estremi_da_riferimento(s):
            if e.get("corte") != "cass":
                continue
            r = _cs.cerca(e["numero"], e["anno"], sezione=e.get("sezione"), tipo=e.get("tipo"),
                          kind=e.get("kind") or "snciv", offline=getattr(args, "offline", False))
            if r["verdetto"] == "ESISTE":
                r["confronto"] = _cs.confronta_estremi(e, r["estremi"])
            esiti.append({"dichiarati": e, **r})
    except Exception as ex:  # lo script prepara comunque le query
        esiti.append({"errore": f"{ex.__class__.__name__}: {ex}"})
    if args.json:
        print(json.dumps({"riferimento": s, "estremi": esiti, "websearch": websearch, "domini": domini,
                          "italgiure": "https://www.italgiure.giustizia.it/sncass/"}, ensure_ascii=False, indent=2))
        return
    if not esiti:
        print("NON_APPLICABILE nessuna pronuncia di Cassazione riconosciuta (ABF, merito, C. cost.): usa le query sotto")
    for r in esiti:
        if r.get("errore"):
            print(f"NON_RISOLTA {r['errore']}")
            continue
        d = r["dichiarati"]
        if r["verdetto"] == "ESISTE":
            import cassazione_locale as _cs
            c = r.get("confronto") or {}
            print(f"{'ESISTE' if c.get('coincidono', True) else 'ESTREMI_DIVERSI'} {_cs.formatta_estremi(r['estremi'])} · {r['fonte_tipo']}"
                  + (" · da cache" if r.get("da_cache") else ""))
            for df_ in c.get("differenze", []):
                print(f"  ✗ {df_['campo']}: dichiarato {df_['dichiarato']} · trovato {df_['trovato']}")
            if r.get("materia"):
                print(f"  materia SentenzeWeb: {', '.join(r['materia'])}")
            print(f"  URL: {r['url']}")
        elif r["verdetto"] == "NON_TROVATA":
            print(f"NON_TROVATA n. {d['numero']}/{d['anno']} — {r['motivo']}")
        else:
            print(f"NON_RISOLTA n. {d['numero']}/{d['anno']} — {r['motivo']}")
            print("  quando l'hai verificata: python3 scripts/cassazione_locale.py --numero "
                  f"{d['numero']} --anno {d['anno']} --registra --sezione … --tipo … --data AAAA-MM-GG --fonte URL --da VR")
    print("ATTUALITA' e MASSIMA restano all'agente (nucleo §3-ter). Query pronte, SOLO su questi domini:")
    print(f"  WebSearch: {websearch}")
    print(f"  italgiure: https://www.italgiure.giustizia.it/sncass/  ·  domini: {', '.join(domini)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fetch diretto fonti primarie (normattiva permalink URN), senza browser.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--riferimento", help='norma, es. "art. 163 c.p.c." / "art. 35 D.Lgs. 149/2022"')
    g.add_argument("--sentenza", help='estremi pronuncia, es. "Cass. civ. sez. III 12/03/2025 n. 7890"')
    ap.add_argument("--data-evento", help="vigenza alla data ISO AAAA-MM-GG (multivigenza): corpus locale se la data e' "
                                          "coperta dalla versione vigente, altrimenti storico.py (cache permanente per "
                                          "versione, un solo download), poi live; vuoto = vigente oggi")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--dry-run", action="store_true", help="stampa solo gli URL URN costruiti, nessun fetch")
    ap.add_argument("--no-cache", action="store_true", help="ignora e non scrivere la cache")
    ap.add_argument("--cache-dir", help="cartella cache (default <cartella di stato>/fonti-cache, $FONTI_CACHE)")
    ap.add_argument("--ttl-ore", type=float, default=24.0, help="validita' cache in ore (default 24)")
    ap.add_argument("--prewarm", action="store_true",
                    help="pass sentinella: scrive/legge la cache condivisa wiki-studio/normativa/cache (TTL 168h)")
    ap.add_argument("--fonte", default="auto",
                    choices=["auto", "normattiva", "eur-lex", "garante", "gu"],
                    help="forza il resolver (default auto: deciso dai marcatori del riferimento)")
    ap.add_argument("--integrale", action="store_true",
                    help="non troncare i testi lunghi (provvedimenti del Garante oltre 60.000 caratteri)")
    ap.add_argument("--offline", action="store_true",
                    help="niente rete: --riferimento solo corpus locale/storico in cache (anche EUR-Lex/Garante/G.U. "
                         "rispondono subito VAI_LIVE), --sentenza solo cache Cassazione")
    args = ap.parse_args(argv)

    if args.sentenza:
        gestisci_sentenza(args)
    else:
        gestisci_norma(args)


if __name__ == "__main__":
    main()
