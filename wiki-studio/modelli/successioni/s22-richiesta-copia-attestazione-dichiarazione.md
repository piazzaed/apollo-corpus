---
{
  "id": "S22",
  "titolo": "Richiesta di copia della dichiarazione di successione o dell'attestazione di presentazione",
  "tipo_atto": "istanza",
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

# S22 · Richiesta di copia della dichiarazione di successione o dell'attestazione di presentazione

## Quando si usa

Solo su richiesta (--solo S22), dopo la presentazione: se la copia conforme non è stata chiesta nella dichiarazione (casella «copia conforme») o ne serve un'altra. Per i Modelli 4 cartacei: certificato modello 240.

- Obbligo: **dopo la presentazione** · firma: dichiarante · va a: Agenzia delle Entrate — ufficio competente
- Perché: l'attestazione di avvenuta presentazione serve per svincolare conti e titoli (se non è stata chiesta nella dichiarazione); per le successioni presentate col Modello 4 il certificato è il modello 240
- Voci di DEAS che sostituisce: Richiesta copia dichiarazione di successione, Richiesta copia conforme dichiarazione di successione, Richiesta Modello 240, Richiesta Modello 240 (AdE), Richiesta Modello 240 (con delega)

## Normativa di riferimento (ancore lette nel corpus locale)

- (nessuna norma citata nel testo)

## Note e trappole

Pagina AdE «Come presentare»: l'attestazione è «utile, ad esempio, per svincolare conti correnti oppure titoli»; le FAQ: «l'attestazione elettronica è utilizzabile una sola volta». Il modello 240 è il certificato di avvenuta presentazione delle dichiarazioni cartacee (guida AdE «I servizi agili», 2022).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le Agenzia delle Entrate
>> {{ UFFICIO.nome }}
>> {{ UFFICIO.indirizzo }}
>> PEC {{ UFFICIO.pec }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — richiesta di copia della dichiarazione**

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} in qualità di {{ F.qualita }} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }},

**CHIEDE**

con riferimento alla dichiarazione di successione presentata il {{ PRESENTAZIONE.data }} (protocollo {{ PRESENTAZIONE.protocollo }}), il rilascio di (barrare):
- ☐ copia semplice della dichiarazione;
- ☐ copia conforme / attestazione di avvenuta presentazione, n. ____ esemplari;
- ☐ certificato di avvenuta presentazione (modello 240), per la dichiarazione presentata su Modello 4.

☐ Delega al ritiro {{ INTERMEDIARIO.nome_completo }}, codice fiscale {{ INTERMEDIARIO.codice_fiscale }}.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del richiedente.
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
