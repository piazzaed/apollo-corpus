---
{
  "id": "S18",
  "titolo": "Dichiarazione di esonero dall'obbligo della dichiarazione di successione (per la banca)",
  "tipo_atto": "dichiarazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 28 D.Lgs. 346/1990",
    "art. 48 D.Lgs. 346/1990",
    "art. 113 D.Lgs. 123/2025",
    "art. 130 D.Lgs. 123/2025"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S18 · Dichiarazione di esonero dall'obbligo della dichiarazione di successione (per la banca)

## Quando si usa

Solo se gli eredi sono coniuge e parenti in linea retta, non ci sono immobili o diritti reali immobiliari e l'attivo non supera 100.000 euro, e si decide di non presentare la dichiarazione. Con sopravvenienze che fanno venir meno le condizioni l'obbligo rinasce.

- Obbligo: **facoltativo** · firma: eredi_maggiorenni · va a: banca, Poste o altro debitore del defunto
- Perché: senza obbligo di dichiarazione (art. 28 c. 7 TUS) la banca può pagare se l'interessato dichiara per iscritto che l'obbligo non c'era (art. 48 cc. 3-4 TUS); la banca la trasmette all'Agenzia entro 15 giorni (c. 5)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 28 D.Lgs. 346/1990
- art. 48 D.Lgs. 346/1990
- art. 113 D.Lgs. 123/2025
- art. 130 D.Lgs. 123/2025

## Note e trappole

Art. 28 c. 7 TUS (dal 2027 art. 113 c. 8 TU 123/2025) e art. 48 cc. 3, 4 e 5 TUS (dal 2027 art. 130 cc. 2, 3 e 5 TU).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le {{ BANCA.nome }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — dichiarazione di inesistenza dell'obbligo di presentare la dichiarazione di successione**

I sottoscritti, chiamati all'eredità di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}:
{% per E in FIRMATARI %}
- {{ E.nome_completo }}, codice fiscale {{ E.codice_fiscale }}, {{ E.relazione }} del de cuius;
{% fine %}
consapevoli delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, ai sensi dell'art. 47 del medesimo decreto

**DICHIARANO**

che non vi è obbligo di presentare la dichiarazione di successione {% se APERTA_DAL_2027 %}(art. 113, comma 8, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 28, comma 7, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}, perché l'eredità è devoluta al coniuge e ai parenti in linea retta del defunto, l'attivo ereditario ha un valore non superiore a euro centomila e non comprende beni immobili o diritti reali immobiliari; e si impegnano a presentarla se, per effetto di sopravvenienze ereditarie, queste condizioni venissero a mancare.

Chiedono pertanto il pagamento delle somme e la consegna dei beni del de cuius secondo le rispettive quote {% se APERTA_DAL_2027 %}(art. 130, commi 2, 3 e 5, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 48, commi 3, 4 e 5, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}.

Luogo e data: ______________________________
{% per E in FIRMATARI %}
[FIRMA: {{ E.firma_di }}]
{% fine %}

Si allegano copie dei documenti d'identità dei sottoscrittori.
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
