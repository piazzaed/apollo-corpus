# Sentinella normativa — istruzioni per il giro automatico

Sei nel repository pubblico del corpus normativo. Il triage (JSON indicato nel prompt) contiene:
- `voci`: voci del sidecar `wiki-studio/normativa/changelog-riforme.meta.json` da riverificare (estremi, parole chiave,
  motivo: scaduta, da ricontrollare, atti cambiati o fuori corpus);
- `debito`: voci aperte e scadute del debito di verifica (`sentinella-debito.json`): cosa leggere e perché;
- `watchlist`: le voci a priorità ALTA della `vigenza-watchlist.md` (cosa monitorare e stato noto);
- `consulta`: i numeri recenti della 1ª Serie Speciale della G.U. (decisioni della Corte costituzionale), con l'indirizzo.

Per ogni voce: c'è stata una modifica, una decisione, un decreto attuativo, una proroga rispetto allo stato noto? Cerca
sulla G.U. (sommari della Serie Generale e della 1ª Serie Speciale), su normattiva (scheda dell'atto, «ultimo
aggiornamento all'atto»), sui siti istituzionali indicati nella voce. Il corpus locale (`python3 scripts/codice_locale.py
--art N --codice SLUG`) ti dice il testo che il corpus ha già.

Formato degli esiti:
```json
{"voci": {"<voce_id>": {"esito": "CONFERMATO|INVARIATO|INCONCLUSO", "sintesi": "…",
                        "prove": [{"url": "…", "estremi": ["…"], "citazione": "…"}],
                        "modificata_da": {"estremi": "L. 28/07/2026 n. 137", "vigente_da": "AAAA-MM-GG"}}},
 "debito": {"<id>": {"esito": "RISOLTO|ANCORA_APERTO|INCONCLUSO", "sintesi": "…", "prove": [ … ]}},
 "watchlist": [{"esito": "CONFERMATO", "estremi": "…", "sintesi": "…", "prove": [ … ]}],
 "nuove": [{"esito": "CONFERMATO", "titolo": "…", "estremi": "…", "sintesi": "…", "prove": [ … ]}]}
```
- CONFERMATO: la modifica c'è e la prova lo mostra (`modificata_da` obbligatorio per le voci);
- INVARIATO: la prova mostra lo stato attuale (es. la scheda normattiva con la data dell'ultimo aggiornamento, il sommario
  della G.U. senza il decreto atteso). Su una voce già «da ricontrollare» vuol dire solo «nessun atto nuovo»: la modifica
  già rilevata resta da recepire e la voce resta com'è;
- RISOLTO: solo se ciò che il debito chiede è fatto per intero. Un debito di sorveglianza («monitorare … fino al …»)
  resta ANCORA_APERTO fino al termine, anche se nel frattempo arriva una tappa (uno schema, un parere): scrivila nella
  sintesi. Se resta qualcosa da seguire, l'esito è ANCORA_APERTO;
- in `watchlist` metti solo le novità confermate; in `nuove` gli atti nuovi rilevanti per un avvocato civilista non coperti
  da alcuna voce.

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
