---
{
  "id": "S16",
  "titolo": "Richiesta alla banca di svincolo e liquidazione dei rapporti agli eredi",
  "tipo_atto": "lettera",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 48 D.Lgs. 346/1990",
    "art. 130 D.Lgs. 123/2025",
    "art. 320 c.c."
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S16 · Richiesta alla banca di svincolo e liquidazione dei rapporti agli eredi

## Quando si usa

Dopo la presentazione, una per banca: la firmano tutti gli eredi. Gli IBAN e le quote si scrivono a mano (o li compila lo studio) se la pratica non li ha.

- Obbligo: **dopo la presentazione** · firma: eredi · va a: banca o intermediario
- Perché: la banca può pagare o trasferire i rapporti agli eredi solo con la prova della presentazione della dichiarazione che li indica (art. 48 cc. 3 e 4 TUS; dal 2027 art. 130 cc. 2 e 3 TU 123/2025)

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 48 D.Lgs. 346/1990
- art. 130 D.Lgs. 123/2025
- art. 320 c.c.

## Note e trappole

Art. 48 c. 3-4 TUS: debitori del defunto, banche ed emittenti non pagano né annotano trasferimenti senza la prova della presentazione della dichiarazione con l'indicazione dei beni (o la dichiarazione scritta che non c'era obbligo). Per i minori i capitali non si riscuotono senza autorizzazione del giudice tutelare (art. 320 c.c.).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le {{ BANCA.nome }}
>> Filiale di {{ BANCA.filiale }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }} — richiesta di svincolo e liquidazione dei rapporti agli eredi**

I sottoscritti, chiamati all'eredità{% se LEGATARI %} e legatari{% fine %} di {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}:
{% per E in FIRMATARI %}
- {{ E.nome_completo }}, codice fiscale {{ E.codice_fiscale }}, residente in {{ E.residenza }};
{% fine %}

premesso che la dichiarazione di successione, con l'indicazione dei rapporti in essere presso codesta banca, è stata presentata in via telematica il {{ PRESENTAZIONE.data }} (protocollo {{ PRESENTAZIONE.protocollo }}), come risulta dalla ricevuta allegata {% se APERTA_DAL_2027 %}(art. 130, commi 2 e 3, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 48, commi 3 e 4, del D.Lgs. 31 ottobre 1990, n. 346){% fine %},

**CHIEDONO**

lo svincolo dei rapporti intestati o cointestati al de cuius:
{% per R in BANCA.rapporti %}
- {{ R }};
{% fine %}
e la liquidazione delle somme e il trasferimento dei titoli a ciascun avente diritto secondo la propria quota o il proprio legato, sui conti indicati:
{% per E in FIRMATARI %}
- {{ E.nome_completo }}: quota ____________ — IBAN ___________________________________;
{% fine %}
{% se MINORI %}
Per la quota dei minori si allega l'autorizzazione del giudice tutelare alla riscossione (art. 320 del codice civile).
{% fine %}

Si allegano: copia della dichiarazione di successione e della ricevuta di presentazione (o l'attestazione di avvenuta presentazione), dichiarazione sostitutiva degli eredi{% se TESTAMENTO %}, copia del testamento e del verbale di pubblicazione{% fine %}, copie dei documenti d'identità e dei codici fiscali.

Luogo e data: ______________________________
{% per E in FIRMATARI %}
[FIRMA: {{ E.firma_di }}]
{% fine %}
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
