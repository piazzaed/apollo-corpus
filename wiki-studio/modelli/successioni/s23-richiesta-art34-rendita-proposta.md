---
{
  "id": "S23",
  "titolo": "Dichiarazione di avvalersi dell'art. 34 TUS per i fabbricati con rendita proposta",
  "tipo_atto": "dichiarazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 34 D.Lgs. 346/1990"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S23 · Dichiarazione di avvalersi dell'art. 34 TUS per i fabbricati con rendita proposta

## Quando si usa

Con fabbricati dichiarati con la rendita proposta (DOCFA non ancora definito).

- Obbligo: **obbligatorio** · firma: dichiarante · va a: Agenzia delle Entrate (allegato EG «altro»)
- Perché: il valore catastale non si rettifica, per i fabbricati con rendita proposta, solo se la volontà di avvalersene è espressa nella dichiarazione (art. 34 cc. 5, 6 e 6-bis TUS)
- Voci di DEAS che sostituisce: Richiesta ex art.34, comma 5, T.U. (rendita proposta)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 34 D.Lgs. 346/1990

## Note e trappole

Testo del modello della v0.53 (references/modelli/richiesta-art34-rendita-proposta.md), ora compilato. L'art. 34 TUS non è fra gli articoli abrogati dall'art. 204 TU 123/2025 (lett. l: «da 11 a 33, da 36 a 46») e resta vigente anche nel 2027: la scheda resta sul TUS e la sentinella la segnala se il testo cambia.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE
## (art. 34, commi 5, 6 e 6-bis, del D.Lgs. 31 ottobre 1990, n. 346) — fabbricati con rendita proposta

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} in qualità di {{ F.qualita }} nella successione di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},

**DICHIARA**

di volersi avvalere, per le seguenti unità immobiliari, oggetto di denuncia con procedura DOCFA con rendita proposta:
{% per I in FABBRICATI_RENDITA_PROPOSTA %}
- {{ I.descrizione }}{% se I.indirizzo %}, {{ I.indirizzo }}{% fine %} — denuncia DOCFA protocollo n. ____________ del ____________;
{% fine %}
della disposizione dell'art. 34, comma 6-bis, del D.Lgs. 31 ottobre 1990, n. 346, che estende a tali unità la disciplina del comma 5 (non assoggettabilità a rettifica del valore dichiarato in misura non inferiore a quello determinato su base catastale).

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
