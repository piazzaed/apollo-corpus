#!/usr/bin/env python3
"""Ufficio AdE competente per la dichiarazione di successione — tabella LOCALE datata (solo stdlib).

PERCHE'
-------
Nella pratica Properzi (16/9/2026) l'ufficio competente è costato 15 chiamate al browser:
le pagine AdE rispondono 403 a WebFetch dalla VM di Cowork ma non al browser, e il dato
non va nemmeno nel `.suc` — serve solo in DEAS e nella Scheda. È un dato tabellare, stabile
per anni (l'ultima riorganizzazione risale al 15/6/2019): va in una tabella locale con la
data di verifica, letta in millisecondi, rinfrescata on-demand con `--aggiorna`.

REGOLA (art. 6 D.Lgs. 346/1990, testo locale in wiki-studio/normativa/testi/tus.md)
------------------------------------------------------------------------------------
L'ufficio competente è quello nella cui circoscrizione era l'ULTIMA RESIDENZA del de cuius;
se il de cuius era residente all'estero, l'ufficio nella cui circoscrizione era l'ultima
residenza italiana; se anche questa è ignota, l'ufficio di Roma competente (art. 6 c. 1-2).
Per la provincia di Torino, dal 15/6/2019, le successioni si lavorano in DUE soli uffici
(UT «Atti pubblici, successioni e rimborsi IVA»): TT2 per il distretto della Direzione
Provinciale I, TT3 per quello della Direzione Provinciale II. La città di Torino è divisa
per CIRCOSCRIZIONE amministrativa (1-10): senza la circoscrizione, per Torino la risposta
è «TT2 oppure TT3» e la domanda per il cliente è l'indirizzo esatto.

FONTI (lette il 18/9/2026)
--------------------------
* pagine AdE «Uffici» delle Direzioni Provinciali I (T7D) e II (T7F) di Torino e dei loro
  Uffici Territoriali (campo «Competenza territoriale»);
* comunicazioni DP I (corso Bolzano 30, codice TT2) e DP II (via Paolo Veronese 199/A,
  codice TT3) del 28/5/2019 sull'operatività degli UT APSRI dal 15/6/2019.

CLI
---
  python3 scripts/uffici_competenza.py --comune "Moncalieri"
  python3 scripts/uffici_competenza.py --comune Torino --circoscrizione 4 [--json]
  python3 scripts/uffici_competenza.py --stato
  python3 scripts/uffici_competenza.py --aggiorna [--nel-repo]     # rilegge le pagine AdE
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import unicodedata
from html import unescape
from pathlib import Path

if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, stato_root  # noqa: E402

#: v0.53: la tabella NAZIONALE ha un file suo. Quello di sola Torino resta com'era per i plugin gia' installati (fino alla
#: 0.52 leggono solo quel formato: la tabella nazionale con lo stesso nome li romperebbe al primo sync); qui e' un ripiego.
SEED = ROOT / "skills/assistente-successioni/references/uffici-italia-successioni.json"
NOME_FILE = SEED.name
SEED_TORINO = ROOT / "skills/assistente-successioni/references/uffici-competenza-successioni.json"

#: Oltre questa età la tabella risponde ancora, ma dichiara che va riverificata (--aggiorna).
VITA_UTILE_GIORNI = 365

_BASE = "https://www.agenziaentrate.gov.it/portale/uffici12/-/uffici/uffici_INSTANCE_mi0d0mGReCpq/"

#: Uffici che lavorano le successioni (UT APSRI) e Uffici Territoriali del loro distretto.
#: I codici sono quelli del tracciato SUC13 (`uffici-suc13.md`) e delle pagine AdE.
DISTRETTI = {
    "TT2": {"direzione": "Direzione Provinciale I di Torino", "codice_dp": "T7D",
            "territoriali": ["TTK", "TTM", "TS5", "TTB"]},
    "TT3": {"direzione": "Direzione Provinciale II di Torino", "codice_dp": "T7F",
            "territoriali": ["TTL", "TTQ", "TST", "TSU", "TSZ", "TS4", "TTD", "TTJ"]},
}

REGOLA = ("art. 6 D.Lgs. 346/1990: ufficio nella cui circoscrizione era l'ultima residenza del "
          "de cuius; se residente all'estero, l'ultima residenza italiana; se ignota, l'ufficio "
          "di Roma competente. Le successioni della provincia di Torino si lavorano, dal "
          "15/6/2019, negli UT «Atti pubblici, successioni e rimborsi IVA»: TT2 (DP I) e TT3 (DP II).")


# ------------------------------------------------------------------ normalizzazione


try:  # v0.53: la corsia successioni si misura da sola (telemetria best-effort, mai un dato personale)
    from telemetria import fase_successione as _fase, nota_fase as _nota, nome_pratica as _nome_pratica
except Exception:  # pragma: no cover — la telemetria non deve mai impedire lo script
    def _fase(_nome):
        return lambda f: f

    def _nota(**_k):
        pass

    def _nome_pratica(_p):
        return ""

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.upper().replace("’", "'").replace("`", "'")
    s = re.sub(r"[^A-Z0-9']+", " ", s).strip()
    # «CIRIE'» e «CIRIE» devono coincidere: gli apostrofi finali sono grafie, non nomi
    return re.sub(r"\s*'\s*", "'", s).rstrip("'")


# ------------------------------------------------------------------ tabella

def _percorsi() -> list[Path]:
    """Refresh runtime, copia aggiornata dalle sentinelle automatiche (v0.36), seed del bundle: vince la piu' fresca."""
    out = [stato_root() / "successioni" / NOME_FILE]
    try:
        import aree as _ar
        for nome in (NOME_FILE, SEED_TORINO.name):
            s = _ar.file_sincronizzato("skills/assistente-successioni/references/" + nome)
            if s is not None:
                out.append(s)
    except Exception:
        pass
    return out + [SEED, SEED_TORINO]


def carica() -> dict | None:
    """La tabella più fresca fra refresh runtime e seed del bundle."""
    migliore = None
    for p in _percorsi():
        if not p.exists():
            continue
        try:
            dati = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        # v0.53: la tabella NAZIONALE (versione 2) vince sempre su quella della sola Torino, anche se piu' vecchia
        data = (int((dati.get("_meta") or {}).get("versione") or 1), str((dati.get("_meta") or {}).get("verificato_il") or ""))
        if migliore is None or data > migliore[0]:
            migliore = (data, dati, p)
    if migliore is None:
        return None
    dati = migliore[1]
    dati["_meta"]["_file"] = str(migliore[2])
    return dati


def eta_giorni(dati: dict) -> int | None:
    try:
        d = _dt.date.fromisoformat(dati["_meta"]["verificato_il"])
    except (KeyError, ValueError):
        return None
    return (_dt.date.today() - d).days


def _ufficio_v2(dati: dict, codice: str) -> dict:
    u = dict((dati.get("uffici") or {}).get(codice) or {})
    u.setdefault("codice", codice)
    if not u.get("nome"):
        try:
            import uffici_italia as ui
            u["nome"] = ui.codici_vigenti().get(codice, "")
        except Exception:
            pass
    for k in ("indirizzo", "pec", "email", "telefono"):
        u.setdefault(k, "")
    return u


def cerca_v2(comune: str, circoscrizione=None, dati: dict = None, provincia: str = "") -> dict:
    """v0.53 — tabella nazionale (uffici_italia.py): comune per codice catastale, citta' divise, omonimi per provincia."""
    import comuni_istat as ci
    base = {"comune": str(comune or "").upper(), "verificato_il": dati["_meta"].get("verificato_il"),
            "regola": dati["_meta"].get("regola", REGOLA)}
    eta = eta_giorni(dati)
    if eta is not None and eta > VITA_UTILE_GIORNI:
        base["avviso"] = f"tabella verificata il {dati['_meta'].get('verificato_il')} ({eta} giorni fa): riverificare"
    s = str(comune or "").strip()
    if re.fullmatch(r"[A-Za-z]\d{3}", s):
        candidati = [ci.da_codice(s.upper())] if ci.da_codice(s.upper()) else []
    else:
        candidati = ci.da_nome(s, provincia)
        sigla = str(provincia or "").strip().upper()
        if sigla and candidati and all(c["provincia"] != sigla for c in candidati):
            # da_nome, senza riscontro, ripiega su tutti gli omonimi (serve alla raccolta delle pagine AdE): qui una provincia
            # DICHIARATA che non torna e' un dato da verificare, non un comune di un'altra provincia
            return {**base, "verdetto": "NON_IN_TABELLA",
                    "motivo": f"nessun comune «{s}» in provincia {sigla} (esiste in: "
                              + ", ".join(sorted({c['provincia'] for c in candidati})) + "): verificare nome e provincia",
                    "domanda_cliente": f"Il comune dell'ultima residenza è proprio «{s}» ({sigla})? Ci indichi il nome completo."}
    if not candidati:
        sop = ci.soppresso(s, provincia)
        if sop:
            esito = cerca_v2(sop["confluito_in"], circoscrizione, dati, sop["provincia"])
            esito["nota"] = f"{s} è soppresso ({sop['data']}): confluito in {sop['confluito_in']}"
            return esito
        return {**base, "verdetto": "NON_IN_TABELLA", "motivo": f"«{s}» non è un comune italiano vigente né soppresso noto"}
    if len(candidati) > 1:
        return {**base, "verdetto": "AMBIGUO", "omonimi": candidati,
                "domanda_cliente": f"In quale provincia si trova il comune di {s} dell'ultima residenza? (esistono omonimi: "
                                   + ", ".join(f"{c['nome']} ({c['provincia']})" for c in candidati) + ")"}
    c = candidati[0]
    base.update({"comune": c["nome"].upper(), "provincia": c["provincia"], "codice_catastale": c["codice"]})
    voce = (dati.get("comuni") or {}).get(c["codice"])
    if not voce:
        return {**base, "verdetto": "NON_IN_TABELLA",
                "motivo": f"{c['nome']} ({c['provincia']}): la pagina AdE dell'ufficio non lo elenca — verificare su «Trova "
                          "l'ufficio» del sito AdE e chiedere conferma all'ufficio della direzione provinciale"}
    divisa = (dati.get("citta_divise") or {}).get(c["codice"])
    if divisa and divisa.get("parti"):
        parti = divisa["parti"]
        uffici = sorted({p["ufficio"] for p in parti.values()} | {voce["ufficio"]})
        if circoscrizione not in (None, ""):
            chiave = str(circoscrizione).strip().upper()
            chiave = str(int(chiave)) if chiave.isdigit() else chiave
            parte = parti.get(chiave)
            if parte:
                return {**base, "verdetto": "OK", "circoscrizione": chiave, "ufficio": _ufficio_v2(dati, parte["ufficio"]),
                        "ufficio_territoriale": parte.get("ufficio_territoriale"), "regola_ufficio": voce.get("regola")}
            return {**base, "verdetto": "NON_IN_TABELLA",
                    "motivo": f"{divisa['tipo']} {circoscrizione!r} non prevista per {c['nome']} ({', '.join(sorted(parti))})"}
        if len(uffici) > 1:
            return {**base, "verdetto": "AMBIGUO", "uffici_possibili": [_ufficio_v2(dati, u) for u in uffici],
                    "per_circoscrizione": {k: p["ufficio"] for k, p in parti.items()},
                    "domanda_cliente": (f"Qual era l'indirizzo esatto (via e numero civico) dell'ultima residenza del defunto a "
                                        f"{c['nome']}? La città è divisa fra più uffici dell'Agenzia delle Entrate "
                                        f"({divisa['tipo']}): serve per individuare quello competente."),
                    "come_trovare_circoscrizione": dati["_meta"].get("torino_circoscrizioni_come", "")}
    return {**base, "verdetto": "OK", "ufficio": _ufficio_v2(dati, voce["ufficio"]),
            "ufficio_territoriale": voce.get("ufficio_territoriale"), "regola_ufficio": voce.get("regola")}


def cerca(comune: str, circoscrizione=None, dati: dict | None = None, provincia: str = "") -> dict:
    """Esito per un comune (e, per Torino, una circoscrizione).

    Ritorna sempre un dict con `verdetto` in {OK, AMBIGUO, NON_IN_TABELLA, TABELLA_ASSENTE}
    e, con OK, l'ufficio completo (codice, nome, indirizzo, PEC, email, telefono).
    Mai un'inferenza: un comune fuori tabella è NON_IN_TABELLA, non «probabilmente TT2».
    """
    dati = dati or carica()
    if not dati:
        return {"verdetto": "TABELLA_ASSENTE",
                "motivo": f"tabella {NOME_FILE} non trovata: eseguire --aggiorna"}
    if (dati.get("_meta") or {}).get("versione") == 2:
        return cerca_v2(comune, circoscrizione, dati, provincia)
    eta = eta_giorni(dati)
    avviso = (f"tabella verificata il {dati['_meta'].get('verificato_il')} ({eta} giorni fa, oltre la vita utile "
              f"di {VITA_UTILE_GIORNI}): riverificare con --aggiorna") if eta is not None and eta > VITA_UTILE_GIORNI else ""
    chiave = _norm(comune)
    base = {"comune": chiave, "verificato_il": dati["_meta"].get("verificato_il"),
            "regola": dati["_meta"].get("regola", REGOLA)}
    if avviso:
        base["avviso"] = avviso

    if chiave == "TORINO":
        circ = dati.get("torino_circoscrizioni") or {}
        if circoscrizione in (None, ""):
            uffici = sorted(set(circ.values()))
            return {**base, "verdetto": "AMBIGUO",
                    "uffici_possibili": [dati["uffici"][u] for u in uffici],
                    "per_circoscrizione": circ,
                    "domanda_cliente": ("Qual era l'indirizzo esatto (via e numero civico) dell'ultima residenza "
                                        "del defunto a Torino? Serve per individuare la circoscrizione e quindi "
                                        "l'ufficio dell'Agenzia delle Entrate competente."),
                    "come_trovare_circoscrizione": dati["_meta"].get("torino_circoscrizioni_come")}
        codice = circ.get(str(int(str(circoscrizione).strip())))
        if not codice:
            return {**base, "verdetto": "NON_IN_TABELLA",
                    "motivo": f"circoscrizione {circoscrizione!r} non prevista (Torino ha le circoscrizioni 1-10)"}
        return {**base, "verdetto": "OK", "circoscrizione": str(int(str(circoscrizione))),
                "ufficio": dati["uffici"][codice]}

    codice = (dati.get("comuni") or {}).get(chiave)
    if not codice:
        return {**base, "verdetto": "NON_IN_TABELLA",
                "motivo": (f"{comune!r} non è fra i comuni della provincia di Torino censiti: per un altro "
                           "distretto cercare l'ufficio sul sito AdE («Trova l'ufficio», competenza per "
                           "l'ultima residenza) e aggiungerlo alla tabella con la data")}
    return {**base, "verdetto": "OK", "ufficio": dati["uffici"][codice],
            "ufficio_territoriale": (dati.get("comuni_ut") or {}).get(chiave)}


# ------------------------------------------------------------------ aggiornamento dalle pagine AdE

def _testo_pagina(url: str) -> str:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (corpus-normativo uffici_competenza)"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    t = unescape(re.sub(r"<[^>]+>", "\n", t))
    return re.sub(r"\n\s*\n+", "\n", t)


def _campo(t: str, etichetta: str) -> str:
    m = re.search(re.escape(etichetta) + r":\s*\n\s*([^\n]+)", t)
    return m.group(1).strip() if m else ""


def _scheda_ufficio(codice: str) -> dict:
    t = _testo_pagina(_BASE + f"dettagliouffT/{codice}/cr/901/iur/{codice}")
    titolo = re.search(r"\n(Direzione Provinciale I+ di TORINO - [^\n]+)\n", t)
    return {"codice": codice,
            "nome": (titolo.group(1).strip() if titolo else "").replace(" - ", " — ", 1),
            "indirizzo": _campo(t, "Indirizzo"), "telefono": _campo(t, "Telefono"),
            "email": _campo(t, "E-mail"), "pec": _campo(t, "PEC"),
            "orario": _campo(t, "Orario"),
            "competenza": _campo(t, "Competenza territoriale"),
            "url": _BASE + f"dettagliouffT/{codice}/cr/901/iur/{codice}"}


def aggiorna(dest: Path) -> dict:
    """Rilegge le pagine AdE e riscrive la tabella. Fallisce (SystemExit) se una pagina
    non porta la competenza: una tabella parziale è peggio di una vecchia."""
    oggi = _dt.date.today().isoformat()
    uffici, comuni, comuni_ut, ut, circ = {}, {}, {}, {}, {}
    for apsri, cfg in DISTRETTI.items():
        s = _scheda_ufficio(apsri)
        dp_t = _testo_pagina(_BASE + f"dettaglioufficio/{cfg['codice_dp']}")
        s["telefono"] = s["telefono"] or _campo(dp_t, "Telefono")
        s["direzione"] = cfg["direzione"]
        uffici[apsri] = {k: v for k, v in s.items() if k != "competenza"}
        for c in cfg["territoriali"]:
            u = _scheda_ufficio(c)
            if not u["competenza"]:
                raise SystemExit(f"[uffici_competenza] {c}: campo «Competenza territoriale» assente "
                                 "sulla pagina AdE — struttura cambiata, tabella NON riscritta")
            voci = [v.strip() for v in u["competenza"].split(",") if v.strip()]
            numeri_circ, nomi = [], []
            for v in voci:
                m = re.fullmatch(r"Circoscrizione\s+(\d+)", v)
                if m:
                    numeri_circ.append(m.group(1))
                elif re.fullmatch(r"\d+", v) and numeri_circ:
                    numeri_circ.append(v)
                else:
                    nomi.append(v)
            for n in numeri_circ:
                circ[n] = apsri
            for nome in nomi:
                if _norm(nome) == "TORINO":
                    continue            # «Torino» sta per le circoscrizioni elencate accanto
                comuni[_norm(nome)] = apsri
                comuni_ut[_norm(nome)] = c
            ut[c] = {"nome": u["nome"], "indirizzo": u["indirizzo"], "apsri": apsri,
                     "comuni": [_norm(n) for n in nomi if _norm(n) != "TORINO"],
                     "circoscrizioni_torino": numeri_circ, "url": u["url"]}
    if len(circ) != 10:
        raise SystemExit(f"[uffici_competenza] circoscrizioni di Torino lette: {sorted(circ)} (attese 10) — tabella NON riscritta")
    dati = {
        "_meta": {
            "verificato_il": oggi, "provincia": "TO", "regola": REGOLA,
            "fonti": ["pagine AdE «Uffici» delle Direzioni Provinciali I (T7D) e II (T7F) di Torino e dei "
                      "loro Uffici Territoriali (campo «Competenza territoriale»)",
                      "comunicazioni DP I e DP II di Torino del 28/5/2019 (operatività UT APSRI dal 15/6/2019)"],
            "torino_circoscrizioni_come": ("dall'indirizzo: servizio del Comune di Torino «Trova la circoscrizione» "
                                           "(www.comune.torino.it/circoscrizioni) o dal certificato di residenza "
                                           "storico, che riporta la circoscrizione"),
            "residenza_estera": ("de cuius residente all'estero: competente l'ufficio dell'ultima residenza in "
                                 "Italia; se ignota, l'ufficio di Roma individuato dall'AdE (art. 6 c. 2 TUS): "
                                 "verificare sul sito AdE, non è in questa tabella"),
            "vita_utile_giorni": VITA_UTILE_GIORNI,
        },
        "uffici": uffici,
        "uffici_territoriali": ut,
        "torino_circoscrizioni": {k: circ[k] for k in sorted(circ, key=int)},
        "comuni": dict(sorted(comuni.items())),
        "comuni_ut": dict(sorted(comuni_ut.items())),
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return dati


# ------------------------------------------------------------------ CLI

def _stampa(esito: dict) -> None:
    v = esito["verdetto"]
    if v == "OK":
        u = esito["ufficio"]
        print(f"OK {esito['comune']}" + (f" (circoscrizione {esito['circoscrizione']})" if esito.get("circoscrizione") else ""))
        print(f"UFFICIO: {u['codice']} — {u['nome']}")
        print(f"INDIRIZZO: {u['indirizzo']}")
        print(f"PEC: {u['pec']}   EMAIL: {u['email']}   TEL: {u.get('telefono', '')}")
        if esito.get("ufficio_territoriale"):
            print(f"UT DI ZONA (non per le successioni): {esito['ufficio_territoriale']}")
    elif v == "AMBIGUO":
        # v0.53: due casi — comuni omonimi (serve la provincia) e citta' divise fra piu' uffici (serve l'indirizzo)
        if esito.get("omonimi"):
            print(f"AMBIGUO {esito['comune']}: comuni omonimi, serve la provincia (--provincia)")
            for c in esito["omonimi"]:
                print(f"  {c['nome']} ({c['provincia']}) · codice catastale {c['codice']}")
        else:
            print(f"AMBIGUO {esito['comune']}: città divisa fra più uffici, serve la parte (--circoscrizione)")
            for n, cod in (esito.get("per_circoscrizione") or {}).items():
                print(f"  {n:>12} → {cod}")
        print(f"DOMANDA PER IL CLIENTE: {esito['domanda_cliente']}")
        if esito.get("come_trovare_circoscrizione"):
            print(f"COME: {esito['come_trovare_circoscrizione']}")
    else:
        print(f"{v} {esito.get('motivo', '')}")
    print(f"VERIFICATO IL: {esito.get('verificato_il', 'n/d')}")
    if esito.get("avviso"):
        print(f"AVVISO: {esito['avviso']}")


@_fase("uffici")
def main() -> int:
    ap = argparse.ArgumentParser(description="Ufficio AdE competente per la successione (tabella locale datata)")
    ap.add_argument("--comune", help="comune dell'ultima residenza del de cuius")
    ap.add_argument("--provincia", default="", help="sigla della provincia (distingue i comuni omonimi)")
    ap.add_argument("--circoscrizione", help="città divise (Torino 1-10, municipi, zone, quartieri)")
    ap.add_argument("--aggiorna", action="store_true",
                    help="v0.53: ricostruisce la tabella NAZIONALE (uffici_italia.py --aggiorna) — mai quella di sola Torino")
    ap.add_argument("--nel-repo", action="store_true", help="con --aggiorna: scrive il seed nel pacchetto")
    ap.add_argument("--stato", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.aggiorna:
        # v0.53: lo scraper di sola Torino (`aggiorna`, tabella versione 1) riscriverebbe la tabella nazionale con 300 comuni:
        # si passa sempre dal costruttore nazionale, che non sostituisce una tabella che non regge il confronto
        import subprocess
        dest = SEED if a.nel_repo else stato_root() / "successioni" / NOME_FILE
        dest.parent.mkdir(parents=True, exist_ok=True)
        return subprocess.run([sys.executable, str(Path(__file__).with_name("uffici_italia.py")), "--aggiorna",
                               "--out", str(dest)]).returncode

    if a.comune:
        esito = cerca(a.comune, a.circoscrizione, provincia=a.provincia)
        if a.json:
            print(json.dumps(esito, ensure_ascii=False, indent=1))
        else:
            _stampa(esito)
        return 0 if esito["verdetto"] in ("OK", "AMBIGUO") else 1

    dati = carica()
    if not dati:
        print(f"ASSENTE  tabella {NOME_FILE} non trovata (python3 scripts/uffici_competenza.py --aggiorna --nel-repo)")
        return 1
    eta = eta_giorni(dati)
    print(f"{'FRESCA' if eta is not None and eta <= VITA_UTILE_GIORNI else 'DA RIVERIFICARE'}  "
          f"verificata il {dati['_meta'].get('verificato_il')} ({eta} gg) · {len(dati.get('comuni', {}))} comuni · "
          f"uffici {', '.join(dati.get('uffici', {}))} · {dati['_meta'].get('_file')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
