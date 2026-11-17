---
{
  "id": "S19",
  "titolo": "Richiesta di svincolo per il pagamento delle imposte (unico erede fino a 26 anni)",
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

# S19 · Richiesta di svincolo per il pagamento delle imposte (unico erede fino a 26 anni)

## Quando si usa

Solo con un unico erede di età non superiore a 26 anni e immobili nell'asse, per le successioni aperte dal 1/1/2025 (il comma 4-bis l'ha introdotto il D.Lgs. 139/2024).

- Obbligo: **facoltativo** · firma: dichiarante · va a: banca o intermediario
- Perché: con immobili nell'asse l'unico erede fino a 26 anni può ottenere lo svincolo prima della dichiarazione, nei limiti delle imposte ipotecaria, catastale e di bollo (art. 48 c. 4-bis TUS; dal 2027 art. 130 c. 4 TU)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 48 D.Lgs. 346/1990
- art. 130 D.Lgs. 123/2025

## Note e trappole

Art. 48 c. 4-bis TUS: le modalità attuative sono stabilite con provvedimento del direttore dell'Agenzia: verificarlo prima dell'invio.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le {{ BANCA.nome }}
>> Filiale di {{ BANCA.filiale }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — richiesta di svincolo per il pagamento delle imposte ipotecaria, catastale e di bollo**

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} unic{{ F.o }} erede di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}, di età non superiore a ventisei anni,

premesso che nell'asse ereditario sono compresi beni immobili,

**CHIEDE**

{% se APERTA_DAL_2027 %}ai sensi dell'art. 130, comma 4, del D.Lgs. 1° agosto 2025, n. 123{% altrimenti %}ai sensi dell'art. 48, comma 4-bis, del D.Lgs. 31 ottobre 1990, n. 346{% fine %}, lo svincolo, anche prima della presentazione della dichiarazione di successione, delle attività cadute in successione presso codesta banca nei limiti delle somme dovute per il versamento delle imposte ipotecaria, catastale e di bollo, pari a euro ______________, da versare per la dichiarazione di successione.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
