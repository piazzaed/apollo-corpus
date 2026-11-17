#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IL TESTO DEI MODULI DELLE SUCCESSIONI (v0.55): una lingua minima per i documenti da compilare. Solo stdlib.

PERCHE'
-------
I documenti che accompagnano una successione (incarico all'intermediario, dichiarazioni sostitutive, prima casa,
lettere alle banche…) sono testi fissi con parti variabili: chi firma, il de cuius, gli eredi, gli immobili. Il testo
lo scrive e lo verifica una persona (o la sentinella dei modelli, sotto controllo meccanico); i dati li mette uno
script, sempre allo stesso modo. Questa e' la lingua dei testi: piccola apposta, perche' la legge sia la sentinella
nel repo pubblico sia il plugin, e perche' un errore di sintassi si veda prima di compilare.

SINTASSI (nella sezione «Testo del modello» della scheda, dentro il blocco ```)
  {{ X }}  {{ X.campo }}               il valore; se manca → [DA COMPLETARE: <che cosa>] (e si annota)
  {{ X | maiuscolo }}                  filtri: maiuscolo · minuscolo · elenco (lista di testi → «a, b e c»)
  {% se COND %} … {% altrimenti %} … {% fine %}
                                       COND: X · non X · X == "testo" · X != "testo"; un dato mancante e' falso
  {% per E in LISTA %} … {% fine %}    dentro: {{ E.campo }}, {{ ciclo.n }} (da 1), {% se ciclo.ultimo %}
Una riga che contiene solo un comando {% … %} sparisce con il suo a capo.

RIGHE (dopo la compilazione: le interpreta chi scrive il .docx)
  # TITOLO            titolo centrato in grassetto        ## sottotitolo     centrato
  >> testo            allineato a destra (destinatario)   - voce             elenco puntato
  [FIRMA: chi]        spazio per la firma con l'etichetta  [PAGINA]           salto pagina
  **testo**           grassetto dentro la riga            ogni riga non vuota e' un paragrafo

Uso:
  python3 scripts/suc_modelli_testo.py --controlla FILE   # sintassi e variabili di un testo (o di una scheda .md)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":  # Cowork/Desktop su Windows: le pipe sono cp1252 → UTF-8
    for _s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

_RX_TOKEN = re.compile(r"({{.*?}}|{%.*?%})", re.S)
_RX_SOLO_COMANDO = re.compile(r"^[ \t]*({%[^%]*%})[ \t]*\n", re.M)
_RX_PERCORSO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_RX_COND = re.compile(r'^(non\s+)?([A-Za-z_][\w.]*)\s*(?:(==|!=)\s*"([^"]*)")?$')
_RX_PER = re.compile(r"^per\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_][\w.]*)$")
FILTRI = ("maiuscolo", "minuscolo", "elenco")
#: il segnaposto dei dati mancanti (la convenzione della v0.29: si vede, si cerca, non si confonde col testo)
MANCA = "[DA COMPLETARE: {}]"


class ErroreModello(ValueError):
    pass


# ---------------------------------------------------------------- analisi

def _tokens(testo: str) -> list:
    testo = _RX_SOLO_COMANDO.sub(r"\1", testo)
    return [t for t in _RX_TOKEN.split(testo) if t != ""]


def analizza(testo: str) -> list:
    """Il testo diventa un albero: ("testo", s) · ("var", percorso, filtri) · ("se", cond, allora, altrimenti) ·
    ("per", nome, lista, corpo). ErroreModello alla prima sintassi sbagliata, col pezzo che la contiene."""
    pila = [("radice", [], None)]
    for tok in _tokens(testo):
        if tok.startswith("{{"):
            interno = tok[2:-2].strip()
            parti = [p.strip() for p in interno.split("|")]
            if not _RX_PERCORSO.match(parti[0]):
                raise ErroreModello(f"variabile non valida: {tok}")
            for f in parti[1:]:
                if f not in FILTRI:
                    raise ErroreModello(f"filtro sconosciuto «{f}» in {tok} (ammessi: {', '.join(FILTRI)})")
            pila[-1][1].append(("var", parti[0], tuple(parti[1:])))
        elif tok.startswith("{%"):
            cmd = re.sub(r"\s+", " ", tok[2:-2].strip())
            if cmd.startswith("se "):
                m = _RX_COND.match(cmd[3:].strip())
                if not m:
                    raise ErroreModello(f"condizione non valida: {tok}")
                nodo = ["se", (bool(m.group(1)), m.group(2), m.group(3), m.group(4)), [], []]
                pila.append(("se", nodo[2], nodo))
            elif cmd == "altrimenti":
                if pila[-1][0] != "se":
                    raise ErroreModello("{% altrimenti %} fuori da un {% se %}")
                _t, _corpo, nodo = pila.pop()
                pila.append(("altrimenti", nodo[3], nodo))
            elif cmd.startswith("per "):
                m = _RX_PER.match(cmd)
                if not m:
                    raise ErroreModello(f"ciclo non valido: {tok} (forma: {{% per E in LISTA %}})")
                nodo = ["per", m.group(1), m.group(2), []]
                pila.append(("per", nodo[3], nodo))
            elif cmd == "fine":
                if len(pila) == 1:
                    raise ErroreModello("{% fine %} di troppo")
                _t, _corpo, nodo = pila.pop()
                pila[-1][1].append(tuple(nodo))
            else:
                raise ErroreModello(f"comando sconosciuto: {tok}")
        else:
            if "{{" in tok or "{%" in tok or "}}" in tok or "%}" in tok:
                raise ErroreModello(f"graffa non chiusa vicino a: {tok[:60]!r}")
            pila[-1][1].append(("testo", tok))
    if len(pila) != 1:
        raise ErroreModello(f"{{% {pila[-1][0]} %}} senza {{% fine %}}")
    return pila[0][1]


def controlla(testo: str) -> list:
    """Gli errori di sintassi (lista vuota = testo valido)."""
    try:
        analizza(testo)
        return []
    except ErroreModello as e:
        return [str(e)]


def variabili(testo: str) -> set:
    """Le variabili che il testo usa, col nome delle liste per quelle dei cicli («EREDI[].nome»). Servono al controllo
    meccanico della sentinella: una correzione del testo non deve inventare dati che lo script non fornisce."""
    out = set()

    def giro(nodi, alias):
        for n in nodi:
            if n[0] == "var":
                out.add(_canonico(n[1], alias))
            elif n[0] == "se":
                if n[1][1].split(".")[0] != "ciclo":
                    out.add(_canonico(n[1][1], alias))
                giro(n[2], alias)
                giro(n[3], alias)
            elif n[0] == "per":
                out.add(_canonico(n[2], alias))
                giro(n[3], {**alias, n[1]: _canonico(n[2], alias) + "[]"})

    giro(analizza(testo), {})
    return {v for v in out if not v.startswith("ciclo")}


def _canonico(percorso: str, alias: dict) -> str:
    testa, _, coda = percorso.partition(".")
    if testa in alias:
        return alias[testa] + ("." + coda if coda else "")
    return percorso


def testo_piatto(testo: str, fissi: dict) -> str:
    """Il testo con i soli comandi decisi da `fissi` (es. {"DAL_2027": True}): le condizioni su quelle variabili scelgono
    il loro ramo, le altre tengono entrambi i rami, i cicli il loro corpo una volta, le variabili diventano spazi. Serve
    a controllare le norme citate regime per regime (le citazioni del 2027 alla data del 2027)."""
    def giro(nodi) -> str:
        pezzi = []
        for n in nodi:
            if n[0] == "testo":
                pezzi.append(n[1])
            elif n[0] == "var":
                pezzi.append(" ")
            elif n[0] == "se":
                negato, percorso, op, atteso = n[1]
                if percorso in fissi and op is None:
                    vero = bool(fissi[percorso]) != negato
                    pezzi.append(giro(n[2] if vero else n[3]))
                else:
                    pezzi.append(giro(n[2]) + " " + giro(n[3]))
            elif n[0] == "per":
                pezzi.append(giro(n[3]))
        return "".join(pezzi)
    return giro(analizza(testo))


# ---------------------------------------------------------------- compilazione

class _Mancante:
    def __init__(self, percorso: str):
        self.percorso = percorso


def _risolvi(percorso: str, ambito: dict):
    parti = percorso.split(".")
    if parti[0] not in ambito:
        return _Mancante(percorso)
    val = ambito[parti[0]]
    for p in parti[1:]:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            return _Mancante(percorso)
    if val is None or val == "" or val == []:
        return _Mancante(percorso)
    return val


def _vero(cond: tuple, ambito: dict) -> bool:
    negato, percorso, op, atteso = cond
    val = _risolvi(percorso, ambito)
    if isinstance(val, _Mancante):
        esito = False if op != "!=" else True
    elif op == "==":
        esito = str(val) == atteso
    elif op == "!=":
        esito = str(val) != atteso
    else:
        esito = bool(val)
    return (not esito) if negato else esito


def _elenco(v) -> str:
    v = [str(x) for x in v if str(x).strip()]
    if len(v) < 2:
        return "".join(v)
    return ", ".join(v[:-1]) + " e " + v[-1]


def _filtra(val, filtri) -> str:
    for f in filtri:
        if f == "elenco":
            val = _elenco(val if isinstance(val, (list, tuple)) else [val])
        elif f == "maiuscolo":
            val = str(val).upper()
        elif f == "minuscolo":
            val = str(val).lower()
    return str(val)


def compila(testo: str, contesto: dict, descrizioni: dict = None) -> tuple:
    """(testo compilato, mancanti): ogni dato che manca diventa «[DA COMPLETARE: …]» con la descrizione del percorso
    (`descrizioni`, chiavi con i nomi canonici: «EREDI[].comune_nascita»), e finisce nell'elenco dei mancanti."""
    descrizioni = descrizioni or {}
    mancanti = []

    def giro(nodi, ambito, alias) -> str:
        pezzi = []
        for n in nodi:
            if n[0] == "testo":
                pezzi.append(n[1])
            elif n[0] == "var":
                val = _risolvi(n[1], ambito)
                if isinstance(val, _Mancante):
                    canon = _canonico(n[1], alias)
                    descr = descrizioni.get(canon) or descrizioni.get(canon.split(".")[-1]) or canon
                    chi = ""
                    testa = n[1].split(".")[0]
                    if testa in alias and isinstance(ambito.get(testa), dict) and ambito[testa].get("nome_completo"):
                        chi = f" di {ambito[testa]['nome_completo']}"
                    descr = f"{descr}{chi}"
                    if descr not in mancanti:
                        mancanti.append(descr)
                    pezzi.append(MANCA.format(descr))
                else:
                    pezzi.append(_filtra(val, n[2]))
            elif n[0] == "se":
                pezzi.append(giro(n[2] if _vero(n[1], ambito) else n[3], ambito, alias))
            elif n[0] == "per":
                lista = _risolvi(n[2], ambito)
                if isinstance(lista, _Mancante) or not isinstance(lista, (list, tuple)):
                    continue
                for i, el in enumerate(lista, start=1):
                    sub = {**ambito, n[1]: el, "ciclo": {"n": i, "ultimo": i == len(lista), "primo": i == 1}}
                    pezzi.append(giro(n[3], sub, {**alias, n[1]: _canonico(n[2], alias) + "[]"}))
        return "".join(pezzi)

    uscita = giro(analizza(testo), contesto, {})
    uscita = re.sub(r"[ \t]+\n", "\n", uscita)
    uscita = re.sub(r"\n{3,}", "\n\n", uscita).strip() + "\n"
    return uscita, mancanti


# ---------------------------------------------------------------- righe → blocchi (per chi scrive il .docx)

def blocchi(testo: str) -> list:
    """Le righe compilate diventano blocchi: (tipo, testo) con tipo titolo · sottotitolo · destra · voce · firma ·
    pagina · vuota · paragrafo."""
    out = []
    for riga in testo.split("\n"):
        r = riga.rstrip()
        s = r.strip()
        if not s:
            out.append(("vuota", ""))
        elif s == "[PAGINA]":
            out.append(("pagina", ""))
        elif s.startswith("## "):
            out.append(("sottotitolo", s[3:].strip()))
        elif s.startswith("# "):
            out.append(("titolo", s[2:].strip()))
        elif s.startswith(">> "):
            out.append(("destra", s[3:].strip()))
        elif s.startswith("- "):
            out.append(("voce", s[2:].strip()))
        elif re.fullmatch(r"\[FIRMA:\s*(.+?)\]", s):
            out.append(("firma", re.fullmatch(r"\[FIRMA:\s*(.+?)\]", s).group(1)))
        else:
            out.append(("paragrafo", s))
    while out and out[-1][0] == "vuota":
        out.pop()
    return out


def corse(testo: str) -> list:
    """«**grassetto**» dentro una riga → [(testo, grassetto)]."""
    parti = re.split(r"(\*\*.+?\*\*)", testo)
    return [(p[2:-2], True) if p.startswith("**") and p.endswith("**") and len(p) > 4 else (p, False)
            for p in parti if p]


# ---------------------------------------------------------------- schede

_RX_BLOCCO = re.compile(r"^## Testo del modello[^\n]*\n+```[a-z]*\n(.*?)\n```", re.S | re.M)


def testo_da_scheda(scheda: str) -> str:
    """Il testo del modello dentro la scheda .md (sezione «## Testo del modello», primo blocco ```)."""
    m = _RX_BLOCCO.search(scheda)
    if not m:
        raise ErroreModello("la scheda non ha la sezione «## Testo del modello» con un blocco ```")
    return m.group(1)


def intestazione_scheda(scheda: str) -> dict:
    """Il frontmatter JSON della scheda (fra le due righe «---»)."""
    m = re.match(r"^---\n(.*?)\n---\n", scheda, re.S)
    if not m:
        raise ErroreModello("la scheda non comincia con il frontmatter fra due righe «---»")
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        raise ErroreModello(f"frontmatter non e' JSON valido: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--controlla", metavar="FILE")
    a = ap.parse_args(argv)
    if not a.controlla:
        ap.print_help()
        return 2
    s = Path(a.controlla).read_text(encoding="utf-8")
    try:
        testo = testo_da_scheda(s) if s.startswith("---\n") else s
        err = controlla(testo)
    except ErroreModello as e:
        err = [str(e)]
    if err:
        print("ERRORE: " + "; ".join(err))
        return 1
    print("OK · variabili: " + ", ".join(sorted(variabili(testo))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
