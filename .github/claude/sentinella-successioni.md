# Sentinella delle successioni — istruzioni per il giro automatico

Sei nel repository pubblico del corpus normativo. Il triage (JSON indicato nel prompt) contiene i segnali delle sonde
(release DEAS nuove, decreti in G.U., articoli cambiati nel corpus) e l'elenco di ciò che va cercato: provvedimenti del
Direttore dell'Agenzia delle Entrate sul modello di dichiarazione di successione, specifiche tecniche SUC13 e modulo di
controllo, circolari e risoluzioni in materia di imposta di successione e donazione, contenuto delle release DEAS nuove.
Lo stato noto è in `skills/assistente-successioni/references/changelog-normativo.md`: leggilo prima di cercare.

Formato degli esiti:
```json
{"novita": [{"titolo": "…", "estremi": "Provv. AdE … n. …", "sintesi": "…", "tocca_calcoli": false,
             "prove": [{"url": "…", "estremi": ["…"], "citazione": "…"}]}]}
```
- elenca solo le novità **rispetto allo stato noto** e provate; se non ce ne sono, `{"novita": []}`;
- `tocca_calcoli: true` se la novità cambia aliquote, franchigie, importi, coefficienti o tassi usati nei calcoli
  (le costanti non si cambiano in automatico: si apre una issue).

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
