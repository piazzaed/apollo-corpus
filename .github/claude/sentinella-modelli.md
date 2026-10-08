# Sentinella dei modelli d'atto — istruzioni per il giro automatico

Sei nel repository pubblico del corpus normativo. Il triage (JSON indicato nel prompt) elenca le schede dei modelli d'atto
(`wiki-studio/modelli/civile/*.md`) che il controllo deterministico ha trovato rosse: per ognuna i problemi (norma abrogata
o modificata, requisito mancante, formula superata, cifra non aggiornata) con la correzione suggerita quando c'è.

Correggi **solo quelle schede** (Edit), e **solo** nelle sezioni «Testo del modello», «Normativa» e «Aggiornamenti»:
- il frontmatter e le altre sezioni restano identici;
- ogni norma che scrivi deve esistere nel corpus alla versione vigente: leggila con
  `python3 scripts/codice_locale.py --art N --codice SLUG` prima di citarla;
- nessuna sentenza, nessun nome di persona o di studio, nessun dato personale (i segnaposto restano segnaposto);
- aggiungi in «Aggiornamenti» una riga datata con cosa hai cambiato e perché;
- verifica la scheda con `python3 scripts/sentinella_modelli.py --giro --id ID --senza-motori --senza-patch`: deve
  tornare VERDE. Se non riesci, lascia la scheda com'era.

Formato degli esiti:
```json
{"modelli": {"<id>": {"esito": "CORRETTO|NON_CORRETTO", "sintesi": "…"}}}
```
Il controllo meccanico rifà il giro sulla scheda e la respinge se tocchi altro o se non torna verde.

## Regole che valgono sempre

1. **Scrivi solo le schede elencate nel triage.** Il tuo prodotto è il file degli
   esiti indicato nel prompt: JSON valido, nel formato qui sotto. Uno script lo controlla e applica solo ciò che supera il
   controllo; il resto lo ignora e apre una issue.
2. **Ogni esito si regge su una PROVA**: `{"url": "https://…", "estremi": ["…"], "citazione": "…"}`.
   - `url`: una pagina **ufficiale** (Gazzetta Ufficiale, normattiva, EUR-Lex, MEF, Agenzia delle Entrate, Ministero della
     giustizia, CNF, Banca d'Italia, ISTAT, BCE, INPS, INAIL, Corte costituzionale, Corte di cassazione, Camera, Senato, Geo
     Network per il DEAS). Mai blog, riviste, studi professionali, aggregatori;
   - `estremi`: le stringhe che identificano l'atto (numero, data, codice redazionale), **scritte come compaiono sulla
     pagina**;
   - `citazione`: almeno 40 caratteri **copiati alla lettera** dalla pagina, che dicono ciò che affermi.
   Lo script riscarica la pagina e deve ritrovare estremi e citazione. Prima di consegnare provala tu:
   `python3 scripts/sentinelle_prove.py --prova --url URL --estremi "…" "…" --citazione "…"`.
3. **Prudenza**: se una fonte non si apre o è ambigua, l'esito è INCONCLUSO, con il motivo. Mai un numero, una data o un
   estremo a memoria. Meglio un INCONCLUSO in più che una notizia sbagliata pubblicata.
4. Lavora fino in fondo: nessun limite di ricerche, ma niente ripetizioni inutili.
5. Italiano, sintesi brevi (una o due frasi), senza nomi di persone o di studi professionali.
