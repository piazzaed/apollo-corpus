# Memento lavoro — istruzioni per l'aggiornamento automatico delle schede

Sei nel repository pubblico del corpus normativo. Il lavoro da fare e' nel file di triage indicato nel prompt:
`schede` (id → motivi: una norma citata e' cambiata, e' uscita prassi nuova, la scheda e' «da ricontrollare»),
`crea` (schede nuove, con titolo e area), `numeri` (valori annuali da aggiornare in
`wiki-studio/lavoro/dati/dati-lavoro.json`). Fai solo quello: non toccare altri file (verrebbero ripristinati).

## Cos'e' una scheda
Una MAPPA per istituto del diritto del lavoro, letta da chi assiste un lavoratore: quali norme leggere alla data dei
fatti, cosa cercare nel contratto collettivo, quale prassi amministrativa, quali numeri annuali, quali termini e
decadenze, quali temi di giurisprudenza cercare, quali insidie, quali documenti chiedere. Non e' una fonte e non
spiega la legge: la indica. Frasi brevi, elenchi, niente dottrina.

## Formato (obbligatorio)
Intestazione fra `---`, una riga per chiave, valori JSON:
`id` (= nome del file), `titolo`, `area` (qualificazione | tipologie | retribuzione | tempo-e-assenze | rapporto |
cessazione | previdenza | tutela), `istituti` (lista), `parole_chiave` (lista: le parole con cui l'istituto compare
nell'oggetto delle circolari), `norme` (lista «slug:articolo», es. "l-604-1966:6", "cc:2103", "dlgs-23-2015:3"),
`prassi` (lista di id dell'indice della prassi, es. "inps:circolare:2026:104"), `numeri` (lista di chiavi di
dati-lavoro.json), `stato` ("bozza": lo sigilla il controllo). Poi:

    # <titolo> — mappa
    > **Uso di questo file (Principio Zero)**: trampolino, non gabbia; mappa, non fonte. Ogni norma si legge alla
    > data dei fatti, ogni pronuncia si cerca e si verifica; i numeri dell'anno stanno in dati-lavoro.json.
    ## Norme da leggere alla data
    ## Cosa cercare nel CCNL
    ## Prassi amministrativa
    ## Numeri
    ## Termini e decadenze
    ## Temi di giurisprudenza (da cercare e leggere, senza estremi)
    ## Insidie lato lavoratore
    ## Documenti e domande al cliente

## Regole che il controllo meccanico applica (una scheda che le viola resta com'era)
1. Ogni norma citata nel testo («art. 6 L. 604/1966», «artt. 2118 e 2119 c.c.», «art. 18 L. 300/1970») deve stare in
   `norme`, e ogni voce di `norme` deve esistere nel corpus e non essere abrogata. Leggi SEMPRE il testo prima di
   citarlo: `python3 scripts/memento_verifica.py --leggi l-604-1966:6` (o `python3 scripts/codice_locale.py --art 6
   --codice l-604-1966`). Forme degli atti: «c.c.», «c.p.c.», «Cost.», «L. 604/1966», «D.Lgs. 23/2015», «D.L. 87/2018»,
   «D.P.R. 1124/1965».
2. Ogni numero con un'unita' (giorni, mesi, anni, ore, settimane, dipendenti, lavoratori, mensilita', %) deve stare
   sulla STESSA riga della norma che lo stabilisce, e comparire nel testo di quella norma (in cifre o in lettere). Se la
   norma non lo dice, non scriverlo.
3. Niente estremi di pronunce (Cassazione, Corte costituzionale, tribunali, CGUE, numeri di sentenza): nella sezione
   dei temi scrivi COSA cercare («onere della prova del repechage», «comporto e disabilita'»), non chi l'ha deciso.
4. Niente importi in euro e niente cifre decimali: i valori annuali stanno in `dati-lavoro.json`; nella scheda va la
   chiave (sezione «Numeri»).
5. La prassi citata nel testo («circolare INPS n. 104/2026», «nota INL n. 6261/2025», «interpello n. 3/2026») deve
   stare in `prassi` ed essere nell'indice `wiki-studio/lavoro/prassi/indice.json` (cerca con
   `python3 scripts/prassi_indice.py --cerca "parole" --ente inps`) e va letta alla fonte (WebFetch dell'url). Se un
   documento utile non e' nell'indice, aggiungilo a `wiki-studio/lavoro/prassi/curata.json` (`voci`: id →
   {ente, tipo, numero, anno, data, titolo, url https}).
6. Niente comandi, niente blocchi di codice, niente nomi di studi o di persone.

## Numeri annuali
Per ogni chiave in `numeri` del triage trova l'atto dell'anno (di solito una circolare INPS di gennaio-febbraio: cerca
nell'indice della prassi), leggilo alla fonte, e scrivi in `serie["AAAA"]`: `valore` (numero), `metodo: "estratto"`,
`fonte` {ente, atto, url, prassi_id}, `verificato_il`. Poi `python3 scripts/dati_lavoro.py --verifica --chiave K
--anno AAAA` deve dare OK (il valore deve comparire nel testo della fonte). Le voci derivate (es. ticket di
licenziamento) le calcola lo script: non scriverle.

## Prima di finire
- `python3 scripts/memento_verifica.py --valida <file>` su ogni scheda toccata: zero errori.
- Scrivi il file degli esiti indicato nel prompt: JSON {id: {"esito": "aggiornata" | "invariata" | "creata" |
  "non_riuscita", "nota": "una riga"}}. «invariata» = hai riletto norme e prassi e la scheda resta giusta cosi'.
- Se non riesci a rendere una scheda conforme, lasciala com'era e scrivi «non_riuscita» con il motivo.
