#!/usr/bin/env python3
"""UFFICI COMPETENTI PER LE SUCCESSIONI IN TUTTA ITALIA (v0.53) — dalle pagine «Uffici» dell'AdE (solo stdlib).

PERCHE'
-------
L'ufficio competente e' quello dell'ULTIMA RESIDENZA del de cuius (art. 6 TUS): ogni Scheda e ogni consegna lo devono
dire con la SIGLA giusta. Fino alla v0.52 la tabella copriva la sola provincia di Torino; fuori, l'ufficio si cercava a
mano (15 chiamate al browser nella pratica del 16/9/2026). Qui si costruisce la tabella nazionale:
  1. i CODICI VIGENTI degli uffici vengono dal tracciato SUC13 (`uffici-suc13.md`, generato dagli XSD AdE): sono gli unici
     che il modulo di controllo accetta;
  2. per ognuno la pagina AdE `dettaglioufficio/<codice>`: direzione provinciale, indirizzo, telefono, email, PEC e il
     campo «Competenza territoriale» (i comuni);
  3. dove la Direzione provinciale ha l'Ufficio territoriale «Atti pubblici, successioni e rimborsi IVA» (38 nel tracciato:
     Torino I e II, Bari, Bologna, Firenze, Genova…), le successioni di TUTTI i comuni della direzione vanno a quello; negli
     altri casi all'ufficio territoriale del comune;
  4. ogni comune si lega al suo codice catastale con la tabella ISTAT (`comuni_istat.py`): gli omonimi non si confondono;
     le citta' divise (circoscrizioni di Torino, municipi) restano divise, e senza la parte la risposta e' «AMBIGUO».
Quello che una pagina non dice resta «non mappato» (mai un ufficio inventato): la Scheda lo dice e la domanda va al
cliente o al sito AdE. Il controllo strutturale (pochi comuni, un codice non vigente, un campo che si svuota) lascia la
tabella vecchia: una tabella parziale e' peggio di una vecchia.

Uso:
  python3 scripts/uffici_italia.py --raccogli [--cache DIR]       # scarica le pagine (≈ 400, qualche minuto) nella cache
  python3 scripts/uffici_italia.py --costruisci [--cache DIR] [--out FILE]   # tabella da cache (nessuna rete)
  python3 scripts/uffici_italia.py --aggiorna [--nel-repo]        # le due cose insieme (la sentinella, una volta al mese)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
UFFICI_SUC13 = ROOT / "skills" / "assistente-successioni" / "references" / "uffici-suc13.md"
TABELLA = ROOT / "skills" / "assistente-successioni" / "references" / "uffici-italia-successioni.json"   # v0.53: file suo
BASE = "https://www.agenziaentrate.gov.it/portale/uffici12/-/uffici/uffici_INSTANCE_mi0d0mGReCpq/"
#: sotto questa copertura la tabella nuova non sostituisce la vecchia
MIN_COMUNI_MAPPATI = 7000
_RX_APSRI = re.compile(r"atti pubblici,\s*successioni", re.I)
_RX_PARTE = re.compile(r"^(circoscrizione|municipio|municipi|quartiere|quartieri|zona|zone)\s+(.+)$", re.I)


def norm(s: str) -> str:
    import comuni_istat as ci
    return ci.norm(s)


def codici_vigenti() -> dict:
    """{codice: descrizione} degli uffici di registrazione VIGENTI nel tracciato (nessun «fino al»)."""
    t = UFFICI_SUC13.read_text(encoding="utf-8")
    i = t.index("## Uffici di registrazione")
    j = t.index("\n## ", i + 10)
    righe = re.findall(r"^\| `([A-Z0-9]+)` \| (.+?) \|$", t[i:j], re.M)
    return {c: d for c, d in righe if not re.search(r"fino al|\bal \d{2}/\d{2}/\d{4}", d)}


def apsri_per_direzione(vigenti: dict) -> dict:
    """{DIREZIONE PROVINCIALE … normalizzata: codice dell'ufficio successioni}."""
    out = {}
    for c, d in vigenti.items():
        if _RX_APSRI.search(d):
            m = re.match(r"(DIREZIONE PROVINCIALE .+?) Ufficio Territoriale", d, re.I)
            if m:
                out[norm(m.group(1))] = c
    return out


def _testo(raw: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    t = _html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return re.sub(r"\n\s*\n+", "\n", t)


def _campo(t: str, etichetta: str) -> str:
    m = re.search(re.escape(etichetta) + r":\s*\n\s*([^\n]+)", t)
    return m.group(1).strip() if m else ""


def analizza_pagina(raw: str, codice: str) -> dict:
    t = _testo(raw)
    cod = _campo(t, "Codice ufficio")
    titolo = re.search(r"\n((?:Direzione Provinciale|Direzione Regionale)[^\n]*?(?: - [^\n]+)?)\n\s*Direttore", t)
    regione = re.search(r"Direzioni Regionali e uffici Provinciali territorio\s*\n\s*([^\n]+)\n", t)
    orario = re.search(r"Orario di apertura:\s*\n(.*?)\n\s*(?:Avvisi|Informazioni utili)", t, re.S)
    dp_codici = sorted(set(re.findall(r"dettaglioufficio/(T[0-9A-Z]{2,3})\b", raw)))
    return {"codice": cod or "", "richiesto": codice, "titolo": titolo.group(1).strip() if titolo else "",
            "regione": regione.group(1).strip() if regione else "",
            "indirizzo": _campo(t, "Indirizzo"), "telefono": _campo(t, "Telefono"), "email": _campo(t, "E-mail"),
            "pec": _campo(t, "PEC"), "competenza": _campo(t, "Competenza territoriale"),
            "orario": re.sub(r"\s+", " ", orario.group(1)).strip()[:300] if orario else "",
            "direzioni_viste": dp_codici, "url": BASE + f"dettaglioufficio/{codice}"}


def _scarica(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (studio; uffici successioni)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


LISTA_REGIONI = "https://www.agenziaentrate.gov.it/portale/lista-uffici"
SITO = "https://www.agenziaentrate.gov.it"
_RX_PREFISSO = re.compile(r"/portale/((?:[a-z\-]+/)?uffici\d*)/-/uffici/(uffici_INSTANCE_[A-Za-z0-9]+)/")
_RX_UT = re.compile(r"dettagliouffT/([A-Z0-9]{2,4})/cr/(\d+)/iur/")


def raccogli(cache: Path, pausa: float = 0.12) -> dict:
    """regioni (lista-uffici) → direzioni provinciali (dettaglioufficio/<DP>) → uffici territoriali (dettagliouffT/…):
    ogni pagina col prefisso della SUA regione (il portale ha una pagina «uffici» per regione). Riusa la cache."""
    cache.mkdir(parents=True, exist_ok=True)
    p = cache / "pagine.json"
    pagine = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    pagine = {k: v for k, v in pagine.items() if v.get("codice")}
    errori, regioni = [], []
    lista = _scarica(LISTA_REGIONI)
    percorsi = sorted(set(re.findall(r'href="(/portale/uffici\d+)"', lista)))
    try:   # le pagine delle Direzioni regionali portano anche le regioni che la lista non elenca (Trentino, Abruzzo…)
        siti = _scarica(SITO + "/portale/siti-web-regionali")
        percorsi += sorted(set(re.findall(r'href="(/portale/(?:dr-[a-z\-]+|alto-adige-itde|trentino[a-z\-]*))"', siti)))
    except Exception as e:  # noqa: BLE001
        errori.append(f"siti-web-regionali: {type(e).__name__}")
    visti_prefissi = set()
    for perc in percorsi:
        try:
            raw = _scarica(SITO + perc)
        except Exception as e:  # noqa: BLE001
            errori.append(f"{perc}: {type(e).__name__}")
            continue
        m = _RX_PREFISSO.search(raw)
        if not m:
            errori.append(f"{perc}: prefisso degli uffici non trovato")
            continue
        prefisso = f"{SITO}/portale/{m.group(1)}/-/uffici/{m.group(2)}/"
        direzioni = sorted(set(re.findall(r"dettaglioufficio/(T[0-9A-Z]{2,3})\b", raw)))
        if prefisso in visti_prefissi and all(dp in pagine for dp in direzioni):
            continue
        visti_prefissi.add(prefisso)
        regioni.append({"percorso": perc, "prefisso": prefisso, "direzioni": direzioni})
        for dp in direzioni:
            try:
                raw_dp = _scarica(prefisso + f"dettaglioufficio/{dp}")
            except Exception as e:  # noqa: BLE001
                errori.append(f"{dp}: {type(e).__name__}")
                continue
            info_dp = analizza_pagina(raw_dp, dp)
            info_dp["url"] = prefisso + f"dettaglioufficio/{dp}"
            info_dp["tipo"] = "direzione"
            pagine[dp] = info_dp
            for ut, cr in sorted(set(_RX_UT.findall(raw_dp))):
                if ut in pagine:
                    continue
                url = prefisso + f"dettagliouffT/{ut}/cr/{cr}/iur/{ut}"
                try:
                    info = analizza_pagina(_scarica(url), ut)
                except Exception as e:  # noqa: BLE001
                    errori.append(f"{ut}: {type(e).__name__}")
                    continue
                info["url"], info["tipo"], info["direzione_codice"] = url, "ufficio", dp
                pagine[ut] = info
                time.sleep(pausa)
            p.write_text(json.dumps(pagine, ensure_ascii=False), encoding="utf-8")
            time.sleep(pausa)
    (cache / "regioni.json").write_text(json.dumps(regioni, ensure_ascii=False, indent=1), encoding="utf-8")
    p.write_text(json.dumps(pagine, ensure_ascii=False), encoding="utf-8")
    return {"pagine": len(pagine), "regioni": len(regioni), "errori": errori}


_ABBREVIAZIONI = ((r"\bSS\b", "SANTI"), (r"\bS\b", "SAN"), (r"\bSTA\b", "SANTA"), (r"\bSANTO STINO\b", "SAN STINO"))
_TIPI_PARTE = {"circoscrizione": "circoscrizione", "municipio": "municipio", "municipi": "municipio", "quartiere": "quartiere",
               "quartieri": "quartiere", "zona": "zona", "zone": "zona"}


def risolvi_comune(nome: str, sigla: str) -> list:
    """Il comune di una voce della «Competenza territoriale». Con la provincia nota MAI un omonimo di un'altra provincia
    (Poggioreale quartiere di Napoli non e' Poggioreale TP); abbreviazioni («S.» = San) e nomi troncati dalla pagina
    («… di Castroz») si riconoscono solo se il prefisso e' unico nella provincia."""
    import comuni_istat as ci
    trovati = ci.da_nome(nome, sigla)
    if sigla:
        trovati = [x for x in trovati if x["provincia"] == sigla]
    if trovati:
        return trovati
    if not sigla:
        return []
    regione = next((v[3] for v in (ci.carica().get("comuni") or {}).values() if v[1] == sigla), "")
    stessa_regione = [x for x in ci.da_nome(nome) if regione and x.get("regione") == regione]
    if len(stessa_regione) == 1:                 # province ridisegnate (Sud Sardegna) o direzioni su piu' province
        return stessa_regione
    forma = ci.norm(nome)
    for rx, sost_ in _ABBREVIAZIONI:
        forma = re.sub(rx, sost_, forma)
    forma = ci.norm(forma)
    della_provincia = [(c, v) for c, v in (ci.carica().get("comuni") or {}).items() if v[1] == sigla]
    esatti = [c for c, v in della_provincia if ci.norm(v[0]) == forma]
    if not esatti and len(forma) >= 10:
        esatti = [c for c, v in della_provincia if ci.norm(v[0]).startswith(forma) or forma.startswith(ci.norm(v[0]) + " ")]
    if not esatti:                               # «Cortaccia Sulla Strada Vino» = «Cortaccia sulla Strada del Vino»
        parole = forma.split()
        esatti = [c for c, v in della_provincia if len(parole) >= 2 and all(w in ci.norm(v[0]).split() for w in parole)]
    return [ci.da_codice(c) for c in esatti] if len(esatti) == 1 else []


def _direzione_e_ufficio(titolo: str) -> tuple:
    if " - " not in titolo:
        return "", titolo
    a, b = titolo.split(" - ", 1)
    return a.strip(), b.strip()


def _provincia_della_direzione(direzione: str, comuni_ut: list) -> str:
    """La sigla della provincia: dal capoluogo nel nome della direzione, altrimenti dal primo comune riconosciuto."""
    import comuni_istat as ci
    m = re.search(r"\bdi\s+(.+)$", direzione, re.I)
    if m:
        nome = m.group(1).strip()
        trovati = ci.da_nome(nome)
        capoluoghi = [x for x in trovati if x]
        if len(capoluoghi) == 1:
            return capoluoghi[0]["provincia"]
        if norm(nome) in ("MONZA E BRIANZA",):
            return "MB"
        if "CUSIO" in norm(nome):
            return "VB"
    for nome in comuni_ut:
        trovati = ci.da_nome(nome)
        if len(trovati) == 1:
            return trovati[0]["provincia"]
    return ""


def costruisci(cache: Path) -> dict:
    import comuni_istat as ci
    pagine = json.loads((cache / "pagine.json").read_text(encoding="utf-8"))
    vigenti = codici_vigenti()
    apsri = apsri_per_direzione(vigenti)
    uffici, comuni, divise, non_risolti, senza_pagina = {}, {}, {}, [], []
    for c, pg in sorted(pagine.items()):
        if not pg.get("codice"):
            senza_pagina.append(c)
            continue
        if pg.get("tipo") == "direzione" and not pg.get("competenza"):
            continue                             # (la Valle d'Aosta pubblica i suoi uffici come direzione: con la competenza valgono)
        direzione, nome_uff = _direzione_e_ufficio(pg.get("titolo") or "")
        uffici[c] = {"codice": c, "nome": nome_uff or vigenti.get(c, ""), "direzione": direzione, "regione": pg.get("regione"),
                     "indirizzo": pg.get("indirizzo"), "telefono": pg.get("telefono"), "email": pg.get("email"),
                     "pec": pg.get("pec"), "orario": pg.get("orario"), "url": pg.get("url"),
                     "successioni": bool(_RX_APSRI.search(nome_uff or vigenti.get(c, "")))}
    # l'ufficio «Atti pubblici, successioni» di ogni direzione provinciale: fra gli uffici trovati nel suo menu
    apsri_dp: dict = {}
    for c, pg in pagine.items():
        dp = pg.get("direzione_codice")
        if dp and (_RX_APSRI.search(vigenti.get(c, "")) or _RX_APSRI.search(pg.get("titolo") or "")):
            apsri_dp[dp] = c
    elenchi = []                                  # (ufficio, competente, regola, [comuni], [parti], [nomi non comuni])
    for c, pg in sorted(pagine.items()):
        if not pg.get("competenza") or c not in uffici:
            continue
        direzione = uffici[c]["direzione"]
        if not direzione and pg.get("direzione_codice"):
            dpt = (pagine.get(pg["direzione_codice"]) or {}).get("titolo") or ""
            direzione = dpt.split(" - ")[0]
            uffici[c]["direzione"] = direzione
        voci = [v.strip() for v in re.split(r",|;", pg["competenza"]) if v.strip()]
        nomi = [v for v in voci if not _RX_PARTE.match(v) and not re.fullmatch(r"[0-9IVXLC]+", v)]
        sigla = _provincia_della_direzione(direzione, nomi)
        competente = apsri_dp.get(pg.get("direzione_codice") or "") or apsri.get(norm(direzione)) or c
        regola = "ufficio «Atti pubblici, successioni» della direzione provinciale" if competente != c else \
            "ufficio territoriale del comune"
        risolti, parti, ignoti, tipo_parti = [], [], [], ""
        for v in voci:
            mp = _RX_PARTE.match(v)
            if mp:
                tipo_parti = tipo_parti or _TIPI_PARTE.get(mp.group(1).lower(), "parte")
                resto = mp.group(2)
                if re.fullmatch(r"[0-9IVXLC\s,e\-]+", resto):
                    parti += [str(int(x)) if x.isdigit() else x.upper() for x in re.findall(r"[0-9]+|[IVXLC]+", resto)]
                else:
                    parti.append(norm(resto))
                continue
            if re.fullmatch(r"[0-9]+|[IVXLC]+", v):
                parti.append(str(int(v)) if v.isdigit() else v.upper())
                continue
            trovati = risolvi_comune(v, sigla)
            (risolti.append(trovati[0]) if len(trovati) == 1 else ignoti.append(v))
        if parti:                                 # in una lista con parti, i nomi che non sono comuni sono quartieri
            parti += [norm(v) for v in ignoti]
            ignoti = []
        non_risolti += [f"{v} ({sigla}, {c})" for v in ignoti]
        elenchi.append((c, competente, regola, risolti, parti, tipo_parti or "parte"))
    # una citta' divisa e' il comune che sta nelle liste di PIU' uffici: le parti di una lista sono le sue
    quante_liste: dict = {}
    for _c, _comp, _r, risolti, _p, _t in elenchi:
        for x in risolti:
            quante_liste[x["codice"]] = quante_liste.get(x["codice"], 0) + 1
    for c, competente, regola, risolti, parti, tipo_parti in elenchi:
        divisa = None
        if parti:
            condivise = [x for x in risolti if quante_liste.get(x["codice"], 0) > 1]
            divisa = condivise[0]["codice"] if len(condivise) == 1 else None
            if divisa is None:
                non_risolti.append(f"parti {parti[:4]} senza città riconoscibile ({c})")
            else:
                d = divise.setdefault(divisa, {"tipo": tipo_parti, "parti": {}})
                for k in parti:
                    d["parti"][k] = {"ufficio": competente, "ufficio_territoriale": c}
        for x in risolti:
            b = x["codice"]
            if b in comuni and comuni[b]["ufficio"] != competente:
                comuni[b].setdefault("anche", [])
                if competente not in comuni[b]["anche"]:
                    comuni[b]["anche"].append(competente)
                divise.setdefault(b, {"tipo": "parte", "parti": {}})
                continue
            comuni.setdefault(b, {"comune": x["nome"], "provincia": x["provincia"], "ufficio": competente,
                                  "ufficio_territoriale": c, "regola": regola})
    for b, d in divise.items():
        if b in comuni:
            comuni[b]["divisa"] = d["tipo"]
    tutti = ci.carica().get("comuni", {})
    non_mappati = sorted(set(tutti) - set(comuni))
    return {"_meta": {"versione": 2, "verificato_il": _dt.date.today().isoformat(),
                      "regola": ("art. 6 D.Lgs. 346/1990 (dal 2027 la norma corrispondente del D.Lgs. 123/2025): ufficio nella cui "
                                 "circoscrizione era l'ultima residenza del de cuius; residenza estera → ultima residenza in "
                                 "Italia; se ignota, l'ufficio di Roma individuato dall'AdE"),
                      "fonti": ["codici vigenti: tracciato SUC13 (XSD AdE, uffici-suc13.md)",
                                "pagine AdE «Uffici» (dettaglioufficio/<codice>): indirizzo, recapiti, competenza territoriale",
                                "comuni: elenco ISTAT (dati/comuni-italiani.json)"],
                      "copertura": {"comuni_mappati": len(comuni), "comuni_italiani": len(tutti), "non_mappati": len(non_mappati),
                                    "uffici": len(uffici), "pagine_senza_dati": senza_pagina, "voci_non_risolte": non_risolti[:200]}},
            "uffici": uffici, "comuni": dict(sorted(comuni.items())), "citta_divise": dict(sorted(divise.items())),
            "non_mappati": non_mappati}


def controlla(nuova: dict, vecchia: dict | None) -> list:
    """Motivi per NON sostituire la tabella (struttura cambiata, copertura crollata, campi svuotati)."""
    motivi = []
    cop = nuova["_meta"]["copertura"]
    if cop["comuni_mappati"] < MIN_COMUNI_MAPPATI:
        motivi.append(f"comuni mappati {cop['comuni_mappati']} < {MIN_COMUNI_MAPPATI}")
    vigenti = set(codici_vigenti()) | set(nuova.get("uffici") or {})
    estranei = [c for c in {v["ufficio"] for v in nuova["comuni"].values()} if c not in vigenti]
    if estranei:
        motivi.append(f"uffici non vigenti nel tracciato: {estranei[:5]}")
    if vecchia and (vecchia.get("_meta") or {}).get("versione") == 2:
        for c, u in (vecchia.get("uffici") or {}).items():
            n = (nuova.get("uffici") or {}).get(c)
            for campo in ("pec", "indirizzo"):
                if n is not None and u.get(campo) and not n.get(campo):
                    n[campo] = u[campo]          # un campo pieno che torna vuoto: si tiene il vecchio (e si dice)
                    nuova["_meta"].setdefault("campi_conservati", []).append(f"{c}.{campo}")
    return motivi


def main() -> int:
    ap = argparse.ArgumentParser(description="Uffici competenti per le successioni in tutta Italia (pagine AdE)")
    ap.add_argument("--raccogli", action="store_true")
    ap.add_argument("--costruisci", action="store_true")
    ap.add_argument("--aggiorna", action="store_true")
    ap.add_argument("--cache", default=str(Path.home() / ".cache" / "uffici-ade"))
    ap.add_argument("--out", default=str(TABELLA))
    ap.add_argument("--nel-repo", action="store_true", help="(compatibilita') scrive nella tabella della skill")
    a = ap.parse_args()
    cache = Path(a.cache)
    if a.raccogli or a.aggiorna:
        r = raccogli(cache)
        print(f"📥 pagine in cache: {r['pagine']} · errori: {len(r['errori'])}" + (f" ({', '.join(r['errori'][:8])})" if r["errori"] else ""))
    if a.costruisci or a.aggiorna:
        nuova = costruisci(cache)
        out = Path(a.out)
        try:
            vecchia = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
        except ValueError:
            vecchia = None
        motivi = controlla(nuova, vecchia)
        cop = nuova["_meta"]["copertura"]
        print(f"🏛️  uffici {cop['uffici']} · comuni mappati {cop['comuni_mappati']}/{cop['comuni_italiani']} · "
              f"città divise {len(nuova['citta_divise'])} · voci non risolte {len(cop['voci_non_risolte'])}")
        if motivi:
            print("⛔ tabella NON sostituita: " + "; ".join(motivi))
            return 1
        out.write_text(json.dumps(nuova, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"📝 {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
