---
{
  "id": "S06",
  "titolo": "Dichiarazione di conformità all'originale delle copie allegate",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 47 D.P.R. 445/2000",
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

# S06 · Dichiarazione di conformità all'originale delle copie allegate

## Quando si usa

Quando alla dichiarazione si allegano copie (testamento, documenti delle passività, bilanci, certificazioni della banca): una sola dichiarazione per tutte le copie.

- Obbligo: **consigliato** · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG)
- Perché: testamento, documenti delle passività, bilanci e inventari si allegano in copia non autentica con questa dichiarazione (art. 30 c. 3-bis TUS)
- Voci di DEAS che sostituisce: Dichiarazione copia conforme

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 47 D.P.R. 445/2000
- art. 30 D.Lgs. 346/1990
- art. 115 D.Lgs. 123/2025

## Note e trappole

Art. 30 c. 3-bis TUS: i documenti delle lettere c), d), g), h) e i) possono essere sostituiti da copie non autentiche con la dichiarazione sostitutiva dell'art. 47 D.P.R. 445/2000 che attesta che sono copie degli originali; l'Agenzia può chiedere gli originali. Art. 19 D.P.R. 445/2000: la conformità all'originale.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DELL'ATTO DI NOTORIETÀ
## (art. 47 del D.P.R. 28 dicembre 2000, n. 445, e {% se DAL_2027 %}art. 115, comma 4, del D.Lgs. 1° agosto 2025, n. 123{% altrimenti %}art. 30, comma 3-bis, del D.Lgs. 31 ottobre 1990, n. 346{% fine %}) — copie conformi agli originali

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
in qualità di dichiarante nella successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

che le copie dei seguenti documenti, allegate alla dichiarazione di successione, costituiscono copie dei relativi originali, che ha personalmente visionato:
{% per A in ALLEGATI %}
- {{ A.descrizione }};
{% fine %}
- ______________________________________________________________;
- ______________________________________________________________.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
