---
{
  "id": "S04",
  "titolo": "Dichiarazione sostitutiva dello stato di famiglia del de cuius",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 46 D.P.R. 445/2000",
    "art. 30 D.Lgs. 346/1990",
    "art. 115 D.Lgs. 123/2025"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S04 · Dichiarazione sostitutiva dello stato di famiglia del de cuius

## Quando si usa

Al posto del certificato di stato di famiglia del defunto. La composizione della famiglia anagrafica non sta nel .suc: la scrive a mano chi firma.

- Obbligo: **consigliato** (dal 2027: obbligatorio) · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG)
- Perché: sostituisce il certificato di stato di famiglia del defunto (art. 30 c. 1 lett. b e c. 3 TUS; dal 2027 art. 115 c. 1 lett. b TU 123/2025)
- Voci di DEAS che sostituisce: Autocertificazione stato di famiglia (de cuius)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 46 D.P.R. 445/2000
- art. 30 D.Lgs. 346/1990
- art. 115 D.Lgs. 123/2025

## Note e trappole

Lo stato di famiglia è uno degli stati dell'art. 46 c. 1 lett. f D.P.R. 445/2000. La famiglia anagrafica (chi conviveva col defunto) non coincide con gli eredi: le righe si compilano a mano.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DI CERTIFICAZIONE
## (art. 46 del D.P.R. 28 dicembre 2000, n. 445) — stato di famiglia del de cuius

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

che alla data del decesso ({{ DEFUNTO.data_decesso }}) la famiglia anagrafica di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, era composta come segue:
- ☐ dal solo de cuius;
- ☐ dal de cuius e dalle seguenti persone (cognome e nome, luogo e data di nascita, rapporto con il de cuius):
- ____________________________________________________________________________
- ____________________________________________________________________________
- ____________________________________________________________________________

La presente dichiarazione è resa ai fini della dichiarazione di successione {% se DAL_2027 %}(art. 115, comma 1, lettera b), del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 30, comma 3, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
