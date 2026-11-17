---
{
  "id": "S01",
  "titolo": "Incarico all'intermediario, impegno alla trasmissione telematica e autorizzazione all'addebito",
  "tipo_atto": "incarico",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 28 D.Lgs. 346/1990",
    "art. 3 D.P.R. 322/1998"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S01 · Incarico all'intermediario, impegno alla trasmissione telematica e autorizzazione all'addebito

## Quando si usa

Sempre, all'inizio della pratica: è il mandato con cui il dichiarante incarica lo studio di predisporre e trasmettere la dichiarazione. Contiene anche l'impegno dell'intermediario alla trasmissione telematica, l'autorizzazione all'addebito delle imposte sul conto indicato nella dichiarazione (firmata dal titolare del conto) e l'informativa sul trattamento dei dati.

- Obbligo: **obbligatorio** · firma: dichiarante · va a: studio (resta agli atti dell'intermediario)
- Perché: l'intermediario trasmette la dichiarazione su incarico del dichiarante, rilascia l'impegno alla trasmissione e conserva la copia sottoscritta; l'addebito delle imposte sul conto va autorizzato dal titolare
- Voci di DEAS che sostituisce: Impegno alla trasmissione telematica ed autorizzazione IBAN, Impegno alla trasmissione telematica, Delega presentazione dichiarazione (con dati delegato), Delega presentazione dichiarazione

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 28 D.Lgs. 346/1990
- art. 3 D.P.R. 322/1998

## Note e trappole

La dichiarazione si presenta con modalità telematiche ed è sottoscritta da almeno uno degli obbligati o da un suo rappresentante negoziale (art. 28, commi 1 e 3, TUS; dal 2027 art. 113 TU 123/2025). L'impegno alla trasmissione e la conservazione della copia sono obblighi dell'intermediario abilitato (art. 3 D.P.R. 322/1998).

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# CONFERIMENTO DI INCARICO ALL'INTERMEDIARIO
## per la predisposizione e la trasmissione telematica della dichiarazione di successione e domanda di volture catastali
**Successione di** {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} a {{ DEFUNTO.luogo_decesso }} il {{ DEFUNTO.data_decesso }}.

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} telefono {{ F.telefono }}, e-mail {{ F.email }}, in qualità di {{ F.qualita }} ({{ F.relazione }} del de cuius),

**CONFERISCE INCARICO**

a {{ INTERMEDIARIO.nome_completo }}, codice fiscale {{ INTERMEDIARIO.codice_fiscale }}, con studio in {{ INTERMEDIARIO.indirizzo }}, intermediario abilitato alla trasmissione telematica delle dichiarazioni, di predisporre la dichiarazione di successione e domanda di volture catastali relativa alla successione sopra indicata, sulla base dei documenti e delle informazioni forniti dal sottoscritto e dagli altri aventi diritto, e di trasmetterla in via telematica all'Agenzia delle Entrate.

A tal fine {{ F.sottoscritto | minuscolo }}:
- si impegna a fornire documenti e informazioni completi e veritieri e a comunicare senza ritardo ogni circostanza che possa modificare il contenuto della dichiarazione;
- prende atto che la dichiarazione, prima della trasmissione, gli sarà sottoposta per la verifica e la sottoscrizione, e che l'intermediario ne conserverà una copia sottoscritta;
- prende atto che la dichiarazione è sottoscritta da almeno uno degli obbligati {% se DAL_2027 %}(art. 113, comma 3, del D.Lgs. 1° agosto 2025, n. 123){% altrimenti %}(art. 28, comma 3, del D.Lgs. 31 ottobre 1990, n. 346){% fine %}.

{% se VERSAMENTO.iban %}
**ADDEBITO DELLE IMPOSTE**

{% se VERSAMENTO.conto_intermediario %}
Le imposte e i tributi da versare con la presentazione della dichiarazione sono addebitati sul conto dell'intermediario (IBAN {{ VERSAMENTO.iban }}); {{ F.sottoscritto | minuscolo }} si impegna a rimborsarne l'importo, che risulta dalla liquidazione contenuta nella dichiarazione, prima della trasmissione.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]
{% altrimenti %}
{{ VERSAMENTO.intestatario.sottoscritto }} {{ VERSAMENTO.intestatario.nome_completo }}, codice fiscale {{ VERSAMENTO.intestatario.codice_fiscale }}, titolare del conto corrente IBAN **{{ VERSAMENTO.iban }}** presso {{ VERSAMENTO.banca }}, autorizza l'intermediario a indicare il conto nella dichiarazione per l'addebito delle imposte e dei tributi da versare con la presentazione, nell'importo che risulta dalla liquidazione contenuta nella dichiarazione stessa, e si impegna a mantenere sul conto la provvista necessaria alla data della trasmissione. Prende atto che il conto deve essere intestato al dichiarante (o all'intermediario che trasmette).

Luogo e data: ______________________________
[FIRMA: {{ VERSAMENTO.intestatario.nome_completo }} (titolare del conto)]
{% fine %}
{% fine %}

**INFORMATIVA SUL TRATTAMENTO DEI DATI PERSONALI** (Regolamento (UE) 2016/679)

Titolare del trattamento è {{ INTERMEDIARIO.nome_completo }}, {{ INTERMEDIARIO.indirizzo }}, PEC {{ INTERMEDIARIO.pec }}. I dati personali del dichiarante, del de cuius e degli altri aventi diritto sono trattati, anche con strumenti informatici, per eseguire l'incarico (predisposizione e trasmissione della dichiarazione, adempimenti connessi) e per adempiere agli obblighi di legge: la base giuridica è l'esecuzione dell'incarico e l'adempimento di obblighi di legge (art. 6, paragrafo 1, lettere b) e c), del Regolamento); il loro conferimento è necessario per eseguire l'incarico. I dati sono comunicati all'Agenzia delle Entrate e, solo se necessario per l'incarico, a banche, uffici pubblici e professionisti coinvolti nella pratica, e non sono diffusi. Possono essere trattati con servizi informatici di fornitori esterni, che agiscono come responsabili del trattamento; se ciò comporta un trasferimento fuori dall'Unione europea, avviene con le garanzie previste dal Regolamento. Sono conservati per il tempo dell'incarico e, dopo, per quello previsto dalla legge per la conservazione della dichiarazione e dei documenti. L'interessato può chiedere l'accesso ai dati, la rettifica, la cancellazione, la limitazione del trattamento, la portabilità e opporsi al trattamento nei casi previsti, e può proporre reclamo al Garante per la protezione dei dati personali.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }} (dichiarante)]

[PAGINA]
# IMPEGNO ALLA TRASMISSIONE TELEMATICA
## della dichiarazione di successione e domanda di volture catastali

**Intermediario**: {{ INTERMEDIARIO.nome_completo }}, codice fiscale {{ INTERMEDIARIO.codice_fiscale }}, {{ INTERMEDIARIO.indirizzo }}.

**Dichiarante**: {{ F.nome_completo }}, codice fiscale {{ F.codice_fiscale }}.

**Successione di**: {{ DEFUNTO.nome_completo }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}.

L'intermediario sopra indicato, contestualmente all'assunzione dell'incarico per la sua predisposizione, si impegna a trasmettere la dichiarazione in via telematica all'Agenzia delle Entrate (art. 3, comma 6, del D.P.R. 22 luglio 1998, n. 322), a consegnare tempestivamente al dichiarante copia della dichiarazione trasmessa e delle ricevute e attestazioni dell'Agenzia delle Entrate, e a conservare l'originale della dichiarazione sottoscritta dal dichiarante, gli originali delle dichiarazioni sostitutive e le copie dei documenti d'identità di chi le ha sottoscritte (provvedimento del Direttore dell'Agenzia delle Entrate del 27 dicembre 2016, punti 4.4 e 6.6).

Data dell'impegno: {{ OGGI }}
[FIRMA: {{ INTERMEDIARIO.firma }} (intermediario)]
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
