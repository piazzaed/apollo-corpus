---
{
  "id": "S05",
  "titolo": "Dichiarazione sostitutiva dello stato di famiglia dell'erede",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 46 D.P.R. 445/2000",
    "art. 30 D.Lgs. 346/1990"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S05 · Dichiarazione sostitutiva dello stato di famiglia dell'erede

## Quando si usa

Per le dichiarazioni presentate dal 1/1/2027 è un allegato (art. 115 c. 1 lett. b TU 123/2025, come modificato dal D.Lgs. 141/2026) per gli eredi e legatari parenti o affini del defunto; prima, solo su richiesta (--solo S05), quando l'ufficio chiede gli stati di famiglia degli eredi.

- Obbligo: **facoltativo** (dal 2027: obbligatorio) · firma: voce · va a: Agenzia delle Entrate (allegato EG), se l'ufficio lo chiede
- Perché: sostituisce il certificato di stato di famiglia degli eredi e legatari parenti o affini del defunto (art. 30 c. 1 lett. b e c. 3 TUS)
- Voci di DEAS che sostituisce: Autocertificazione stato di famiglia (eredi)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 46 D.P.R. 445/2000
- art. 30 D.Lgs. 346/1990

## Note e trappole

Uno per ciascun erede o legatario: lo firma l'interessato.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DI CERTIFICAZIONE
## (art. 46 del D.P.R. 28 dicembre 2000, n. 445) — stato di famiglia

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

che {% se F.minore %}il minore è{% altrimenti %}è{% fine %} {{ F.relazione }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}, e che la famiglia anagrafica {% se F.minore %}del minore{% altrimenti %}del sottoscrittore{% fine %} è composta come segue:
- ☐ da una sola persona;
- ☐ dalle seguenti persone, oltre a {{ F.nome_completo }} (cognome e nome, luogo e data di nascita, rapporto di parentela):
- ____________________________________________________________________________
- ____________________________________________________________________________

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
