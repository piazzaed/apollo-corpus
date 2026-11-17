---
{
  "id": "S17",
  "titolo": "Delega degli eredi a uno di loro per i rapporti con le banche",
  "tipo_atto": "delega",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S17 · Delega degli eredi a uno di loro per i rapporti con le banche

## Quando si usa

Se gli eredi preferiscono che sia uno solo a tenere i rapporti con le banche.

- Obbligo: **facoltativo** · firma: altri_eredi · va a: banche e intermediari
- Perché: consente al dichiarante di chiedere certificazioni e informazioni e di consegnare i documenti della successione anche per conto degli altri eredi (la riscossione delle quote altrui richiede una procura)

## Normativa di riferimento (ancore lette nel corpus locale)

- (nessuna norma citata nel testo)

## Note e trappole

La delega non dà il potere di incassare le quote degli altri eredi: per quello serve una procura (di solito notarile o sul modulo della banca).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DELEGA

I sottoscritti, chiamati all'eredità{% se LEGATARI %} e legatari{% fine %} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}:
{% per E in FIRMATARI %}
- {{ E.nome_completo }}, {{ E.nato }} a {{ E.luogo_nascita }} il {{ E.data_nascita }}, codice fiscale {{ E.codice_fiscale }};
{% fine %}

**DELEGANO**

{{ DICHIARANTE.nome_completo }}, {{ DICHIARANTE.nato }} a {{ DICHIARANTE.luogo_nascita }} il {{ DICHIARANTE.data_nascita }}, codice fiscale {{ DICHIARANTE.codice_fiscale }}, a chiedere e ritirare, presso le banche, le Poste e gli altri intermediari presso cui il de cuius intratteneva rapporti, informazioni, estratti, certificazioni e documenti relativi a tali rapporti, e a consegnare la documentazione della successione, anche in loro nome.

La delega non comprende la riscossione delle somme spettanti ai deleganti.

Luogo e data: ______________________________
{% per E in FIRMATARI %}
[FIRMA: {{ E.firma_di }}]
{% fine %}

Si allegano copie dei documenti d'identità dei deleganti e del delegato.
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
