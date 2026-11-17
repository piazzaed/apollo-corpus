---
{
  "id": "S02",
  "titolo": "Dichiarazione sostitutiva dell'atto di notorietà (eredi e testamento)",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 46 D.P.R. 445/2000",
    "art. 47 D.P.R. 445/2000",
    "art. 76 D.P.R. 445/2000"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S02 · Dichiarazione sostitutiva dell'atto di notorietà (eredi e testamento)

## Quando si usa

Sempre: è la dichiarazione degli eredi (decesso, testamento, eredi e legatari, rinunce) che va allegata in EG e che le banche chiedono per svincolare i rapporti.

- Obbligo: **consigliato** · firma: dichiarante · va a: banche; Agenzia delle Entrate (allegato EG) solo se il quadro EH non basta
- Perché: attesta il decesso, il testamento o la sua mancanza e chi sono i chiamati: è la prova che chiedono le banche; verso l'Agenzia le dichiarazioni del dichiarante stanno nel quadro EH (provv. 27/12/2016, punto 4.4) e questa va in EG solo se servono elementi che l'EH non contiene
- Voci di DEAS che sostituisce: Dichiarazione sostitutiva di atto di notorietà, Dichiarazione di Autocertificazione

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 46 D.P.R. 445/2000
- art. 47 D.P.R. 445/2000
- art. 76 D.P.R. 445/2000

## Note e trappole

Gli stati e i fatti non indicati nell'art. 46 si comprovano con la dichiarazione sostitutiva dell'atto di notorietà (art. 47 c. 3 D.P.R. 445/2000), che può riguardare anche fatti relativi ad altri soggetti di cui il dichiarante ha diretta conoscenza (art. 47 c. 2).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE SOSTITUTIVA DELL'ATTO DI NOTORIETÀ
## (artt. 46 e 47 del D.P.R. 28 dicembre 2000, n. 445)

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %}
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**DICHIARA**

- che il giorno {{ DEFUNTO.data_decesso }} è {{ DEFUNTO.deceduto }} a {{ DEFUNTO.luogo_decesso }} {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, di stato civile {{ DEFUNTO.stato_civile }};
{% se TESTAMENTO %}
- che il de cuius ha disposto dei propri beni con testamento {{ TESTAMENTO.tipo }} in data {{ TESTAMENTO.data }}, {{ TESTAMENTO.pubblicazione }}, {{ TESTAMENTO.registrazione }}, e che, per quanto a sua conoscenza, non esistono altre disposizioni testamentarie;
{% altrimenti %}
- che, per quanto a sua conoscenza, il de cuius non ha lasciato disposizioni testamentarie e che l'eredità si devolve per legge;
{% fine %}
- che i chiamati all'eredità{% se LEGATARI %} e i legatari{% fine %} sono:
{% per E in BENEFICIARI %}
- {{ E.nome_completo }}, {{ E.nato }} a {{ E.luogo_nascita }} il {{ E.data_nascita }}, codice fiscale {{ E.codice_fiscale }}, {{ E.relazione }} del de cuius{% se E.tipo == "2" %} (legatari{{ E.o }}){% fine %}{% se E.minore %}, minore di età{% fine %};
{% fine %}
{% se RINUNCIATARI %}
- che hanno rinunciato all'eredità:
{% per R in RINUNCIATARI %}
- {{ R.nome_completo }}, {{ R.nato }} a {{ R.luogo_nascita }} il {{ R.data_nascita }}, codice fiscale {{ R.codice_fiscale }}, {{ R.relazione }} del de cuius;
{% fine %}
{% fine %}
{% se PER_LEGGE %}
- che, oltre alle persone sopra indicate, non vi sono altri soggetti che abbiano diritto all'eredità per legge;
{% altrimenti %}
- ☐ che il de cuius non ha lasciato coniuge, figli o loro discendenti, né ascendenti, diversi dalle persone sopra indicate, oppure ☐ che gli altri legittimari sono: ______________________________;
{% fine %}
{% se CONIUGE_EREDE %}
- che fra il de cuius e il coniuge superstite non è stata pronunciata sentenza di separazione personale, passata in giudicato, con addebito della separazione al coniuge superstite o a entrambi i coniugi;
{% fine %}
{% se MINORI %}
- che fra i chiamati vi sono i minori di età sopra indicati;
{% fine %}
- ☐ che fra i chiamati non vi sono persone interdette, inabilitate o beneficiarie di amministrazione di sostegno, oppure ☐ che vi sono: ______________________________.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
