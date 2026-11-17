---
{
  "id": "S09",
  "titolo": "Dichiarazione sostitutiva sui dati catastali degli immobili",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 47 D.P.R. 445/2000"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S09 · Dichiarazione sostitutiva sui dati catastali degli immobili

## Quando si usa

Facoltativa: le visure catastali bastano di solito. Utile quando le visure non riportano bene l'intestazione o per un ufficio che la chiede.

- Obbligo: **facoltativo** · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG, se richiesta)
- Perché: attesta gli identificativi catastali e la titolarità degli immobili del de cuius, se l'ufficio o una banca la chiede al posto delle visure
- Voci di DEAS che sostituisce: Autocertificazione identificativi catastali

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 47 D.P.R. 445/2000

## Note e trappole

Dichiarazione sostitutiva dell'atto di notorietà (art. 47 D.P.R. 445/2000) con l'elenco degli immobili come risultano dalla pratica: chi firma deve controllarli.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DELL'ATTO DI NOTORIETÀ
## (art. 47 del D.P.R. 28 dicembre 2000, n. 445) — dati catastali degli immobili

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
in qualità di dichiarante nella successione di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

che alla data del decesso risultavano intestati in catasto al de cuius i seguenti immobili, per i diritti indicati:
{% per I in IMMOBILI %}
- {{ I.descrizione }}{% se I.indirizzo %}, {{ I.indirizzo }}{% fine %} — {{ I.titolarita }};
{% fine %}
- ______________________________________________________________.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
