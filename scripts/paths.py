"""Helper di percorsi PORTABILE (Mac + Windows). Niente path assoluti cablati."""
import sys
if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8 (accenti, frecce, emoji)
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
from pathlib import Path
import json
import os

def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def claude_skills_dir() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / "Claude" / "skills"
    return Path.home() / "Library" / "Application Support" / "Claude" / "skills"

ROOT = project_root()
WIKI = ROOT / "wiki-studio"
AUTORI = WIKI / "autori"


# --------------------------------------------------------------------- stato persistente

def _scrivibile(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        probe = p / ".probe-scrittura"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


#: cartella dello stato di SESSIONE dentro la cartella dell'attivita'
SESSIONE = ".studio-sessione"


def _nome_stato() -> str:
    """Nome della cartella dello stato PERSISTENTE: `.<nome del plugin>` dal manifest `.claude-plugin/plugin.json`;
    fuori da un plugin (repo pubblico del corpus, GitHub Action) `.<nome della cartella radice>`."""
    try:
        nome = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError, AttributeError):
        nome = None
    return "." + (str(nome).strip() if nome else ROOT.name)


NOME_STATO = _nome_stato()
_RX_VM = None


def _sotto(p: Path, radice: Path) -> bool:
    try:
        r_, c_ = radice.resolve(), p.resolve()
    except OSError:
        r_, c_ = radice, p
    return c_ == r_ or r_ in c_.parents


def _base_da_cwd(cwd: str) -> Path:
    """La cartella dell'ATTIVITA' a partire da un cwd qualsiasi, anche dopo un `cd` del modello (v0.32: in una pratica
    vera l'hook riceveva `pratiche/<slug>/lettura` come cwd e i gate non vedevano piu' la pratica). Ordine:
      1. Cowork locale, VM: /sessions/<x>/mnt/outputs;
      2. Cowork remoto: $CLAUDE_PROJECT_DIR (o /home/claude) se il cwd ci sta sotto;
      3. risalendo, il genitore della cartella `pratiche` che contiene davvero pratiche (`*/pratica.json`);
      4. risalendo, la prima cartella con `.studio-sessione/identita.json` fuori da `pratiche/`;
      5. il cwd."""
    global _RX_VM
    import re
    if _RX_VM is None:
        _RX_VM = re.compile(r"^(/sessions/[^/]+/mnt)(?:/|$)")
    s = str(cwd or "")
    m = _RX_VM.match(s)
    if m and (Path(m.group(1)) / "outputs").is_dir():
        return Path(m.group(1)) / "outputs"
    p = Path(s)
    if _entrypoint_remoto():
        radice = Path(os.environ.get("CLAUDE_PROJECT_DIR") or "/home/claude")
        if radice.is_dir() and _sotto(p, radice):
            return radice
    antenati = [p] + list(p.parents)[:10]
    for anc in antenati:
        if anc.name == "pratiche" and anc != p.anchor:
            try:
                if any(anc.glob("*/pratica.json")):
                    return anc.parent
            except OSError:
                pass
    for anc in antenati:
        dentro_pratica = any(x.parent.name == "pratiche" and (x / "pratica.json").exists() for x in [anc] + list(anc.parents)[:8])
        if not dentro_pratica and (anc / SESSIONE / "identita.json").exists():
            return anc
    return p


def base_sessione() -> Path:
    """La cartella dell'ATTIVITA' in cui vive lo stato della pratica (v0.30).

    Cowork LOCALE: gli hook girano sul computer e gli script nella VM; l'unica cartella che vedono entrambi e'
    quella dell'attivita' (`outputs`). Cowork REMOTO (diagnostica del 26/09/2026, CLAUDE_CODE_ENTRYPOINT=remote_cowork):
    hook e bash sono sulla stessa macchina Linux nel cloud, cartella dell'attivita' `/home/claude`. Ordine:
      1. $STUDIO_SESSIONE_BASE — la imposta l'hook con la cartella dell'attivita' ricavata dal `cwd` del proprio
         stdin (imposta_base → _base_da_cwd);
      2. _base_da_cwd(cwd): VM locale, radice del remoto, genitore di `pratiche/`, `.studio-sessione/identita.json`
         risalendo — qualunque sia il cwd (il modello puo' aver fatto cd dentro la pratica);
      3. nella VM di Cowork locale, l'unica /sessions/<x>/mnt/outputs;
      4. il cwd.
    """
    env = os.environ.get("STUDIO_SESSIONE_BASE")
    if env:
        return Path(env)
    cwd = os.getcwd()
    b = _base_da_cwd(cwd)
    if b != Path(cwd):
        return b
    try:
        vm = [p for p in Path("/sessions").glob("*/mnt/outputs") if p.is_dir()] if Path("/sessions").is_dir() else []
    except OSError:
        vm = []
    if len(vm) == 1:
        return vm[0]
    return Path(cwd)


def imposta_base(cwd) -> None:
    """Per gli hook: la cartella dell'attivita' ricavata dal `cwd` dello stdin (anche se il modello ha fatto `cd`
    dentro la pratica). Vale anche per i processi figli."""
    if cwd and not os.environ.get("STUDIO_SESSIONE_BASE"):
        os.environ["STUDIO_SESSIONE_BASE"] = str(_base_da_cwd(str(cwd)))


def _entrypoint_remoto() -> bool:
    return "remote_cowork" in (os.environ.get("CLAUDE_CODE_ENTRYPOINT") or "").lower()


def modalita_cowork() -> str:
    """'remoto': Cowork nel cloud, hook e bash sulla STESSA macchina Linux (CLAUDE_CODE_ENTRYPOINT=remote_cowork;
    in bash $CLAUDE_PLUGIN_ROOT e' vuota ma il percorso del plugin e' lo stesso degli hook; niente sopravvive
    fra un'attivita' e l'altra; SentenzeWeb non risponde, normattiva a singhiozzo — diagnostica del 26/09/2026).
    'locale': Cowork sul computer, hook sull'host e bash nella VM (/sessions/<x>/mnt). '' fuori da Cowork."""
    if _entrypoint_remoto():
        return "remoto"
    b = str(base_sessione())
    if b.startswith("/sessions/") or "local-agent-mode-sessions" in b:
        return "locale"
    return ""


def is_cowork() -> bool:
    return bool(modalita_cowork())


def stato_root() -> Path:
    """Radice dello stato di SESSIONE (v0.30): `<cartella dell'attivita'>/.studio-sessione`.

    Pratica corrente, chiave delle ricevute, autorizzazioni, telemetria, ledger, cache delle fonti, corpus
    sincronizzato: tutto cio' che hook e script devono condividere, e che deve morire con l'attivita'
    (decisione del 25/09/2026: una pratica si apre e si chiude nella stessa attivita' Cowork).
    $STUDIO_STATO_ROOT resta l'override esplicito (test)."""
    env = os.environ.get("STUDIO_STATO_ROOT")
    if env:
        return Path(env)
    return base_sessione() / SESSIONE


def stato_root_persistente() -> Path:
    """La conoscenza che deve sopravvivere alle sessioni (corpus vivo, stato della sentinella dei
    modelli, calibrazione degli esiti): la vecchia cascata. $STUDIO_STATO_PERSISTENTE per i test."""
    env = os.environ.get("STUDIO_STATO_PERSISTENTE") or os.environ.get("STUDIO_STATO_ROOT")
    if env:
        return Path(env)
    fratello = ROOT.parent / NOME_STATO
    if fratello.exists() or _scrivibile(fratello):
        return fratello
    return Path.home() / NOME_STATO


def rel_base(p) -> str:
    """Percorso RELATIVO alla cartella dell'attivita' se ci sta dentro (valido dall'host e dalla VM), altrimenti
    assoluto. Anche un percorso VM /sessions/<x>/mnt/outputs/... diventa relativo."""
    import re
    s = str(p)
    m = re.match(r"^/sessions/[^/]+/mnt/outputs/(.+)$", s)
    if m:
        return m.group(1)
    try:
        return Path(s).resolve().relative_to(base_sessione().resolve()).as_posix()
    except (ValueError, OSError):
        return s


def da_base(s) -> Path:
    """Inverso di rel_base: relativo → sotto la cartella dell'attivita'; percorso VM → mappato sulla base locale."""
    import re
    s = str(s or "")
    m = re.match(r"^/sessions/[^/]+/mnt/outputs/(.+)$", s)
    if m:
        return base_sessione() / m.group(1)
    p = Path(s)
    return p if p.is_absolute() else base_sessione() / p


if __name__ == "__main__":
    print("project_root:", project_root())
    print("skills dir  :", claude_skills_dir())
    print("wiki        :", WIKI)
    print("base attivita:", base_sessione())
    print("stato_root  :", stato_root(), "(sessione)")
    print("persistente :", stato_root_persistente())
