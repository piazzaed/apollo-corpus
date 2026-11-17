---
{
  "id": "S24",
  "titolo": "Ricorso al giudice tutelare per l'autorizzazione ad accettare l'eredità con beneficio d'inventario (minore)",
  "tipo_atto": "ricorso",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 320 c.c.",
    "art. 471 c.c.",
    "art. 484 c.c."
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S24 · Ricorso al giudice tutelare per l'autorizzazione ad accettare l'eredità con beneficio d'inventario (minore)

## Quando si usa

Quando un chiamato è minorenne: il ricorso lo firmano i genitori che esercitano la responsabilità genitoriale. Per un interdetto o un beneficiario di amministrazione di sostegno il ricorso è del tutore o dell'amministratore (da adattare). La dichiarazione di successione si può presentare anche prima dell'accettazione.

- Obbligo: **consigliato** · firma: genitori · va a: giudice tutelare competente
- Perché: l'eredità devoluta a un minore si accetta solo col beneficio d'inventario (art. 471 c.c.) e i genitori accettano per il figlio solo con l'autorizzazione del giudice tutelare (art. 320 c.c.)
- Voci di DEAS che sostituisce: Richiesta accettazione con beneficio di inventario (minore), Richiesta accettazione con beneficio di inventario (interdetto)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 320 c.c.
- art. 471 c.c.
- art. 484 c.c.

## Note e trappole

Art. 471 c.c.: le eredità devolute ai minori e agli interdetti si accettano solo col beneficio d'inventario. Art. 320 c. 3 c.c.: i genitori non possono accettare o rinunziare a eredità per il figlio se non per necessità o utilità evidente dopo autorizzazione del giudice tutelare. Art. 484 c.c.: dichiarazione davanti al notaio o al cancelliere e inventario. Competenza e forma del ricorso vanno verificate sul caso.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Al Giudice tutelare del Tribunale di ______________________

# RICORSO
## per l'autorizzazione ad accettare con beneficio d'inventario l'eredità devoluta a un minore (artt. 320 e 471 del codice civile)

☐ I sottoscritti ______________________________ e ______________________________, genitori esercenti congiuntamente la responsabilità genitoriale, ☐ Il/La sottoscritto/a ______________________________, genitore che esercita in via esclusiva la responsabilità genitoriale, sul minore {{ M.nome_completo }}, {{ M.nato }} a {{ M.luogo_nascita }} il {{ M.data_nascita }}, codice fiscale {{ M.codice_fiscale }}, residente in {{ M.residenza }},

**PREMESSO**

- che il giorno {{ DEFUNTO.data_decesso }} è {{ DEFUNTO.deceduto }} a {{ DEFUNTO.luogo_decesso }} {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }};
- che il minore è chiamato all'eredità in qualità di {{ M.relazione }} del de cuius{% se TESTAMENTO %}, in forza di testamento {{ TESTAMENTO.tipo }} {{ TESTAMENTO.pubblicazione }}{% altrimenti %}, per legge{% fine %};
- che l'asse ereditario comprende, per quanto noto, i beni indicati nell'elenco allegato;
- che l'eredità devoluta a un minore si accetta solo col beneficio d'inventario (art. 471 del codice civile) e che l'accettazione con beneficio d'inventario risponde alla necessità o all'evidente utilità del minore per le ragioni seguenti: ______________________________________________;

**CHIEDE/CHIEDONO**

di essere autorizzato/i ad accettare con beneficio d'inventario, in nome e per conto del minore, l'eredità di {{ DEFUNTO.nome_completo }}, con dichiarazione da rendere davanti al notaio o al cancelliere, preceduta o seguita dall'inventario (art. 484 del codice civile).

Si allegano: dichiarazione sostitutiva di certificazione di morte; stato di famiglia; elenco dei beni; copie dei documenti d'identità dei ricorrenti.

Luogo e data: ______________________________
[FIRMA: genitore]
[FIRMA: secondo genitore (se la responsabilità è congiunta)]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
