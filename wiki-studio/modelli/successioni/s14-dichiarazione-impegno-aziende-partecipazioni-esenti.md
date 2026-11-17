---
{
  "id": "S14",
  "titolo": "Dichiarazione di impegno per l'esenzione di aziende e partecipazioni (art. 3 c. 4-ter TUS)",
  "tipo_atto": "dichiarazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 3 D.Lgs. 346/1990",
    "art. 89 D.Lgs. 123/2025",
    "art. 320 c.c."
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S14 · Dichiarazione di impegno per l'esenzione di aziende e partecipazioni (art. 3 c. 4-ter TUS)

## Quando si usa

Per ogni discendente o coniuge che riceve aziende, quote o azioni con l'agevolazione D.

- Obbligo: **obbligatorio** · firma: voce · va a: Agenzia delle Entrate (con la dichiarazione; allegato EG se chi firma non è il dichiarante)
- Perché: l'esenzione di aziende, quote e azioni trasferite a discendenti e coniuge vale se gli aventi causa rendono, con la dichiarazione di successione, l'impegno quinquennale (art. 3 c. 4-ter TUS; dal 2027 art. 89 c. 6 TU)
- Voci di DEAS che sostituisce: Dichiarazione per esenzione art. 3, comma 4 Ter (Testo Unico)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 3 D.Lgs. 346/1990
- art. 89 D.Lgs. 123/2025
- art. 320 c.c.

## Note e trappole

Art. 3 c. 4-ter TUS: aziende → prosecuzione dell'attività per almeno cinque anni; partecipazioni di controllo in società di capitali → detenzione del controllo per cinque anni; altre quote → titolarità per cinque anni. L'impegno si rende contestualmente alla dichiarazione; il mancato rispetto comporta decadenza, imposta ordinaria, sanzione e interessi.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE DI IMPEGNO
## {% se APERTA_DAL_2027 %}(art. 89, comma 6, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 3, comma 4-ter, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} {{ F.relazione }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}, avente causa dei seguenti beni:
{% per B in F.BENI %}
- {{ B.descrizione }};
{% fine %}

**DICHIARA DI IMPEGNARSI** (barrare la casella che ricorre):
- ☐ a proseguire l'esercizio dell'attività d'impresa per un periodo non inferiore a cinque anni dalla data del trasferimento (aziende o rami di azienda);
- ☐ a detenere il controllo, ai sensi dell'art. 2359, primo comma, numero 1), del codice civile, per un periodo non inferiore a cinque anni dalla data del trasferimento (azioni e quote di società di capitali);
- ☐ a mantenere la titolarità del diritto per un periodo non inferiore a cinque anni dalla data del trasferimento (altre quote sociali).

Dichiara di essere a conoscenza che il mancato rispetto delle condizioni comporta la decadenza dal beneficio, il pagamento dell'imposta in misura ordinaria, della sanzione e degli interessi di mora.
{% se F.minore %}
La prosecuzione di un'impresa commerciale da parte del minore richiede l'autorizzazione del giudice tutelare (art. 320, quinto comma, del codice civile).
{% fine %}

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
