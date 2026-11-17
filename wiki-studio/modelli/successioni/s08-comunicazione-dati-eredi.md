---
{
  "id": "S08",
  "titolo": "Comunicazione delle generalità e del domicilio fiscale degli eredi",
  "tipo_atto": "comunicazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 65 D.P.R. 600/1973"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S08 · Comunicazione delle generalità e del domicilio fiscale degli eredi

## Quando si usa

Sempre che ci siano eredi del contribuente: la legge dice «devono comunicare» (senza sanzione; in mancanza gli atti si notificano agli eredi impersonalmente, art. 65 c. 4). Si consegna all'ufficio o si spedisce con raccomandata con avviso di ricevimento (art. 65 c. 2), separata dalla dichiarazione.

- Obbligo: **obbligatorio** · firma: eredi · va a: Agenzia delle Entrate — ufficio del domicilio fiscale del de cuius
- Perché: gli eredi del contribuente comunicano all'ufficio del domicilio fiscale del defunto le proprie generalità e il proprio domicilio fiscale (art. 65 c. 2 D.P.R. 600/1973)
- Voci di DEAS che sostituisce: Comunicazione dei dati degli eredi

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 65 D.P.R. 600/1973

## Note e trappole

Art. 65 c. 2 D.P.R. 600/1973: «Gli eredi del contribuente devono comunicare all'ufficio delle imposte del domicilio fiscale del dante causa le proprie generalità e il proprio domicilio fiscale» (da rileggere sul corpus). Firmano tutti gli eredi. Dal 1/1/2027 l'art. 65 è abrogato dal D.Lgs. 141/2026: il ramo 2027 non cita l'articolo finché il corpus non ha la norma che lo sostituisce.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le Agenzia delle Entrate
>> {{ UFFICIO.nome }}
>> {{ UFFICIO.indirizzo }}
>> PEC {{ UFFICIO.pec }}

**Oggetto: eredi di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — comunicazione delle generalità e del domicilio fiscale{% se DAL_2027 %} degli eredi del contribuente{% altrimenti %} (art. 65, comma 2, del D.P.R. 29 settembre 1973, n. 600){% fine %}**

I sottoscritti, nella qualità di chiamati all'eredità di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} a {{ DEFUNTO.luogo_decesso }} il {{ DEFUNTO.data_decesso }}, comunicano le proprie generalità e il proprio domicilio fiscale:
{% per E in EREDI %}
- {{ E.nome_completo }}, {{ E.nato }} a {{ E.luogo_nascita }} il {{ E.data_nascita }}, codice fiscale {{ E.codice_fiscale }}, domicilio fiscale in {{ E.residenza }};
{% fine %}

Luogo e data: ______________________________
{% per E in EREDI %}
[FIRMA: {{ E.firma_di }}]
{% fine %}
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
