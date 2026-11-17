---
{
  "id": "S15",
  "titolo": "Richiesta alla banca della certificazione dei rapporti alla data del decesso",
  "tipo_atto": "lettera",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 23 D.Lgs. 346/1990"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S15 · Richiesta alla banca della certificazione dei rapporti alla data del decesso

## Quando si usa

All'inizio della pratica, una per banca o intermediario (Poste comprese).

- Obbligo: **obbligatorio** · firma: dichiarante · va a: banca o intermediario (filiale presso cui erano i rapporti)
- Perché: saldi, titoli (con la quota esente dei titoli di Stato) e debiti alla data del decesso sono i dati della dichiarazione; per i debiti verso banche serve il certificato dell'art. 23 c. 2 TUS

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 23 D.Lgs. 346/1990

## Note e trappole

Art. 23 c. 2 TUS: la deduzione dei debiti verso banche e intermediari è subordinata al certificato rilasciato dall'ente entro trenta giorni dalla richiesta scritta di un obbligato alla dichiarazione, con tutti i rapporti debitori e creditori presso tutte le sedi e filiali (dal 2027 art. 108 TU 123/2025).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
>> Spett.le {{ BANCA.nome }}
>> Filiale di {{ BANCA.filiale }}

**Oggetto: successione di {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }} — richiesta di certificazione dei rapporti alla data del decesso**

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} in qualità di {{ F.qualita }} ({{ F.relazione }} del de cuius) e di soggetto obbligato alla dichiarazione di successione,

**CHIEDE**

il rilascio di una certificazione, riferita alla data del decesso, di tutti i rapporti intestati o cointestati al de cuius presso ogni sede, agenzia e filiale, con l'indicazione per ciascuno di:
- numero e tipo del rapporto, intestatari e quota del de cuius;
- saldo contabile alla data del decesso, compresi gli interessi maturati e non ancora accreditati;
- titoli e strumenti finanziari in deposito (codice ISIN, quantità, valore alla data del decesso), distinguendo i titoli di Stato e gli altri titoli esenti e, per i fondi, la quota investita in titoli di Stato;
- buoni fruttiferi, polizze e prodotti assicurativi collocati, con l'indicazione dei beneficiari designati;
- cassette di sicurezza o depositi chiusi;
- debiti del de cuius alla data del decesso (mutui, finanziamenti, saldi passivi, garanzie prestate anche per terzi), con la certificazione prevista dall'{% se APERTA_DAL_2027 %}art. 108, comma 2, del D.Lgs. 1° agosto 2025, n. 123{% altrimenti %}art. 23, comma 2, del D.Lgs. 31 ottobre 1990, n. 346{% fine %} per i debiti verso banche e intermediari finanziari e, per i saldi passivi dei conti correnti, l'integrale svolgimento del conto dal dodicesimo mese anteriore al decesso o, se precedente, dall'ultimo saldo attivo.

Rapporti già noti:
{% per R in BANCA.rapporti %}
- {{ R }};
{% fine %}

Si allegano la dichiarazione sostitutiva di certificazione di morte, la dichiarazione sostitutiva degli eredi e copia del documento d'identità del richiedente. La certificazione può essere inviata a {{ INTERMEDIARIO.nome_completo }}, {{ INTERMEDIARIO.indirizzo }}, PEC {{ INTERMEDIARIO.pec }}.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
