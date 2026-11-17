---
{
  "id": "S12",
  "titolo": "Dichiarazione di accettazione dell'eredità (art. 475 c.c.)",
  "tipo_atto": "dichiarazione",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 475 c.c.",
    "art. 2648 c.c.",
    "art. 471 c.c.",
    "art. 472 c.c.",
    "art. 490 c.c.",
    "art. 649 c.c."
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S12 · Dichiarazione di accettazione dell'eredità (art. 475 c.c.)

## Quando si usa

Solo su richiesta (--solo S12): quando un erede vuole accettare in modo espresso (ad esempio per una banca). La firmano solo i chiamati: non i legatari (il legato si acquista senza accettazione, art. 649 c.c.), non i minori, gli interdetti, i minori emancipati e gli inabilitati (solo col beneficio d'inventario, artt. 471-472 c.c.). Con l'accettazione pura e semplice l'erede risponde dei debiti ereditari anche oltre il valore dei beni (art. 490 c.c., a contrario). Per la trascrizione serve il notaio.

- Obbligo: **facoltativo** · firma: chiamati_maggiorenni · va a: agli atti degli eredi (e della banca, se la chiede)
- Perché: accettazione espressa per scrittura privata (art. 475 c.c.); NON basta per la trascrizione (art. 2648 c.c. chiede atto pubblico o scrittura autenticata)
- Voci di DEAS che sostituisce: Accettazione dell'eredità

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 475 c.c.
- art. 2648 c.c.
- art. 471 c.c.
- art. 472 c.c.
- art. 490 c.c.
- art. 649 c.c.

## Note e trappole

Art. 475 c.c.: l'accettazione è espressa quando, in un atto pubblico o in una scrittura privata, il chiamato dichiara di accettare o assume il titolo di erede; è nulla sotto condizione, a termine o parziale. Art. 2648 c.c.: la trascrizione si fa su atto pubblico o scrittura privata autenticata o accertata giudizialmente.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# DICHIARAZIONE DI ACCETTAZIONE DELL'EREDITÀ
## (art. 475 del codice civile)

I sottoscritti, chiamati all'eredità di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} a {{ DEFUNTO.luogo_decesso }} il {{ DEFUNTO.data_decesso }}:
{% per E in FIRMATARI %}
- {{ E.nome_completo }}, {{ E.nato }} a {{ E.luogo_nascita }} il {{ E.data_nascita }}, codice fiscale {{ E.codice_fiscale }}, residente in {{ E.residenza }};
{% fine %}

**DICHIARANO**

di accettare puramente e semplicemente l'eredità del de cuius, ciascuno per la propria quota{% se TESTAMENTO %}, come determinata dal testamento{% altrimenti %}, come determinata dalla legge{% fine %}, assumendo il titolo di erede, consapevoli che con l'accettazione pura e semplice rispondono dei debiti ereditari anche oltre il valore dei beni ricevuti.

Luogo e data: ______________________________
{% per E in FIRMATARI %}
[FIRMA: {{ E.firma_di }}]
{% fine %}
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
