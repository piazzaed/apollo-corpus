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
- `wiki-studio/lavoro/` — strumenti per il diritto del lavoro:
  - `ccnl/` indice dei contratti collettivi dell'Archivio nazionale del CNEL: solo metadati (codici, titoli,
    firmatari, accordi con le loro date, dipendenti INPS per contratto), fonte CNEL, licenza IODL 2.0. I testi dei
    contratti non stanno qui: si scaricano dall'archivio del CNEL quando servono;
  - `prassi/` indice di circolari, messaggi, note e interpelli (INPS, Ispettorato nazionale del lavoro, Ministero
    del lavoro, INAIL): numero, data, oggetto e indirizzo del documento, nessun testo;
  - `dati/` numeri che cambiano ogni anno (massimali, minimali, importi), ciascuno con l'atto da cui e' preso;
  - `memento/` schede per istituto: mappe che dicono quali norme, quali clausole del contratto e quali documenti
    leggere, non fonti. Ogni citazione va verificata sul testo ufficiale; le pronunce non vi sono citate.
- `manifest.json` — impronte sha256 di ogni file e data dell'ultima verifica di ogni atto

Aggiornamento automatico ogni lunedì (`.github/workflows/settimanale.yml`); le fonti di secondo livello
entrano nel manifest a ogni caricamento (`.github/workflows/contributi.yml`), e un file non valido resta
in quarantena. L'area lavoro si aggiorna dopo il giro del lunedì (`.github/workflows/lavoro.yml`): le schede
toccate da una legge modificata o da una circolare nuova le riscrive un modello linguistico (Claude), e un
controllo meccanico ne verifica ogni riferimento prima della pubblicazione; una scheda che non lo supera resta
com'era, marcata «da ricontrollare». Non è una banca dati ufficiale: per ogni uso professionale fa fede la fonte (normattiva,
Gazzetta Ufficiale, SentenzeWeb, il documento indicato in ciascun file).
