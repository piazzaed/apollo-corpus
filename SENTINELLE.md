# Sentinelle automatiche

Questo repository, oltre al corpus normativo (vedi README), ospita le **sentinelle automatiche**: un workflow settimanale
(`.github/workflows/sentinelle.yml`) che tiene aggiornati, con un controllo meccanico, alcuni dati e documenti usati dai
plugin che leggono il corpus.

| Area | Cosa aggiorna | Come si verifica |
|---|---|---|
| dati | tassi (BCE, legale, mora commerciale, FOI, BOT), soglie d'usura, tabelle datate | valori estratti dagli script da documenti ufficiali scaricati nel giro; limiti di plausibilità; per le tabelle, articoli di riferimento invariati nel corpus |
| normativa | sidecar delle riforme monitorate, debito di verifica, changelog delle riforme, drift-report | ogni esito ha una prova: pagina ufficiale riscaricata, estremi e citazione ritrovati |
| successioni | novità sul modello, specifiche e software di compilazione, uffici competenti | come sopra; le costanti di calcolo non cambiano mai in automatico |
| modelli | schede dei modelli d'atto | controllo deterministico delle norme citate contro il corpus; correzioni accettate solo se il controllo torna verde |

Le aree hanno un manifest proprio (`wiki-studio/sentinelle/manifest.json`), separato da quello del corpus. Ciò che non
supera il controllo resta com'era e apre una issue con l'etichetta `sentinelle`. Un'area scrive nel repository solo se
compare nella variabile `SENTINELLE_AREE_SCRITTURA`; altrimenti il giro è a secco (solo rapporto).

I modelli d'atto sono schede di lavoro: vanno sempre adattati al caso e riletti da chi firma.
