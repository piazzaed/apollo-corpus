# Apollo — corpus normativo

Testi ufficiali di atti normativi italiani, come pubblicati da
[normattiva.it](https://www.normattiva.it) (formato Akoma Ntoso, testo vigente), con la data di vigenza
di ciascun articolo. I testi di legge non sono protetti dal diritto d'autore (art. 5 L. 633/1941).

- `wiki-studio/normativa/testi/` — un file `.md` per atto (o per libro) e il relativo indice `*-indice.json`
- `wiki-studio/normativa/changelog-auto.*` — modifiche articolo per articolo fra un aggiornamento e l'altro
- `wiki-studio/normativa/movimento.json` — atti modificati da leggi appena pubblicate in Gazzetta Ufficiale
  e non ancora recepite nel testo consolidato di normattiva
- `wiki-studio/normativa/cassazione/` — estremi dei provvedimenti civili della Corte di cassazione dal 2021
  (numero, sezione, date, tipo, materia; nessun dato personale), da SentenzeWeb
- `wiki-studio/normativa/testi/secondo-livello/` — testi che normattiva non pubblica: regolamenti e disposizioni
  di autorità, codici deontologici, contratti collettivi nazionali di lavoro. Un file per fonte (per i contratti
  collettivi, uno per edizione), con in testa la fonte pubblica da cui è preso (`url`), l'impronta sha256 del
  documento d'origine (`sha256_fonte`) e l'esito del confronto automatico fra il testo e quel documento
  (`fedelta`). Sono riprodotti soltanto da fonti pubbliche (archivio CNEL, siti delle parti firmatarie,
  autorità); chi ne detiene i diritti può chiederne la rimozione aprendo una issue.
- `manifest.json` — impronte sha256 di ogni file e data dell'ultima verifica di ogni atto

Aggiornamento automatico ogni lunedì (`.github/workflows/settimanale.yml`); le fonti di secondo livello
entrano nel manifest a ogni caricamento (`.github/workflows/contributi.yml`), e un file non valido resta
in quarantena. Non è una banca dati ufficiale: per ogni uso professionale fa fede la fonte (normattiva,
Gazzetta Ufficiale, SentenzeWeb, il documento indicato in ciascun file).
