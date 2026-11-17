---
{
  "id": "S20",
  "titolo": "Richiesta di apertura della cassetta di sicurezza con inventario",
  "tipo_atto": "lettera",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 48 D.Lgs. 346/1990",
    "art. 130 D.Lgs. 123/2025"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S20 · Richiesta di apertura della cassetta di sicurezza con inventario

## Quando si usa

Quando il de cuius aveva una cassetta di sicurezza (o armadi, plichi, depositi chiusi: art. 48 c. 7).

- Obbligo: **obbligatorio** · firma: dichiarante · va a: banca concedente della cassetta
- Perché: dopo la morte del concessionario la cassetta si apre solo alla presenza di un funzionario dell'Agenzia o di un notaio, che fa l'inventario, previa comunicazione della banca all'ufficio (art. 48 c. 6 TUS; dal 2027 art. 130 c. 6 TU)
- Voci di DEAS che sostituisce: Richiesta sopralluogo funzionario per cassetta di sicurezza

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 48 D.Lgs. 346/1990
- art. 130 D.Lgs. 123/2025

## Note e trappole

L'inventario della cassetta va poi allegato alla dichiarazione (beni inventariati, BI).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le {{ BANCA.nome }}
>> Filiale di {{ BANCA.filiale }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — richiesta di apertura della cassetta di sicurezza con redazione dell'inventario**

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} in qualità di {{ F.qualita }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},

**CHIEDE**

che si proceda all'apertura della cassetta di sicurezza n. ________ intestata o cointestata al de cuius, alla presenza ☐ di un funzionario dell'Agenzia delle Entrate ☐ del notaio __________________________, che redigerà l'inventario del contenuto, previa comunicazione da parte di codesta banca all'ufficio dell'Agenzia delle Entrate competente del giorno e dell'ora dell'apertura {% se APERTA_DAL_2027 %}(art. 130, comma 6, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 48, comma 6, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}.

Chiede di essere avvisat{{ F.o }} della data fissata, insieme a {{ INTERMEDIARIO.nome_completo }} ({{ INTERMEDIARIO.pec }}).

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
