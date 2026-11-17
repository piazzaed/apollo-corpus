---
{
  "id": "S11",
  "titolo": "Richiesta del certificato di destinazione urbanistica",
  "tipo_atto": "istanza",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 30 D.P.R. 380/2001",
    "art. 34 D.Lgs. 346/1990"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S11 · Richiesta del certificato di destinazione urbanistica

## Quando si usa

Con terreni nell'asse, uno per Comune. Imposta di bollo e diritti di segreteria secondo le indicazioni del Comune.

- Obbligo: **facoltativo** · firma: dichiarante · va a: Comune in cui si trovano i terreni (ufficio urbanistica)
- Perché: il certificato attesta se i terreni hanno destinazione edificatoria, che esclude il valore catastale (art. 34 c. 5 TUS); il Comune lo rilascia entro trenta giorni (art. 30 c. 3 D.P.R. 380/2001)
- Voci di DEAS che sostituisce: Richiesta Certificato di Destinazione Urbanistica

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 30 D.P.R. 380/2001
- art. 34 D.Lgs. 346/1990

## Note e trappole

Art. 30 c. 3 D.P.R. 380/2001: il certificato è rilasciato dal competente ufficio comunale entro il termine perentorio di trenta giorni dalla domanda.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Al Comune di {{ C.nome }}
>> Ufficio urbanistica

**Oggetto: richiesta di certificato di destinazione urbanistica (art. 30, comma 3, del D.P.R. 6 giugno 2001, n. 380)**

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} telefono {{ F.telefono }}, e-mail {{ F.email }}, in qualità di {{ F.qualita }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},

**CHIEDE**

il rilascio del certificato di destinazione urbanistica dei seguenti terreni, da produrre ai fini della dichiarazione di successione:
{% per T in C.TERRENI %}
- {{ T.descrizione }};
{% fine %}

Allega copia del proprio documento d'identità e l'estratto di mappa o la visura dei terreni.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
