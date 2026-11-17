---
{
  "id": "S07",
  "titolo": "Richiesta delle agevolazioni «prima casa» (eredi diversi dal dichiarante)",
  "tipo_atto": "dichiarazione_sostitutiva",
  "rito": "n/a",
  "fase": "successione",
  "materia": "successioni",
  "changelog_deps": [],
  "volatilita": "media",
  "ambito": "successioni",
  "norme_chiave": [
    "art. 69 L. 342/2000",
    "art. 46 D.P.R. 445/2000",
    "art. 47 D.P.R. 445/2000"
  ],
  "fonte": "Studio — testi propri (v0.55); norme lette nel corpus locale; prima casa dal quadro EH del modello AdE (provv. 13/02/2025)",
  "data_formulario": "2026-11",
  "verificato_il": "2026-11-17",
  "prossima_verifica": "2027-05-17",
  "stato": "attivo"
}
---

# S07 · Richiesta delle agevolazioni «prima casa» (eredi diversi dal dichiarante)

## Quando si usa

Per ogni erede, legatario o coniuge titolare del diritto di abitazione che chiede la prima casa e NON è il dichiarante (per il dichiarante la richiesta sta nel quadro EH, Sezione II), e anche per il dichiarante quando chiede la pertinenza da sola (codice Y) o l'immobile contiguo senza l'abitazione principale (codice Z): le istruzioni AdE (Fascicolo 1) chiedono sempre la dichiarazione sostitutiva in EG9. Le caselle si barrano a mano: sono le dichiarazioni a)-i) della Sezione II del quadro EH del modello AdE, più j) e k) per i codici Y e Z.

- Obbligo: **obbligatorio** · firma: voce · va a: Agenzia delle Entrate (allegato EG9 «prima casa»)
- Perché: chi chiede la prima casa e non è il dichiarante rende la sua richiesta a parte, allegata nel rigo EG9 con il documento d'identità (istruzioni AdE, Fascicolo 1): il quadro EH vale solo per il dichiarante
- Voci di DEAS che sostituisce: Dichiarazione Prima Casa (dal 1-1-2014), Dichiarazione Prima Casa (fino al 31-12-2013), Richiesta agevolazione fiscale "prima casa", (Regione Umbria) Dichiarazione Prima Casa

## Normativa di riferimento (ancore lette nel corpus locale)

- art. 69 L. 342/2000
- art. 46 D.P.R. 445/2000
- art. 47 D.P.R. 445/2000

## Note e trappole

Testo delle dichiarazioni ricalcato sul quadro EH, Sezione II, del modello approvato con provvedimento 13/02/2025 (art. 69 c. 3 L. 342/2000: imposte ipotecaria e catastale in misura fissa). Le istruzioni (Fascicolo 1, p. 50) chiedono che la richiesta del beneficiario diverso dal dichiarante sia resa ai sensi degli artt. 46 e 47 D.P.R. 445/2000 e allegata in EG9 con il documento d'identità. L'impegno a cedere l'altra casa entro due anni (lett. d) vale per i decessi dal 1/1/2025; prima, il termine della norma dell'epoca va verificato. Art. 69 c. 4 L. 342/2000: le dichiarazioni sono rese dall'interessato nella dichiarazione di successione. Codici Y e Z: estremi dell'atto di acquisto della casa principale, dati catastali, volontà di costituire il vincolo pertinenziale, nessun'altra pertinenza della stessa categoria (o impegno a cederla entro due anni) — istruzioni AdE, Fascicolo 1. Dal 1/1/2027 l'art. 69 cc. 3-4 è abrogato (art. 204 TU 123/2025) e la regola passa nel testo unico: finché il corpus non ha la tariffa del TU, il ramo 2027 non cita l'articolo.

## Testo del modello (lingua di scripts/suc_modelli_testo.py)
```
# RICHIESTA DELLE AGEVOLAZIONI «PRIMA CASA»
## da allegare alla dichiarazione di successione (quadro EG, rigo EG9) — artt. 46 e 47 del D.P.R. 28 dicembre 2000, n. 445

**Successione di** {{ DEFUNTO.nome_completo }}, {{ DEFUNTO.nato }} a {{ DEFUNTO.luogo_nascita }} il {{ DEFUNTO.data_nascita }}, codice fiscale {{ DEFUNTO.codice_fiscale }}, con ultima residenza in {{ DEFUNTO.residenza }}, {{ DEFUNTO.deceduto }} il {{ DEFUNTO.data_decesso }}.

{% se F.minore %}I sottoscritti ______________________________, genitore o genitori esercenti la responsabilità genitoriale su {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, codice fiscale {{ F.codice_fiscale }}, minore di età, in nome e per conto del minore (art. 5 del D.P.R. 28 dicembre 2000, n. 445),{% altrimenti %}{{ F.sottoscritto }} {{ F.nome_completo }}, {{ F.nato }} a {{ F.luogo_nascita }} il {{ F.data_nascita }}, residente in {{ F.residenza }}, codice fiscale {{ F.codice_fiscale }},{% fine %} {% se F.abitazione %}coniuge superstite titolare del diritto di abitazione sulla casa adibita a residenza familiare{% altrimenti %}{{ F.relazione }} del de cuius e beneficiari{{ F.o }} della successione{% fine %},
{% se F.minore %}consapevoli{% altrimenti %}consapevole{% fine %} delle sanzioni penali previste dall'art. 76 del D.P.R. 28 dicembre 2000, n. 445, per le ipotesi di falsità in atti e di dichiarazioni mendaci, e della decadenza dai benefici prevista dall'art. 75 del medesimo decreto,

**CHIEDE**

di avvalersi, per gli immobili sotto indicati, dell'agevolazione fiscale {% se DAL_2027 %}«prima casa» per i trasferimenti a causa di morte{% altrimenti %}prevista dall'art. 69, comma 3, della legge 21 novembre 2000, n. 342{% fine %}, consistente nell'applicazione delle imposte ipotecaria e catastale in misura fissa:
{% per I in F.IMMOBILI %}
- immobile principale: {{ I.descrizione }}{% se I.indirizzo %}, {{ I.indirizzo }}{% fine %};
{% fine %}
{% per I in F.PERTINENZE %}
- pertinenza: {{ I.descrizione }}{% se I.indirizzo %}, {{ I.indirizzo }}{% fine %};
{% fine %}

e a tal fine **DICHIARA** (barrare le caselle che ricorrono):

a) ☐ che l'unità immobiliare (le unità immobiliari) per cui chiede l'agevolazione è situata nello stesso comune in cui risiede;
   ☐ che è situata nello stesso comune in cui svolge abitualmente la propria attività;
   ☐ che è sua intenzione stabilire la residenza entro diciotto mesi dall'apertura della successione nel comune di ubicazione dell'immobile;
b) ☐ di non essere titolare esclusivo o in comunione con il coniuge di diritti di proprietà, usufrutto, uso e abitazione di altra casa di abitazione nel territorio del comune in cui è situato l'immobile;
c) ☐ di non essere titolare, neppure per quote, anche in regime di comunione legale, su tutto il territorio nazionale, dei diritti di proprietà, usufrutto, uso, abitazione e nuda proprietà su altra casa di abitazione acquistata da sé o dal coniuge con le agevolazioni sull'acquisto della prima casa;
{% se DECESSO_DAL_2025 %}
d) ☐ di essere titolare, su tutto il territorio nazionale, dei diritti di proprietà, usufrutto, uso, abitazione o nuda proprietà su altra casa di abitazione acquistata con le agevolazioni sull'acquisto della prima casa e di impegnarsi al trasferimento della stessa entro due anni dal decesso;
{% altrimenti %}
d) ☐ di essere titolare, su tutto il territorio nazionale, dei diritti di proprietà, usufrutto, uso, abitazione o nuda proprietà su altra casa di abitazione acquistata con le agevolazioni sull'acquisto della prima casa e di impegnarsi al trasferimento della stessa entro il termine previsto dalla norma vigente alla data del decesso;
{% fine %}
e) ☐ che l'immobile rientra fra le case di abitazione non di lusso (categorie catastali diverse da A/1, A/8 e A/9);
{% se DECESSO_DAL_14_06_2023 %}
f) ☐ di essersi trasferit{{ F.o }} all'estero per motivi di lavoro, che il trasferimento è avvenuto prima dell'acquisto dell'immobile, di aver risieduto o svolto attività di lavoro in Italia per almeno cinque anni prima dell'acquisto e che l'unità immobiliare si trova nel comune di nascita o in quello in cui aveva la residenza o svolgeva la propria attività prima del trasferimento;
{% altrimenti %}
f) ☐ di essersi trasferit{{ F.o }} all'estero per motivi di lavoro e che l'unità immobiliare è situata nello stesso comune in cui ha sede o esercita l'attività il soggetto alle cui dipendenze lavora;
{% fine %}
g) ☐ di essere cittadin{{ F.o }} italian{{ F.o }} residente all'estero;
h) ☐ di far parte del personale in servizio permanente appartenente alle Forze armate o alle Forze di polizia;
i) ☐ di impegnarsi a unire catastalmente gli immobili contigui, entro tre anni dalla presentazione della dichiarazione, per costituire un'unica unità abitativa.
{% se F.cod_Y %}
j) (pertinenza senza l'abitazione principale, codice Y) che l'immobile indicato come pertinenza è destinato a pertinenza della casa di abitazione, non compresa nella successione, già di sua titolarità e acquistata con le agevolazioni «prima casa» con atto ______________________ del ____________, censita ______________________ (altre pertinenze già collegate: ______________________); ☐ di non essere titolare di altra pertinenza della stessa categoria catastale acquistata con le agevolazioni, oppure ☐ di impegnarsi a trasferirla entro due anni dall'apertura della successione; ☐ di voler destinare l'immobile a pertinenza della casa sopra indicata (se il vincolo non risulta già da un atto precedente);
{% fine %}
{% se F.cod_Z %}
k) (immobile contiguo senza l'abitazione principale, codice Z) che l'immobile è contiguo alla casa di abitazione, non compresa nella successione, acquistata con le agevolazioni «prima casa» con atto ______________________ del ____________, censita ______________________, alla quale sarà unito catastalmente;
{% fine %}

Si impegna a rendere le ulteriori dichiarazioni e a produrre i documenti che l'ufficio richiederà per la verifica dei requisiti.

Chi firma dichiara di aver preso visione dell'informativa sul trattamento dei dati personali ai sensi dell'art. 13 del Regolamento (UE) 2016/679.

Luogo e data: ______________________________
[FIRMA: {{ F.firma_di }}]

Si allega copia fotostatica non autenticata di un documento di identità in corso di validità del sottoscrittore (art. 38, comma 3, del D.P.R. 28 dicembre 2000, n. 445).
```

## Aggiornamenti

- 2026-11-17: prima stesura (v0.55), sostituisce la «Composizione documenti» di DEAS.
