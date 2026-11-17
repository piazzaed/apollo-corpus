---
{
  "id": "S10",
  "titolo": "Dichiarazione sostitutiva sulla destinazione urbanistica dei terreni",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 34 D.Lgs. 346/1990",
    "art. 47 D.P.R. 445/2000"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S10 · Dichiarazione sostitutiva sulla destinazione urbanistica dei terreni

## Quando si usa

Con terreni nell'asse, se non si chiede il certificato di destinazione urbanistica (S11): chi firma barra la destinazione che risulta dallo strumento urbanistico.

- Obbligo: **consigliato** · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG)
- Perché: il valore catastale dei terreni non si rettifica, salvo che lo strumento urbanistico preveda la destinazione edificatoria (art. 34 c. 5 TUS): la destinazione va accertata (certificato del Comune o dichiarazione)
- Voci di DEAS che sostituisce: Autocertificazione destinazione urbanistica

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 34 D.Lgs. 346/1990
- art. 47 D.P.R. 445/2000

## Note e trappole

Art. 34 c. 5 TUS: il valore dichiarato non inferiore a quello catastale non è rettificabile, ma la regola non vale per i terreni con destinazione edificatoria. Il certificato si chiede al Comune (art. 30 c. 3 D.P.R. 380/2001): questa dichiarazione lo sostituisce solo come dichiarazione di parte.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DELL'ATTO DI NOTORIETÀ
## (art. 47 del D.P.R. 28 dicembre 2000, n. 445) — destinazione urbanistica dei terreni

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
in qualità di dichiarante nella successione di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

che, secondo gli strumenti urbanistici vigenti o adottati alla data del decesso, i seguenti terreni:
{% per T in TERRENI %}
- {{ T.descrizione }} — {{ T.titolarita }};
{% fine %}
hanno la seguente destinazione:
- ☐ agricola, senza destinazione edificatoria;
- ☐ edificatoria (indicare quali terreni e lo strumento urbanistico): ______________________________;
- ☐ altra: ______________________________.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
