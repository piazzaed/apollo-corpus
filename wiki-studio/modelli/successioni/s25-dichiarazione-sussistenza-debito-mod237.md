---
{
  "id": "S25",
  "titolo": "Dichiarazione di sussistenza di debito (conforme al Mod. 237)",
  "tipo_atto": "dichiarazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 21 D.Lgs. 346/1990",
    "art. 23 D.Lgs. 346/1990",
    "art. 108 D.Lgs. 123/2025"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S25 · Dichiarazione di sussistenza di debito (conforme al Mod. 237)

## Quando si usa

Per i debiti che risultano da atto scritto di data certa anteriore all'apertura o da provvedimento giurisdizionale definitivo (art. 21 c. 1 TUS), quando i documenti dell'art. 23 cc. 1-2 non ne provano la sussistenza alla data della morte: «altre passività» (codice 12). Non per le spese mediche e funerarie (fatture) né per i debiti verso banche (certificato dell'art. 23 c. 2). Le firme vanno autenticate; per i debiti verso i dipendenti non firma il creditore.

- Obbligo: **consigliato** · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG5 «passività»)
- Perché: un debito che non risulta da titolo, scritture o certificato bancario si dimostra con l'attestazione conforme al modello approvato, firmata da un obbligato e dal creditore, con firme autenticate (art. 23 c. 3 TUS)
- Voci di DEAS che sostituisce: Dichiarazione di sussistenza di debito (mod.237)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 21 D.Lgs. 346/1990
- art. 23 D.Lgs. 346/1990
- art. 108 D.Lgs. 123/2025

## Note e trappole

Ricalca il Mod. 237 (Modulario Entrate-011, provvedimenti pubblicati sul suppl. 37 alla G.U. n. 53 del 4/3/2002), ancora pubblicato sul sito AdE e richiamato dalle istruzioni (rigo EG5). Il richiamo alla sanzione del vecchio art. 51 TUS non si riporta: le misure sono cambiate.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le Agenzia delle Entrate
>> {{ UFFICIO.nome }}

# DICHIARAZIONE DI SUSSISTENZA DI DEBITO
## agli effetti dell'{% se APERTA_DAL_2027 %}art. 108, comma 3, del D.Lgs. 1° agosto 2025, n. 123{% altrimenti %}art. 23, comma 3, del D.Lgs. 31 ottobre 1990, n. 346{% fine %} (conforme al Mod. 237)

I sottoscritti dichiarano che il {{ DEFUNTO.data_decesso }}, giorno della morte di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, sussisteva il debito certo e liquido del defunto per l'importo di {{ D.importo }} (in lettere: ________________________________), dipendente da (causa del credito e titoli costitutivi, con le ragioni delle eventuali variazioni dell'importo originario):

{{ D.descrizione }}

______________________________________________________________

Luogo e data: ______________________________

L'erede o gli eredi:
[FIRMA: {{ F.firma_di }}]

Il creditore o i creditori:
[FIRMA: {{ D.creditore }}]

Le firme devono essere autenticate ({% se APERTA_DAL_2027 %}art. 108, comma 3, del D.Lgs. 1° agosto 2025, n. 123{% altrimenti %}art. 23, comma 3, del D.Lgs. 31 ottobre 1990, n. 346{% fine %}).

Visto per l'autenticità delle firme: ______________________________
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
