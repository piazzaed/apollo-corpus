# Sentinella dei dati periodici — istruzioni per il giro automatico

Sei nel repository pubblico del corpus normativo. I tassi li aggiornano gli script; a te restano le serie per cui lo
script non sa trovare la pagina. Il triage (JSON indicato nel prompt) può contenere:
- `foi`: gli indici ISTAT FOI senza tabacchi mancanti (mesi dopo `dopo`, fino a `fino_a`, base corrente);
- `bot12`: il rendimento medio ponderato delle aste dei BOT a 12 mesi dopo la data `dopo`.

Formato degli esiti:
```json
{"foi": [{"mese": "AAAA-MM", "indice": 103.9, "prova": {"url": "…", "estremi": ["…"], "citazione": "…"}}],
 "bot12": [{"asta": "AAAA-MM-GG", "rendimento": 2.981, "prova": {"url": "…", "estremi": ["…"], "citazione": "…"}}]}
```
Il numero deve comparire nella pagina della prova **scritto come lo scrive la fonte** (virgola decimale): lo script lo
cerca, insieme al nome del mese per il FOI, e scarta i valori che si discostano troppo dalla serie.

## Regole che valgono sempre

1. **Non scrivere nel repository** (salvo, per i modelli, le schede elencate nel triage). Il tuo prodotto è il file degli
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
