#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LE SENTINELLE NEL REPO PUBBLICO DEL CORPUS (v0.36): manifest, verifica, strumenti, semi, workflow.

Accanto al corpus normativo (manifest.json, workflow «corpus settimanale», «lavoro», «contributi»: strumenti v3 che qui NON
si toccano), il repo pubblico ospita le aree delle sentinelle automatiche (`aree.py`): dati periodici, riforme della
watchlist, successioni, modelli d'atto. Hanno un manifest proprio, `wiki-studio/sentinelle/manifest.json`: il client di
un plugin che non lo conosce semplicemente non lo legge.

  python3 scripts/sentinelle_pubblica.py --manifest [--radice R]      manifest delle aree dal disco
  python3 scripts/sentinelle_pubblica.py --verifica [--radice R]      sha, percorsi ammessi, nomi vietati, dati personali
  python3 scripts/sentinelle_pubblica.py --aggiungi AREA [--radice R] git add dei soli file di un'area (nel workflow)
  python3 scripts/sentinelle_pubblica.py --pubblica AREA [--radice R] commit, rebase, stato e manifest, verifica, push
  python3 scripts/sentinelle_pubblica.py --scansiona                  nomi vietati e dati personali nei file del plugin
  python3 scripts/sentinelle_pubblica.py --aggiorna-strumenti CLONE   script, workflow e regole nel clone del repo
  python3 scripts/sentinelle_pubblica.py --carica-semi CLONE [--forza] primo caricamento dei dati delle aree nel clone
  python3 scripts/sentinelle_pubblica.py --sonda                      le fonti rispondono? (diagnosi della rete)

Le regole: niente nomi di studi professionali, di persone o di clienti (impronte `sentinelle_base.VIETATI_SHA` e nome del plugin);
niente dati personali; gli strumenti v3 del corpus non si sovrascrivono mai; i file dell'Action non si riportano indietro
(il primo caricamento non sovrascrive cio' che l'Action ha gia' scritto, salvo --forza).
Solo stdlib, Python 3.9.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aree  # noqa: E402
import sentinelle_base as sb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 1
VERSIONE_SENTINELLE = 1
STRUMENTI_SENTINELLE = (
    "aree.py", "sentinelle_base.py", "sentinelle_prove.py", "sentinelle_dati.py", "sentinelle_normativa.py",
    "sentinelle_successioni.py", "sentinelle_modelli.py", "sentinelle_giro.py", "sentinelle_pubblica.py",
    "sentinella_modelli.py", "storico.py", "fonti_fetch.py", "freshness.py", "tassi.py", "soglia_usura.py",
    "uffici_competenza.py",
)
#: le funzioni dei moduli v3 del repo da cui dipendono gli strumenti delle sentinelle (si controlla che ci siano)
DIPENDENZE_V3 = {
    "paths.py": ("ROOT", "WIKI", "stato_root", "stato_root_persistente"),
    "corpus.py": ("risolvi", "patch_json", "_agg"),
    "codice_locale.py": ("articolo",),
    "corpus_diff.py": ("drift_report_sezione",),
    "corpus_pubblica.py": ("numeri_gu", "_get_testo", "_testo_html"),
}
FONTI_SONDA = {
    "Gazzetta Ufficiale": "https://www.gazzettaufficiale.it/30giorni/serie_generale",
    "MEF (decreti usura)": "https://www.dt.mef.gov.it/it/attivita_istituzionali/sistema_bancario_finanziario/anti_usura/categorie_creditizie/",
    "BCE Data Portal": "https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?format=csvdata&lastNObservations=1",
    "Geo Network (DEAS)": "https://www.geonetwork.it/supporto/deas-ii-pro/aggiornamenti",
    "normattiva": "https://www.normattiva.it/",
}


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 16), b""):
            h.update(blocco)
    return h.hexdigest()


def file_delle_aree(radice: Path) -> list:
    """[(rel, area, proprietario)] dei file presenti sotto la radice che appartengono a un'area."""
    radice = Path(radice)
    out = []
    for base in ("dati", "wiki-studio/normativa", "wiki-studio/modelli", "wiki-studio/parcella", "wiki-studio/sentinelle",
                 "skills/assistente-successioni/references"):
        d = radice / base
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_file():
                rel = p.relative_to(radice).as_posix()
                c = aree.classifica(rel)
                if c:
                    out.append((rel, c[0], c[1]))
    return out


def costruisci_manifest(radice: Path = ROOT) -> dict:
    radice = Path(radice)
    stato = sb.leggi_json(radice / aree.STATO, {}) or {}
    out = {"schema": SCHEMA, "generato_il": sb.adesso(), "versione_sentinelle": VERSIONE_SENTINELLE, "aree": {}}
    for rel, area, prop in file_delle_aree(radice):
        p = radice / rel
        out["aree"].setdefault(area, {"file": {}})["file"][rel] = {"sha256": _sha(p), "byte": p.stat().st_size, "proprietario": prop}
    for area, voce in (stato.get("aree") or {}).items():
        out["aree"].setdefault(area, {"file": {}})["stato"] = voce
    return out


def scrivi_manifest(radice: Path = ROOT) -> dict:
    m = costruisci_manifest(radice)
    sb.scrivi_json(Path(radice) / aree.MANIFEST, m)
    return m


def _vietati_extra() -> set:
    """Il nome del plugin che pubblica, parola per parola (oltre alle impronte fisse)."""
    try:
        nome = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name") or ""
    except (OSError, ValueError):
        nome = ""
    return {w for w in sb._parole(nome) if len(w) > 3 and w not in ("studio", "plugin", "legale")}


def controlla_testo(rel: str, testo: str) -> list:
    errori = []
    vietati = sb.nomi_vietati(testo, _vietati_extra())
    if vietati:
        errori.append(f"{rel}: {len(vietati)} nomi vietati")
    personali = sb.dati_personali(testo, telefoni_istituzionali=rel.endswith("uffici-competenza-successioni.json"))
    if personali:
        errori.append(f"{rel}: dati personali ({', '.join(sorted({t for t, _ in personali}))})")
    return errori


def verifica(radice: Path = ROOT) -> list:
    """Errori bloccanti delle aree (lista vuota = pubblicabile)."""
    radice = Path(radice)
    m = sb.leggi_json(radice / aree.MANIFEST)
    errori = []
    if not isinstance(m, dict) or m.get("schema") != SCHEMA:
        return ["manifest delle sentinelle assente o di schema ignoto"]
    elencati = set()
    for area, voce in (m.get("aree") or {}).items():
        for rel, info in (voce.get("file") or {}).items():
            elencati.add(rel)
            c = aree.classifica(rel)
            p = radice / rel
            if not c or c[0] != area:
                errori.append(f"{rel}: percorso non ammesso nell'area {area}")
            elif not p.is_file():
                errori.append(f"{rel}: file mancante")
            elif info.get("sha256") != _sha(p):
                errori.append(f"{rel}: sha diverso dal manifest")
    for rel, _area, _prop in file_delle_aree(radice):
        p = radice / rel
        if rel not in elencati:
            errori.append(f"{rel}: presente ma non nel manifest")
        testo = p.read_text(encoding="utf-8", errors="replace")
        if rel.endswith(".json"):
            try:
                json.loads(testo)
            except ValueError:
                errori.append(f"{rel}: JSON non valido")
        errori += controlla_testo(rel, testo)
    return errori


def aggiungi(radice: Path, area: str) -> list:
    """`git add` dei soli file di un'area (e dei suoi file di stato): mai un `git add -A` generico.

    Restano fuori lo stato comune (`stato.json`) e il manifest delle aree: tutti i job del giro partono dal commit del
    lancio e li scriverebbero insieme, quindi li riscrive `pubblica` sopra la versione appena scaricata."""
    radice = Path(radice)
    rels = [rel for st, rel in sb.toccati(radice) if (aree.classifica(rel) or ("", ""))[0] in (area, "stato")
            and rel not in (aree.STATO, aree.MANIFEST)]
    for rel in rels:
        sb.git(radice, "add", "-A", "--", rel)
    return rels


def _rimetti(radice: Path, rel: str) -> None:
    """Il file com'e' nell'ultimo commit (tolto, se nell'ultimo commit non c'e')."""
    if sb.git(radice, "cat-file", "-e", f"HEAD:{rel}").returncode == 0:
        sb.git(radice, "checkout", "--", rel)
    else:
        (Path(radice) / rel).unlink(missing_ok=True)


def pubblica(radice: Path, area: str, tentativi: int = 3, attesa: float = 15.0, remoto: str = "origin",
             ramo: str = "main") -> tuple:
    """Commit dei file dell'area, rebase sul ramo remoto, voce dell'area riapplicata sullo stato appena scaricato,
    manifest, verifica, push. Se il push non passa (un altro giro ha pubblicato intanto) si toglie il commit di stato e
    manifest e si riprova da capo. Ritorna (pubblicato?, messaggi)."""
    import time
    radice = Path(radice)
    p_stato = radice / aree.STATO
    voce = ((sb.leggi_json(p_stato, {}) or {}).get("aree") or {}).get(area)
    _rimetti(radice, aree.STATO)
    _rimetti(radice, aree.MANIFEST)
    msg = [f"aggiunti: {', '.join(aggiungi(radice, area)) or 'nessuno'}"]
    if sb.git(radice, "diff", "--cached", "--quiet").returncode != 0:
        sb.git(radice, "commit", "-q", "-m", f"sentinelle {area} {sb.oggi().isoformat()}")
    for n in range(1, tentativi + 1):
        if sb.git(radice, "pull", "-q", "--rebase", "--autostash", remoto, ramo).returncode != 0:
            sb.git(radice, "rebase", "--abort")
            msg.append(f"tentativo {n}: rebase non riuscito")
            time.sleep(attesa)
            continue
        base = sb.git(radice, "rev-parse", "HEAD").stdout.strip()
        if voce is not None:
            st = sb.leggi_json(p_stato, {}) or {}
            st.setdefault("_meta", {})["descrizione"] = ("Stato dell'ultimo giro delle sentinelle automatiche (GitHub Action "
                                                         "«sentinelle» del corpus pubblico), per area.")
            st["_meta"]["aggiornato_il"] = sb.adesso()
            st.setdefault("aree", {})[area] = voce
            sb.scrivi_json(p_stato, st)
        scrivi_manifest(radice)
        errori = verifica(radice)
        if errori:
            msg += [f"verifica: {e}" for e in errori]
            return False, msg
        sb.git(radice, "add", "--", aree.STATO, aree.MANIFEST)
        if sb.git(radice, "diff", "--cached", "--quiet").returncode != 0:
            sb.git(radice, "commit", "-q", "-m", f"sentinelle: stato e manifest {sb.oggi().isoformat()}")
        r = sb.git(radice, "push", "-q", remoto, f"HEAD:{ramo}")
        if r.returncode == 0:
            msg.append(f"pubblicato al tentativo {n}")
            return True, msg
        msg.append(f"tentativo {n}: push respinto ({(r.stderr or '').strip()[:120]})")
        sb.git(radice, "reset", "-q", "--hard", base)
        time.sleep(attesa)
    return False, msg


# ----------------------------------------------------------------------------------------------- strumenti e semi

def strumenti_v3(clone: Path) -> tuple:
    """I nomi della tupla STRUMENTI del corpus_pubblica.py del clone (letta senza importarla)."""
    p = Path(clone) / "scripts" / "corpus_pubblica.py"
    try:
        for n in ast.parse(p.read_text(encoding="utf-8")).body:
            if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "STRUMENTI" for t in n.targets):
                return tuple(ast.literal_eval(n.value))
    except (OSError, SyntaxError, ValueError):
        pass
    return ()


def _nomi_definiti(p: Path) -> set:
    try:
        albero = ast.parse(p.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    nomi = set()
    for n in albero.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            nomi.add(n.name)
        elif isinstance(n, ast.Assign):
            nomi |= {t.id for t in n.targets if isinstance(t, ast.Name)}
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            nomi.add(n.target.id)
    return nomi


def controlla_dipendenze(clone: Path) -> list:
    out = []
    for nome, servono in DIPENDENZE_V3.items():
        definiti = _nomi_definiti(Path(clone) / "scripts" / nome)
        mancano = [s for s in servono if s not in definiti]
        if mancano:
            out.append(f"{nome}: mancano {', '.join(mancano)}")
    return out


def versione_nel_repo(clone: Path) -> int:
    try:
        return int((Path(clone) / "scripts" / "VERSIONE_SENTINELLE").read_text(encoding="utf-8").strip() or 0)
    except (OSError, ValueError):
        return 0


def aggiorna_strumenti(clone: Path) -> list:
    """Copia gli strumenti delle sentinelle, il workflow, le regole per Claude e la nota pubblica nel clone."""
    clone = Path(clone)
    v3 = set(strumenti_v3(clone))
    conflitti = sorted(set(STRUMENTI_SENTINELLE) & v3)
    if conflitti:
        return [f"NON aggiornati: {', '.join(conflitti)} sono strumenti del corpus (v3) e non si sovrascrivono"]
    mancano = controlla_dipendenze(clone)
    if mancano:
        return ["NON aggiornati: il repo non ha le funzioni da cui dipendono le sentinelle — " + "; ".join(mancano)]
    if versione_nel_repo(clone) > VERSIONE_SENTINELLE:
        return [f"NON aggiornati: il repo ha le sentinelle alla versione {versione_nel_repo(clone)}, questo plugin la "
                f"{VERSIONE_SENTINELLE} (aggiorna il plugin)"]
    for nome in STRUMENTI_SENTINELLE:
        testo = (ROOT / "scripts" / nome).read_text(encoding="utf-8")
        errori = controlla_testo(nome, testo)
        if errori:
            return ["NON aggiornati: " + "; ".join(errori)]
    copiati = []
    (clone / "scripts").mkdir(parents=True, exist_ok=True)
    for nome in STRUMENTI_SENTINELLE:
        shutil.copy2(ROOT / "scripts" / nome, clone / "scripts" / nome)
        copiati.append(nome)
    (clone / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (clone / ".github" / "workflows" / "sentinelle.yml").write_text(workflow(), encoding="utf-8")
    (clone / ".github" / "claude").mkdir(parents=True, exist_ok=True)
    import sentinelle_regole as sr
    for area, testo in sr.REGOLE.items():
        (clone / ".github" / "claude" / f"sentinella-{area}.md").write_text(testo, encoding="utf-8")
    (clone / "SENTINELLE.md").write_text(sr.NOTA_PUBBLICA, encoding="utf-8")
    (clone / "scripts" / "VERSIONE_SENTINELLE").write_text(f"{VERSIONE_SENTINELLE}\n", encoding="utf-8")
    return copiati + ["sentinelle.yml", "regole per Claude", "SENTINELLE.md"]


def scansiona(radice: Path = ROOT) -> list:
    """Nomi vietati e dati personali nei file delle aree del plugin che si pubblicano (i drift-report locali no: li
    riscrive l'Action)."""
    out = []
    for rel, _area, _prop in file_delle_aree(radice):
        if rel == aree.MANIFEST or rel.startswith("wiki-studio/normativa/drift-reports/"):
            continue
        out += controlla_testo(rel, (Path(radice) / rel).read_text(encoding="utf-8", errors="replace"))
    return out


def carica_semi(clone: Path, forza: bool = False) -> dict:
    """Primo caricamento: i semi si copiano sempre (li possiede il plugin), i file dell'Action solo se il repo non li ha."""
    clone = Path(clone)
    errori = scansiona(ROOT)
    if errori:
        return {"esito": "RIFIUTATO", "motivo": "la scansione ha trovato nomi o dati da togliere", "errori": errori}
    copiati, tenuti = [], []
    for rel, _area, prop in file_delle_aree(ROOT):
        if rel == aree.MANIFEST or rel.startswith("wiki-studio/normativa/drift-reports/"):
            continue
        dest = clone / rel
        if prop == "action" and dest.exists() and not forza:
            tenuti.append(rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
        copiati.append(rel)
    scrivi_manifest(clone)
    return {"esito": "OK", "copiati": len(copiati), "tenuti": len(tenuti), "errori": verifica(clone)}


def sonda() -> dict:
    from urllib.request import Request, urlopen
    out = {}
    for nome, url in FONTI_SONDA.items():
        try:
            with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0 (corpus-normativo sentinelle)"}), timeout=25) as r:
                out[nome] = f"OK {r.status}"
        except Exception as e:  # noqa: BLE001
            out[nome] = f"KO {e.__class__.__name__}"
    return out


# ----------------------------------------------------------------------------------------------- workflow

_AREE_WF = ("dati", "normativa", "successioni", "modelli")
_TOOL_CLAUDE = {
    "dati": "Read,Glob,Grep,Write,WebFetch,WebSearch,Bash(python3 scripts/sentinelle_prove.py:*)",
    "normativa": "Read,Glob,Grep,Write,WebFetch,WebSearch,Bash(python3 scripts/sentinelle_prove.py:*),Bash(python3 scripts/codice_locale.py:*),Bash(python3 scripts/cassazione_indice.py:*)",
    "successioni": "Read,Glob,Grep,Write,WebFetch,WebSearch,Bash(python3 scripts/sentinelle_prove.py:*)",
    "modelli": "Read,Glob,Grep,Write,Edit,Bash(python3 scripts/codice_locale.py:*),Bash(python3 scripts/sentinella_modelli.py:*)",
}


def _job(area: str, prec: str) -> str:
    needs = f"    needs: [{prec}]\n" if prec else ""
    cond = (f"always() && (github.event_name != 'workflow_dispatch' || inputs.area == 'tutte' || inputs.area == '{area}')")
    return f"""
  {area}:
    runs-on: ubuntu-latest
    timeout-minutes: 240
{needs}    if: ${{{{ {cond} }}}}
    env:
      SCRIVE: ${{{{ contains(vars.SENTINELLE_AREE_SCRITTURA, '{area}') && !(github.event_name == 'workflow_dispatch' && inputs.a_secco) }}}}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
      - name: cartelle di lavoro fuori dal repo
        run: |
          echo "STUDIO_STATO_ROOT=$RUNNER_TEMP/stato" >> "$GITHUB_ENV"
          echo "STUDIO_CORPUS=$RUNNER_TEMP/corpus-vivo" >> "$GITHUB_ENV"
          echo "STUDIO_STATO_PERSISTENTE=$RUNNER_TEMP/persistente" >> "$GITHUB_ENV"
          echo "FONTI_CACHE=$RUNNER_TEMP/fonti-cache" >> "$GITHUB_ENV"
          sudo apt-get install -y -qq poppler-utils >/dev/null 2>&1 || echo "pdftotext non installato"
      - name: passi senza Claude
        id: det
        run: >-
          python3 scripts/sentinelle_giro.py --area {area} --fase deterministica --triage $RUNNER_TEMP/triage-{area}.json
          --github-output "$GITHUB_OUTPUT" --report $RUNNER_TEMP/sentinelle.md
      - name: passi senza Claude fissati (commit locale, cosi' il controllo vede solo le modifiche di Claude)
        run: |
          git config user.name "corpus-bot"
          git config user.email "corpus-bot@users.noreply.github.com"
          python3 scripts/sentinelle_pubblica.py --aggiungi {area}
          git commit -m "sentinelle {area}: passi senza Claude $(date -u +%F)" || echo "nessuna modifica"
      - name: Claude
        id: claude
        if: steps.det.outputs.claude == 'true'
        continue-on-error: true
        uses: anthropics/claude-code-action@v1
        env:
          CLAUDE_CODE_SUBAGENT_MODEL: opus
        with:
          claude_code_oauth_token: ${{{{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}}}
          github_token: ${{{{ secrets.GITHUB_TOKEN }}}}
          prompt: |
            Segui le istruzioni di .github/claude/sentinella-{area}.md.
            Il lavoro da fare e' in ${{{{ runner.temp }}}}/triage-{area}.json.
            Alla fine scrivi gli esiti in ${{{{ runner.temp }}}}/esiti-{area}.json.
          claude_args: >-
            --model opus
            --allowedTools "{_TOOL_CLAUDE[area]}"
      - name: controllo meccanico
        id: controllo
        if: always()
        run: >-
          python3 scripts/sentinelle_giro.py --area {area} --fase dopo-claude --triage $RUNNER_TEMP/triage-{area}.json
          --esiti $RUNNER_TEMP/esiti-{area}.json --claude-ok ${{{{ steps.claude.outcome != 'failure' }}}}
          --issue $RUNNER_TEMP/issue-{area}.md --github-output "$GITHUB_OUTPUT" --report $RUNNER_TEMP/sentinelle.md
      - name: cosa pubblicherebbe il giro (diff, per rivederlo)
        if: always()
        run: |
          git diff origin/main -- . > $RUNNER_TEMP/diff-{area}.patch || true
          git ls-files --others --exclude-standard | while read -r f; do git diff --no-index -- /dev/null "$f" || true; done >> $RUNNER_TEMP/diff-{area}.patch
      - name: pubblica
        if: always() && env.SCRIVE == 'true'
        run: python3 scripts/sentinelle_pubblica.py --pubblica {area}
      - name: segnalazione
        if: always() && env.SCRIVE == 'true' && steps.controllo.outputs.problemi != '0'
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh label create sentinelle --color FBCA04 --description "da ricontrollare (sentinelle automatiche)" --force || true
          gh label create memento --color 0E8A16 --description "schede del memento da rivedere" --force || true
          gh issue create --title "sentinelle {area}: da ricontrollare ($(date -u +%F))" --label sentinelle --body-file $RUNNER_TEMP/issue-{area}.md || true
      - name: rapporto
        if: always()
        run: |
          echo "scritture: ${{{{ env.SCRIVE }}}}" | tee -a $GITHUB_STEP_SUMMARY
          cat $RUNNER_TEMP/sentinelle.md 2>/dev/null | tee -a $GITHUB_STEP_SUMMARY || true
          cat $RUNNER_TEMP/issue-{area}.md 2>/dev/null | tee -a $GITHUB_STEP_SUMMARY || true
          git diff --stat origin/main -- . 2>/dev/null | tail -15 || true
          python3 -c "import json,sys; d=json.load(open(sys.argv[1])); r=([m for m in d if m.get('type')=='result'] or [dict()])[-1]; print('Claude:', r.get('num_turns'), 'passi.', str(r.get('result') or '')[:3000]); [print('::warning::permesso negato a Claude:', x.get('tool_name'), json.dumps(x.get('tool_input'), ensure_ascii=False)[:200]) for x in r.get('permission_denials') or []]" $RUNNER_TEMP/claude-execution-output.json 2>/dev/null || true
          grep -h -E "❌|⚠️|non verificat|respint|interrott" $RUNNER_TEMP/sentinelle.md $RUNNER_TEMP/issue-{area}.md 2>/dev/null | head -20 | sed 's/^- */::warning::/' || true
      - name: file del giro (triage, esiti, segnalazioni, diff)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sentinelle-{area}
          path: |
            ${{{{ runner.temp }}}}/triage-{area}.json
            ${{{{ runner.temp }}}}/triage-{area}.giro.json
            ${{{{ runner.temp }}}}/esiti-{area}.json
            ${{{{ runner.temp }}}}/issue-{area}.md
            ${{{{ runner.temp }}}}/sentinelle.md
            ${{{{ runner.temp }}}}/diff-{area}.patch
          retention-days: 14
          if-no-files-found: ignore
"""


def workflow() -> str:
    testa = """name: sentinelle

# Sentinelle automatiche: dati periodici, riforme della watchlist, successioni, modelli d'atto (vedi SENTINELLE.md).
# Scrivono nel repo solo le aree elencate nella variabile del repo SENTINELLE_AREE_SCRITTURA (es. "dati normativa"):
# finché un'area non c'è, il giro è «a secco» (rapporto nel riepilogo, nessun push, nessuna issue).

on:
  workflow_run:
    workflows: ["lavoro (CCNL, prassi, memento)"]
    types: [completed]
  schedule:
    - cron: "33 3 * * 3"          # mercoledì 05:33 ora italiana: riserva se la catena del lunedì non è partita
  workflow_dispatch:
    inputs:
      area:
        description: "area da far girare"
        type: choice
        options: ["tutte", "dati", "normativa", "successioni", "modelli"]
        default: "tutte"
      a_secco:
        description: "solo rapporto: nessuna scrittura nel repo, nessuna issue"
        type: boolean
        default: true

permissions:
  contents: write
  issues: write
  id-token: write

concurrency:
  group: corpus
  cancel-in-progress: false

env:
  PYTHONDONTWRITEBYTECODE: "1"

jobs:"""
    corpo, prec = "", ""
    for area in _AREE_WF:
        corpo += _job(area, prec)
        prec = area
    return testa + corpo


# ----------------------------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Le sentinelle nel repo pubblico del corpus: manifest, verifica, strumenti, semi.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--manifest", action="store_true")
    g.add_argument("--verifica", action="store_true")
    g.add_argument("--aggiungi", metavar="AREA")
    g.add_argument("--pubblica", metavar="AREA", help="commit, rebase, stato e manifest, verifica, push (nel workflow)")
    g.add_argument("--scansiona", action="store_true")
    g.add_argument("--aggiorna-strumenti", metavar="CLONE")
    g.add_argument("--carica-semi", metavar="CLONE")
    g.add_argument("--sonda", action="store_true")
    g.add_argument("--workflow", action="store_true", help="stampa il workflow sentinelle.yml")
    ap.add_argument("--radice", default=str(ROOT))
    ap.add_argument("--forza", action="store_true", help="con --carica-semi: sovrascrive anche i file dell'Action")
    a = ap.parse_args(argv)
    radice = Path(a.radice)
    if a.manifest:
        m = scrivi_manifest(radice)
        print(f"manifest delle sentinelle: {sum(len(v.get('file') or {}) for v in m['aree'].values())} file in {len(m['aree'])} aree")
        return 0
    if a.verifica:
        errori = verifica(radice)
        for e in errori:
            print(f"  ✗ {e}")
        print("verifica delle sentinelle: OK" if not errori else f"verifica delle sentinelle: {len(errori)} errori")
        return 1 if errori else 0
    if a.aggiungi:
        print("aggiunti: " + (", ".join(aggiungi(radice, a.aggiungi)) or "nessuno"))
        return 0
    if a.pubblica:
        ok, msg = pubblica(radice, a.pubblica)
        print("\n".join(msg))
        return 0 if ok else 1
    if a.scansiona:
        errori = scansiona(radice)
        for e in errori:
            print(f"  ✗ {e}")
        print("scansione: pulita" if not errori else f"scansione: {len(errori)} file da correggere")
        return 1 if errori else 0
    if a.aggiorna_strumenti:
        r = aggiorna_strumenti(Path(a.aggiorna_strumenti))
        print("\n".join(r))
        return 1 if r and r[0].startswith("NON") else 0
    if a.carica_semi:
        r = carica_semi(Path(a.carica_semi), forza=a.forza)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["esito"] == "OK" and not r.get("errori") else 1
    if a.sonda:
        for k, v in sonda().items():
            print(f"{k:22} {v}")
        return 0
    if a.workflow:
        print(workflow())
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
