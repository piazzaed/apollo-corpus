---
{
  "id": "S13",
  "titolo": "Delega per la presentazione della domanda di voltura catastale",
  "tipo_atto": "delega",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 38 D.P.R. 445/2000"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S13 · Delega per la presentazione della domanda di voltura catastale

## Quando si usa

Quando nella dichiarazione è barrata la casella che esclude le volture automatiche: la voltura si presenta poi con Voltura Web o allo sportello.

- Obbligo: **consigliato** · firma: dichiarante · va a: Agenzia delle Entrate — Ufficio provinciale - Territorio
- Perché: le volture non partono con la dichiarazione (casella «non dar corso alle volture»): la domanda si presenta a parte, e il delegato agisce in rappresentanza (art. 38 c. 3-bis D.P.R. 445/2000)
- Voci di DEAS che sostituisce: Delega presentazione voltura (con dati delegato)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 38 D.P.R. 445/2000

## Note e trappole

Art. 38 c. 3-bis D.P.R. 445/2000: il potere di rappresentanza per presentare istanze e dichiarazioni e ritirare atti presso le pubbliche amministrazioni può essere conferito ad altro soggetto con le modalità dello stesso articolo (firma e copia del documento d'identità).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DELEGA
## per la presentazione della domanda di volture catastali (art. 38, comma 3-bis, del D.P.R. 28 dicembre 2000, n. 445)

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} in qualità di {{ F.qualita }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},

**DELEGA**

{{ INTERMEDIARIO.nome_completo }}, codice fiscale {{ INTERMEDIARIO.codice_fiscale }}, con studio in {{ INTERMEDIARIO.indirizzo }}, a presentare all'Agenzia delle Entrate, Ufficio provinciale - Territorio, la domanda di volture catastali conseguente alla successione sopra indicata per gli immobili dichiarati, a sottoscriverla per suo conto ove occorra e a ritirarne le ricevute.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (delegante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del delegante.
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
