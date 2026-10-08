# Changelog riforme — rete di sicurezza anti-allucinazione (cross-check, NON fonte)
<!-- tag: tipo_atto=*, rito=*, fase=*, materia=*, foro=* -->

> ⚠️ **Cos'è questo file e cosa NON è.** È una **rete di sicurezza anti-trappola**: una lista curata di
> *errori post-riforma* tipici del modello (istituti abrogati/rinominati, riti sostituiti). Serve a
> **intercettare** le citazioni sbagliate, **NON** è l'elenco delle norme citabili e **NON** è la fonte da
> cui attingere la norma. **La norma vigente si legge dal corpus locale datato** (testo ufficiale normattiva:
> `corpus_cerca.py` per trovarla, `norma.py --data-evento` per leggerla alla data; il web solo per ciò che il corpus non
> copre o per le modifiche successive allo snapshot): questo changelog è il **cross-check** che il Livello 0 applica con
> gate intertemporale per evitare le trappole note. Vedi il **Principio della ricerca mirata** in
> [`../protocolli/nucleo-verifica.md`](../protocolli/nucleo-verifica.md).
>
> Ha **assorbito** la copia divergente che stava in
> `skills/report-strategia-verificato/references/riforme-changelog.md` (eliminata): è l'**unico** changelog,
> referenziato via `${CLAUDE_PLUGIN_ROOT}/wiki-studio/normativa/changelog-riforme.md`.
>
> **Ultimo controllo: 20 agosto 2026** (recepimento delle proposte tell-only dei drift-report della
> Sentinella dal 14/07 al 20/08/2026 — v. [`drift-reports/`](drift-reports/)). La copia macchina della
> freschezza per-voce e gli **intervalli di vigenza** stanno nel sidecar
> [`changelog-riforme.meta.json`](changelog-riforme.meta.json) (letto da `scripts/freshness.py`). La
> dimensione "alla data" è in [`../protocolli/datazione-verifica.md`](../protocolli/datazione-verifica.md).
>
> 🔎 **Come leggere lo status probatorio delle voci recepite.** Ogni voce aggiunta dai giri della Sentinella
> porta la qualificazione della fonte con cui è stata chiusa: **[PRIMARIA]** = testo letto su
> normattiva/G.U./Corte costituzionale/Cassazione; **[ESTREMI PRIMARI, CONTENUTO NON LETTO]** = l'atto esiste
> ed è attestato da fonte primaria ma il testo non è stato aperto — **non citabile nel merito**;
> **[SECONDARIA]** = da riconfermare live prima di qualunque uso in atto. Dove manca la marcatura, vale il
> regime ordinario del file (cross-check, mai fonte).
>
> **Convenzione**: ⛔ = errore tipico del modello (da NON usare). ✅ = formulazione corretta.
>
> ⚠️ **Avvertenza intertemporale (leggere sempre)**: le voci marcate "abrogato/sostituito" valgono **per i
> giudizi instaurati dopo la decorrenza della riforma**. Per *tempus regit actum* (art. 35 D.Lgs. 149/2022,
> decorrenze scaglionate) un istituto "abrogato" può essere ancora quello corretto in un giudizio pendente
> **prima** della riforma. Il gate "abrogato → nuovo" è **condizionato alla data di instaurazione del
> grado**, MAI automatico (vedi `datazione-verifica.md`). I dubbi transitori sono claim DUBBIE da verificare.

## Quadro sintetico

| Riforma | Estremi | In vigore | Impatto chiave |
|---|---|---|---|
| Riforma Cartabia (processo civile) | D.Lgs. 10/10/2022 n. 149 | 28/02/2023 | rito semplificato di cognizione (artt. 281-decies ss., introdotto con **ricorso** ex 281-undecies); **702-bis ABROGATO**; memorie ex art. 171-ter; verifiche preliminari 171-bis; nuovi requisiti citazione (163); appello (342) |
| Correttivo Cartabia | D.Lgs. 31/10/2024 n. 164 | **26/11/2024** | chiarimenti 171-bis; digitalizzazione/PEC; titolo esecutivo da duplicato informatico (475); modifiche al pignoramento; mutamento rito sfratto |
| CCII | D.Lgs. 12/01/2019 n. 14 | 15/07/2022 | adeguati assetti (art. 2086 c.c.); composizione negoziata; liquidazione giudiziale (ex fallimento) |
| Terzo correttivo CCII | D.Lgs. 136/2024 | 28/09/2024 | ulteriori modifiche al CCII [verificare punti rilevanti per il caso] |
| Imposta di successione/donazione | D.Lgs. 18/09/2024 n. 139 | 01/01/2025 | **autoliquidazione**; eliminato coacervo; presentazione telematica (rilevante per `assistente-successioni`) |
| Parametri forensi | DM 13/08/2022 n. 147 (mod. DM 55/2014) | 23/10/2022 | tabelle compensi **VIGENTI** — ⚠️ nuovo DM ATTESO (vedi watchlist) |
| **Rendite vitalizie in successione** | **C.Cost. sent. 89/2026** (dep. 28/05/2026) | dal 04/06/2026 | **floor 2,5%** al saggio legale per attualizzare le rendite: caduti art. 17 co. 1 lett. c) TUS *ante* 139/2024, art. 46 d.P.R. 131/1986, art. 9 co. 4 D.Lgs. 139/2024, artt. 50 co. 8 e 102 co. 4 D.Lgs. 123/2025 (§2.5) |
| **TU imposte indirette** | D.Lgs. 01/08/2025 n. 123 | in vigore 13/08/2025, **efficacia 1/1/2027** | abroga il **TUS 346/1990**, gran parte del d.P.R. 131/1986 e del D.Lgs. 347/1990 (art. 204). **Fino al 31/12/2026 si applica il TUS** (§2.6) |
| **TU adempimenti e accertamento** | D.Lgs. 05/08/2026 n. 141 | in vigore 07/08/2026, effetti TU 1/1/2027 | art. 4 (56 lettere, a→ggg) riscrive il D.Lgs. 123/2025; dal 1/1/2027 **dichiarazioni sostitutive** al posto dei certificati in successione (§2.7) |
| **Contratto a termine — somministrazione** | D.L. 30/04/2026 n. 62 conv. L. 25/06/2026 n. 112, art. 16-quinquies | **28/06/2026** | cambia il **computo dei 24 mesi** (solo somministrati a termine) e introduce il tetto autonomo di **36 mesi** per i somministrati a tempo indeterminato (§1.3) |
| **Indennità art. 28 D.Lgs. 81/2015** | D.L. 16/09/2024 n. 131 art. 11, conv. L. 14/11/2024 n. 166 | 17/09/2024 | il tetto delle **12 mensilità non è più invalicabile**: il giudice può liquidare di più se il lavoratore prova il **maggior danno**; comma 3 abrogato (§1.3) |
| **Collegato lavoro** | L. 13/12/2024 n. 203 | 12/01/2025 | attività stagionali (art. 11), dimissioni per fatti concludenti (art. 19), periodo di prova nel termine (art. 13) — §1.3 |
| **Delega riforma forense** | L. 28/07/2026 n. 137 | 16/08/2026 | decreti delegati entro il **16/02/2027**; il DM parametri diventa **biennale** su proposta CNF (art. 2 lett. g n. 2) — §6 |
| **Immigrazione 2025** | D.L. 28/03/2025 n. 37 conv. L. 23/05/2025 n. 75 | 29/03/2025 | trattenimento, Albania, **procedura accelerata alla frontiera** — tocca i presupposti del ricorso ex art. 35-bis (§4.7) |

---

## 1. CIVILE / PROCESSUALE

### 1.1 Riforma Cartabia — D.Lgs. 149/2022 (in vigore 28/02/2023) e Correttivo D.Lgs. 164/2024 (26/11/2024)
<!-- tag: fase=primo_grado|appello|cassazione|cautelare|condizioni_procedibilita|monitorio -->

#### Rito sommario di cognizione → Rito semplificato di cognizione
- ⛔ "Ricorso ex art. 702-bis CPC" / "rito sommario di cognizione" / artt. 702-bis, 702-ter, 702-quater CPC (per i giudizi instaurati **dal 28/02/2023**; per quelli pendenti prima, vedi avvertenza intertemporale).
- ✅ **Rito semplificato di cognizione**, artt. **281-decies, 281-undecies, 281-duodecies, 281-terdecies CPC**.
- ⚠️ **Forma di introduzione**: il rito semplificato si introduce **con RICORSO (art. 281-undecies)**, NON con citazione. La **citazione** (art. 163) è la forma del **rito ordinario**. Trappola da bloccare: "semplificato introdotto con citazione".
- Nota: obbligatorio quando il Tribunale decide in composizione monocratica e i fatti non sono controversi o l'istruzione è di pronta soluzione (art. 281-decies). Decisione con ordinanza.

#### Verifiche preliminari e memorie integrative
- ⛔ "Memorie ex art. 183, comma 6, CPC" (vecchia formulazione 30/30/20).
- ✅ **Verifiche preliminari del giudice ex art. 171-bis CPC** (entro 15 gg dalla scadenza per la costituzione del convenuto). **Memorie integrative ex art. 171-ter CPC**: 3 memorie con termini **a ritroso dall'udienza** ex art. 183 (**40 / 20 / 10 giorni**).
- Nota: la struttura "tre memorie" sopravvive ma cambiano numerazione e tempistica (anticipata).

#### Costituzione delle parti e termini di comparizione
- ⛔ Termine di costituzione dell'attore "= 10 giorni dalla notifica".
- ✅ L'attore si costituisce **almeno 10 giorni prima dell'udienza** (art. 165). Termine a comparire **almeno 120 giorni** dalla notificazione (art. 163-bis, elevato dai precedenti 90; 150 gg se estero). Convenuto: costituzione **almeno 70 giorni prima dell'udienza** (art. 166).

#### Trattazione scritta
- ⛔ "L'udienza è sempre obbligatoria".
- ✅ **Trattazione scritta sostitutiva dell'udienza ex art. 127-ter CPC** (note scritte), d'ufficio o su istanza, salvo opposizione delle parti. Deposito telematico **ore 24** del giorno di scadenza (art. 196-quater disp. att.).

#### Persone, minorenni e famiglie
- ⛔ Citare separatamente i riti per separazione/divorzio/modifica condizioni.
- ✅ **Rito unico famiglia ex artt. 473-bis ss. CPC** (473-bis a 473-bis.71), Tribunale ordinario in composizione collegiale. Il **Tribunale per le persone, i minorenni e le famiglie** (artt. 49 ss. D.Lgs. 149/2022) ha entrata in funzione differita — verificare lo stato attuale.

#### Cassazione — nuovi filtri
- ✅ **art. 360-bis** (inammissibilità); **art. 380-bis** novellato (proposta di definizione semplificata del relatore; collegiale entro 40 gg su richiesta); **rinvio pregiudiziale art. 363-bis** (questione di diritto nuova e seriale).

#### Mediazione e negoziazione assistita
- ✅ **Mediazione obbligatoria ampliata** (art. 5 D.Lgs. 28/2010): aggiunte associazione in partecipazione, consorzio, franchising, opera, rete, somministrazione, società di persone, subfornitura. **Negoziazione assistita estesa al lavoro** (art. 2-ter D.L. 132/2014, facoltativa per controversie ex art. 409).

#### Cautelari — strumentalità attenuata
- ✅ **art. 669-octies, c. 6 CPC**: per i provvedimenti d'urgenza ex art. 700 e gli anticipatori, il giudizio di merito **non è obbligatorio** per conservare l'efficacia.

### 1.2 Processo esecutivo — Cartabia / Correttivo
<!-- tag: materia=esecuzioni|recupero_crediti|bancario|condominio|locazioni, fase=esecuzione -->
- ✅ Verificare artt. 543 ss. CPC come modificati; forma telematica della dichiarazione del terzo come regola; **iscrizione a ruolo** di precetto/pignoramento a carico del creditore entro termini perentori (verificare la disposizione). Correttivo 164/2024: titolo esecutivo da **duplicato informatico** (art. 475).

### 1.3 Rito del lavoro — Cartabia (441-bis), tutele crescenti riscritte dalla Consulta, trasparenza, termine
<!-- tag: materia=lavoro|previdenza, rito=lavoro -->

> Voci verificate live il **12/07/2026** (normattiva.it via `fonti_fetch.py`; cortecostituzionale.it/giurcost.org
> e stampa specializzata per la sequenza costituzionale). Freshness per-voce nel sidecar
> [`changelog-riforme.meta.json`](changelog-riforme.meta.json), materia `lavoro`. Profilo operativo completo:
> skill `diritto-del-lavoro`.

#### Rito: resta autonomo + corsia licenziamenti (Cartabia, giudizi instaurati dal 28/02/2023)
- ✅ Il rito lavoro resta **autonomo** (artt. 409-447 CPC), NON confluito nel rito semplificato.
- ⛔ "Ricorso ex art. 1, co. 48 ss., L. 92/2012" / "rito Fornero" per i giudizi instaurati **dal 28/02/2023**.
- ✅ **Rito Fornero ABROGATO**: art. 1, commi **47-69**, L. 92/2012 abrogati dall'**art. 37, co. 1, lett. e),
  D.Lgs. 149/2022** (testo verificato 12/07/2026 su normattiva). Al suo posto: **artt. 441-bis ss. CPC** —
  trattazione e decisione **prioritarie** per le controversie di licenziamento con domanda di
  **reintegrazione** (anche se c'è questione di qualificazione del rapporto); termini riducibili **fino alla
  metà** (minimo 20 gg tra notifica e udienza); concentrazione istruttoria/decisoria; stesse esigenze di
  celerità in appello e cassazione (441-ter socio di cooperativa; 441-quater licenziamento discriminatorio).
- ⚠️ **Gate intertemporale**: per i ricorsi Fornero **depositati prima del 28/02/2023** il vecchio rito resta
  quello corretto del giudizio pendente (art. 35 D.Lgs. 149/2022, *tempus regit actum* — v. avvertenza in testa).
- ✅ Negoziazione assistita **estesa al lavoro**: voce già al **§1.1** (art. 2-ter D.L. 132/2014, facoltativa) —
  qui solo il raccordo: l'accordo vale come **sede protetta** ex art. 2113, co. 4, c.c. (non duplicare la voce).

#### Tutele crescenti (D.Lgs. 23/2015) — testo RISCRITTO dalla Corte costituzionale
- ⛔ Applicare/citare il **testo originario**: indennità rigida "2 mensilità per anno di servizio" (art. 3);
  "1 mensilità per anno" per i vizi formali (art. 4); reintegra solo per nullità "**espressamente**" previste
  (art. 2); **tetto di 6 mensilità** per le piccole imprese (art. 9). Tutto superato dalla sequenza che segue.
- ✅ **C.Cost. 194/2018** — art. 3, co. 1: caduto il criterio rigido a sola anzianità; indennità (6-36 mens.)
  determinata dal giudice su una pluralità di criteri (verificato 12/07/2026 su temi.camera.it/lavorodirittieuropa.it).
- ✅ **C.Cost. 150/2020** — art. 4: stesso principio per i **vizi formali e procedurali** (verificato
  12/07/2026 su quotidianopiu.it/rivistalabor.it).
- ✅ **C.Cost. 183/2022** — *anello mancante, aggiunto il 20/08/2026* [PRIMARIA: ricostruzione contenuta nella
  motivazione dell'ord. 131/2026, letta integralmente su cortecostituzionale.it il 14/08/2026]: accerta il
  *vulnus* sul tetto delle sei mensilità per i piccoli datori ma **non può porvi rimedio** in difetto di
  soluzioni costituzionalmente obbligate → inammissibilità **con monito**, avvertendo che «*un ulteriore
  protrarsi dell'inerzia legislativa non sarebbe tollerabile*». È la pronuncia che spiega **perché** sia poi
  arrivata la 118/2025: si cita come precedente-monito, mai come base di illegittimità.
- ✅ **C.Cost. 22/2024** — art. 2, co. 1: illegittima la parola «**espressamente**» → reintegrazione piena per
  **tutti** i casi di nullità di legge, anche "virtuali" da norma imperativa (verificato 12/07/2026 su
  altalex.com/giurcost.org).
- ✅ **C.Cost. 128/2024** — art. 3, co. 2: reintegra attenuata anche per il **GMO** quando è direttamente
  dimostrata in giudizio l'**insussistenza del fatto materiale** (verificato 12/07/2026 su
  lavorodirittieuropa.it/cortecostituzionale.it).
- ✅ **C.Cost. 129/2024** — disciplinare: reintegra attenuata anche per fatto punito dal **CCNL con sanzione
  conservativa** (verificato 12/07/2026 su lavorosi.it/eius.it).
- ✅ **C.Cost. 118/2025** — art. 9, co. 1: incostituzionale il **tetto delle 6 mensilità** per i datori
  sotto-soglia; resta il dimezzamento (forbice fino a ~18 mens., senza tetto fisso). **Estremi completi,
  letti sulla nota di aggiornamento (11) dell'art. 9 su normattiva l'08/08/2026** [PRIMARIA]: sentenza
  **23 giugno – 21 luglio 2025, n. 118**, in **G.U. 1ª serie speciale n. 30 del 23/07/2025**, illegittimità
  «*limitatamente alle parole «e non può in ogni caso superare il limite di sei mensilità»*».
- ✅ **C.Cost. ord. 131/2026** — *conferma processuale, non principio nuovo* [PRIMARIA: testo integrale letto
  su cortecostituzionale.it il 14/08/2026]. ECLI:IT:COST:2026:131, Pres. Amoroso, red. Sciarrone Alibrandi;
  c.d.c. e decisione 23/03/2026, **deposito 17/07/2026**, G.U. 1ª s.s. n. 29 del 22/07/2026. Dichiara la
  **manifesta inammissibilità** della questione sull'art. 9 co. 1 per **sopravvenuta carenza di oggetto**,
  il tetto essendo già caduto con la 118/2025. Atto deciso: **reg. ord. n. 212/2025 del Tribunale di Padova**
  (ord. 16/07/2025) — ⚠️ **non** la reg. ord. 39/2026 di Livorno, attribuzione errata nata da snippet
  indicizzati e cancellata il 14/08/2026.
- ✅ **Referendum abrogativo 8-9/06/2025**: quorum NON raggiunto (affluenza ~30,6%) → l'impianto del
  D.Lgs. 23/2015 **resta in vigore** (verificato 12/07/2026 su misterlex.it).
- ⚠️ **Trappola di lettura, da non sbagliare mai** (rilevata su primaria l'01/08/2026): sul testo di
  normattiva il tetto delle sei mensilità è **ancora scritto nel corpo dell'art. 9, co. 1** — la caducazione
  vive **soltanto nella nota di aggiornamento (11)**. Chi legge l'articolo senza le note ricava una **regola
  morta**. Regola permanente per la lente L1 in [`../protocolli/nucleo-verifica.md`](../protocolli/nucleo-verifica.md).
- ⚠️ **Mappatura pronuncia → articolo inciso** (rilievo del 10/08/2026): la sequenza sopra **non** incide
  tutta sugli stessi articoli. Su normattiva gli **artt. 3 e 9** portano solo le note da **194/2018**,
  **128/2024** e **118/2025**; le altre pronunce toccano articoli diversi (art. 2 → 22/2024; art. 4 →
  150/2020; disciplinare → 129/2024). Citare la pronuncia **con l'articolo che ha inciso**, mai la sequenza
  in blocco.
- ⚠️ **Rimessione pendente da monitorare — art. 8 L. 604/1966** (norma **contigua**, non il D.Lgs. 23/2015):
  **reg. ord. n. 39/2026**, ordinanza **Tribunale di Livorno 12/02/2026**, G.U. 1ª s.s. n. 11 del 18/03/2026
  [PRIMARIA: scheda-ordinanza ed elenco pendenti letti su cortecostituzionale.it, da ultimo il 19/08/2026].
  Camera di consiglio **06/07/2026**, rel. Sciarrone Alibrandi; **nessun deposito al 20/08/2026**. Il *petitum*
  **non è la caducazione del tetto ma la sua sostituzione con un massimo di 12 mensilità**: se accolta in
  questi termini il tetto **raddoppia, non sparisce** — dato che cambia la stima del rischio in una
  conciliazione. Nessun effetto sul testo vigente dell'art. 8 (letto integro su normattiva il 09/08/2026).
- 🔴 **Da NON associare a questa voce: la reg. ord. 41/2026.** Accertato su primaria il 19/08/2026 che è
  un'ordinanza del **Trib. di Campobasso, sez. immigrazione, 06/02/2026**, sulla **cittadinanza iure
  sanguinis** (art. 3-bis L. 91/1992), confluita nell'ord. C.Cost. **147/2026** (rinvio pregiudiziale alla
  CGUE, dep. 23/07/2026). Nulla a che vedere con le tutele crescenti.
- Materia ad **ALTA volatilità**: riverificare la sequenza prima di ogni atto.
- ✅ **Doppio binario** (regola di instradamento): assunti **fino al 6/3/2015** → art. 18 L. 300/1970
  post-Fornero (reintegra piena per nullità/discriminatorio a prescindere dall'organico, anche dirigenti);
  assunti **dal 7/3/2015** → D.Lgs. 23/2015 come riscritto sopra. Prima domanda: data di assunzione + organico.

#### Crediti retributivi — decorrenza della prescrizione (post-Fornero)
- ✅ Prescrizione quinquennale (art. 2948, n. 4, c.c.) con decorrenza **dalla CESSAZIONE del rapporto** per i
  rapporti non più assistiti da stabilità reale adeguata (orientamento consolidato: Cass. sez. lav.
  n. 26246/2022, verificato 12/07/2026 su adlabor.it/diritto.it). Regola prudente: computare dalla cessazione.

#### Trasparenza — D.Lgs. 104/2022 (in vigore dal 13/08/2022)
- ✅ Attuazione dir. (UE) **2019/1152** (condizioni di lavoro trasparenti e prevedibili — esistenza e base
  verificate 12/07/2026 su normattiva): obblighi informativi rafforzati (D.Lgs. 152/1997 novellato), inclusi i
  sistemi decisionali/di monitoraggio **automatizzati** (art. 1-bis, poi ritoccato dal D.L. 48/2023) —
  [verificare il dettaglio degli obblighi prima dell'uso in pareri/diffide].
#### Collegato lavoro — L. 13/12/2024 n. 203 (G.U. S.G. n. 303 del 28/12/2024, cod. red. 24G00218, in vigore 12/01/2025)

> Tre istituti chiusi **su primaria** (normattiva, permalink URN) nei giri del 10 e 11/08/2026. Restano fuori
> perimetro, non verificati: smart working, apprendistato, conciliazioni telematiche, contratto misto.

- ✅ **Attività stagionali — art. 11 L. 203/2024** (norma di **interpretazione autentica** dell'art. 21, co. 2,
  secondo periodo, D.Lgs. 81/2015) [PRIMARIA, letta 10/08/2026]: rientrano nelle attività stagionali, «*oltre
  a quelle indicate dal d.P.R. 7 ottobre 1963, n. 1525*», le attività organizzate per far fronte a
  **intensificazioni in determinati periodi dell'anno** o a esigenze tecnico-produttive/cicli stagionali
  «*secondo quanto previsto dai contratti collettivi di lavoro, **ivi compresi quelli già sottoscritti alla
  data di entrata in vigore della presente legge***». ➜ La stagionalità **la definiscono i CCNL**, non più il
  solo d.P.R. 1963. Ricade su due leve tipiche: lo **stop and go** dell'art. 21 co. 2 (le pause di 10/20 gg
  non si applicano alle stagionali → niente trasformazione automatica) e i **rinnovi/proroghe** liberi senza
  causale. Leva difensiva classica del datore in causa di conversione: conoscerla in attacco e in difesa.
  - ⚠️ **Non asserire** che la norma sia retroattiva *perché* di interpretazione autentica: è lettura
    dottrinale, non clausola del testo. Il testo dice solo «ivi compresi quelli già sottoscritti».
- ✅ **Dimissioni per fatti concludenti — art. 19 L. 203/2024**, che inserisce il **comma 7-bis** nell'art. 26
  D.Lgs. 151/2015 [PRIMARIA, letta 11/08/2026]: assenza ingiustificata oltre il termine del CCNL applicato o,
  in mancanza, **oltre quindici giorni** → comunicazione all'**Ispettorato territoriale del lavoro**, che può
  verificarne la veridicità; il rapporto «*si intende risolto per volontà del lavoratore*» e non si applica la
  procedura telematica di convalida. **Terzo periodo — la vera difesa del lavoratore**: la regola non opera se
  il lavoratore **dimostra l'impossibilità**, per forza maggiore o fatto imputabile al datore, di comunicare i
  motivi dell'assenza. Il co. 8-bis esclude l'applicazione ai rapporti alle dipendenze delle PP.AA. ex art. 1
  co. 2 D.Lgs. 165/2001.
- ✅ **Periodo di prova nel contratto a termine — art. 13 L. 203/2024** (non l'art. 19), che riscrive l'art. 7,
  co. 2, D.Lgs. 104/2022 [PRIMARIA, letta 11/08/2026]: «*Fatte salve le disposizioni più favorevoli della
  contrattazione collettiva*», durata = **un giorno di effettiva prestazione ogni quindici giorni di
  calendario** dall'inizio del rapporto; **mai meno di 2 giorni**, **mai più di 15** per rapporti fino a sei
  mesi e **30** per quelli oltre sei e sotto i dodici mesi. Resta fermo il primo periodo del co. 2 (prova
  proporzionata a durata e mansioni; divieto di nuova prova nel rinnovo per le stesse mansioni).
- Prassi applicativa (secondaria, da riconfermare): **Circolare Min. Lavoro n. 6/2025**.

#### Contratto a termine — D.Lgs. 81/2015, stato causali al 19/08/2026
- ✅ **Art. 19 vigente** [PRIMARIA: testo integrale riletto su normattiva il **19/08/2026**, note comprese]:
  acausale ≤ **12 mesi**; da 12 a **24 mesi** solo con (a) causali dei **CCNL** ex art. 51; (b) in assenza di
  previsioni collettive, **e comunque entro il 31/12/2026**, esigenze tecnico-organizzativo-produttive
  **individuate dalle parti**; (b-bis) sostituzione. Superamento 12 mesi senza condizioni → trasformazione a
  tempo indeterminato (co. 1-bis); tetto 24 mesi per successione di contratti. Il previgente co. 1.1 è
  **abrogato** (D.L. 48/2023).
- ✅ **Il perimetro della lett. b), alla lettera** (la parafrasi lo perde): la condizione non è «il CCNL non ha
  previsto causali», ma «*in assenza delle previsioni di cui alla lettera a), **nei contratti collettivi
  applicati in azienda***». Il riferimento è alle previsioni **ex art. 51** richiamate dalla lett. a) e ai
  contratti **effettivamente applicati in azienda**.
- 🔴 **NOVITÀ 2026 — computo dei 24 mesi cambiato. D.L. 30/04/2026 n. 62 (cod. red. 26G00082, G.U. S.G. n. 99
  del 30/04/2026), conv. con modif. dalla L. 25/06/2026 n. 112 (cod. red. 26G00128, G.U. n. 147 del
  27/06/2026), art. 16-quinquies** — modifiche efficaci dal **28/06/2026** [PRIMARIA: nota di aggiornamento
  (58) e corpo dell'art. 19 letti su normattiva il 09-10/08/2026]:
  - **co. 2, secondo periodo** — nel computo dei 24 mesi entrano i periodi di missione «*di lavoratori assunti
    dal somministratore con contratto di lavoro **a tempo determinato***»: il computo **si restringe** ai soli
    somministrati **a termine**;
  - **co. 2-bis (nuovo)** — il somministrato assunto **a tempo indeterminato** può svolgere missioni a termine
    presso lo stesso utilizzatore, su mansioni di pari livello e categoria legale, per una durata complessiva
    **ulteriore rispetto a quella del co. 2 e non superiore a trentasei mesi**, salvo diverso limite del CCNL
    applicato dall'utilizzatore.
  - ⚠️ **Gate intertemporale, da scrivere accanto alla regola**: il limite del co. 2-bis **decorre dal
    28/06/2026** e i **periodi di missione anteriori non rilevano** (art. 16-quinquies, co. 2). Per i rapporti
    anteriori vale il regime previgente.
  - ➜ Chi conta le missioni di un somministrato **a tempo indeterminato** dentro i 24 mesi del co. 2 sbaglia;
    chi ignora il tetto autonomo dei **36 mesi** sbaglia in senso opposto.
- ⚠️ La lett. b) "causale delle parti" **SCADE il 31/12/2026**: a ridosso/oltre quella data ricontrollare
  SEMPRE (proroga o riforma attese) → `vigenza-watchlist.md`, priorità ALTA. Sorveglianza già programmata
  sulla finestra **bilancio / milleproroghe**. ⚠️ **Nota di calendario**: la conferma può arrivare **a ridosso
  della scadenza**, quando i contratti con quella causale sono già stipulati — il rischio è contrattuale, non
  solo processuale.
- ⚠️ **Nota anti-confusione (errore di citazione già pronto)**: **L. 118/2025** (8/08/2025, conv. D.L. 95/2025
  — è la legge che ha prorogato la causale al 31/12/2026) ≠ **C.Cost. 118/2025** (21/07/2025 — tutele
  crescenti). Stesso numero, stesso anno, materie contigue.
- 🔴 **Impugnazione e indennità — art. 28: la voce è cambiata nel 2024 e le schede erano ferme al
  testo previgente** (correzione del 10/08/2026). Restano fermi i **180 giorni dalla cessazione del singolo
  contratto** con le modalità dell'art. 6 L. 604/1966. Ma il **co. 2**, nel testo vigente [PRIMARIA: letto su
  normattiva il 10/08/2026], recita ora: indennità onnicomprensiva tra **2,5 e 12 mensilità**, «*((Resta ferma
  la possibilità per il giudice di stabilire l'indennità in **misura superiore** se il lavoratore dimostra di
  aver subito un **maggior danno**.))*»; e il **co. 3 è ABROGATO**.
  - **Veicolo normativo**: **D.L. 16/09/2024 n. 131, art. 11** («salva-infrazioni», procedura di infrazione
    n. 2014/4231), G.U. S.G. n. 217 del 16/09/2024, cod. red. 24G00149, in vigore **17/09/2024**; conv. con
    modif. dalla **L. 14/11/2024 n. 166**, G.U. S.G. n. 267 del 14/11/2024, cod. red. 24G00184 [estremi di
    G.U. confermati su **schede ELI primarie** l'11/08/2026]. Il confronto fra decreto originario e testo
    coordinato mostra che la **conversione non ha toccato la sostanza** dell'art. 11 (unica differenza: un
    «n.» aggiunto nella rubrica) e **non risulta alcuna disposizione transitoria**.
  - ⛔ **Conseguenza redazionale**: la formula «indennità onnicomprensiva 2,5-12 mensilità» usata da sola
    **porta a sottodimensionare la domanda**. Nel ricorso ex art. 414 c.p.c. il **maggior danno va allegato e
    capitolato**, non lasciato implicito: altrimenti resta la forbice.
  - ⚠️ **Cosa prevedesse il co. 3 abrogato** (per le cause su rapporti cessati **ante 17/09/2024**) [PRIMARIA:
    multivigenza normattiva al 01/01/2019-16/09/2024, letta l'11/08/2026]: «*In presenza di contratti
    collettivi che prevedano l'assunzione, anche a tempo indeterminato, di lavoratori già occupati con
    contratto a termine nell'ambito di specifiche graduatorie, il limite massimo dell'indennità fissata dal
    comma 2 è ridotto alla metà.*» Era una norma **di favore per il datore**: la sua abrogazione va nella
    stessa direzione dell'inciso sul maggior danno.

---

## 2. SUCCESSIONI
<!-- tag: materia=successioni -->

### 2.1 Imposta di successione e donazione — D.Lgs. 139/2024 (dal 01/01/2025)
<!-- tag: materia=successioni -->
- ✅ **Autoliquidazione**: il contribuente calcola e versa l'imposta principale entro 90 gg dalla presentazione della dichiarazione (art. 33 D.Lgs. 346/1990 novellato); l'Ufficio liquida solo la complementare.
- ✅ **Eliminato il coacervo** ai fini dell'imposta di successione (resta rilevante civilisticamente per collazione e azione di riduzione).
- Aliquote invariate (4% coniuge/figli, franchigia 1 mln; 6% fratelli, franchigia 100k; 6% altri parenti fino al 4° grado e affini; 8% altri).
- ⛔ **NON applicare la disciplina transitoria dell'art. 9, comma 4** (coefficienti del DM MEF 21/12/2015 per le
  rendite costituite ante riforma quando il tasso legale è ≤ 0,1%): **è caduta**. Dichiarata
  costituzionalmente illegittima in via consequenziale da **C.Cost. 89/2026**, capo 3 del dispositivo (§2.5);
  e comunque abrogata dall'art. 204, lett. rrr), del D.Lgs. 123/2025 dal 1/1/2027. [PRIMARIA: la nota
  **AGGIORNAMENTO (4)** dell'art. 9 su normattiva recepisce la sentenza — letta il 19/08/2026.]

### 2.2 Riti delle azioni successorie
<!-- tag: materia=successioni -->
- ✅ Petizione ereditaria, divisione giudiziale, azione di riduzione restano nel **rito ordinario** (NON nel rito unico famiglia 473-bis), con le modifiche post-Cartabia (171-bis, 171-ter). Divisione contenziosa: ordinario, con possibile rito semplificato 281-decies se ne ricorrono i presupposti.

### 2.3 Patto di famiglia
<!-- tag: materia=successioni -->
- ✅ Disciplina invariata (artt. 768-bis ss. c.c.). Parti: tutti i legittimari attuali (768-quater); i non assegnatari vanno **liquidati** dal beneficiario.

### 2.4 Accettazione con beneficio d'inventario — termini
<!-- tag: materia=successioni -->
- ✅ Inventario art. 485 c.c. (3 mesi + 3 prorogabili); dichiarazione art. 487 (10 anni dall'apertura; se in possesso dei beni: 3 mesi per l'inventario + 40 gg per dichiarare). Errore frequente: confondere i termini di chi possiede i beni con chi non li possiede.

### 2.5 Rendite e pensioni vitalizie — C.Cost. sent. n. 89/2026 (floor 2,5%)
<!-- tag: materia=successioni -->

> **Buco di copertura colmato, non novità.** La sentenza è pubblicata dal 3/6/2026, cioè *prima* dell'«ultimo
> controllo» che la watchlist portava (17/06/2026): doveva già esserci e non c'era. Emersa il 03/08/2026
> partendo dall'agenda della Consulta invece che dalla watchlist; testo integrale letto su primaria il
> **15/08/2026** (cortecostituzionale.it, `scheda-pronuncia/2026/89`).

- **Estremi** [PRIMARIA]: **C.Cost. sent. n. 89 del 2026**, ECLI:IT:COST:2026:89, giudizio in via incidentale,
  Pres. **Amoroso**, Red. **Antonini**. C.d.c. e decisione **23/03/2026**, **deposito 28/05/2026**,
  pubblicazione in **G.U. 1ª serie speciale n. 22 del 03/06/2026**. Atti decisi: **reg. ord. 210/2025**
  (Cass. sez. trib., ord. 11/06/2025 n. 15547). Norme impugnate: **art. 17, co. 1, lett. c), D.Lgs. 346/1990**.
- **Dispositivo — cinque capi**:
  1. illegittimità dell'**art. 17 D.Lgs. 346/1990** (TUS), *nel testo applicabile prima* della modifica di cui
     all'art. 1, co. 1, lett. r), D.Lgs. 139/2024, **nella parte in cui non prevede che, ai fini della
     determinazione del valore di cui al co. 1 lett. c), non possa assumersi un saggio legale d'interesse
     inferiore al 2,5 per cento**;
  2. in via consequenziale (art. 27 L. 87/1953), illegittimità dell'**art. 46 d.P.R. 131/1986** (imposta di
     registro), stessa parte, stesso floor per il valore di cui al co. 2 lett. c);
  3. in via consequenziale, illegittimità dell'**art. 9, co. 4, D.Lgs. 139/2024** (disciplina transitoria);
  4. in via consequenziale, illegittimità dell'**art. 102, co. 4, D.Lgs. 123/2025**;
  5. in via consequenziale, illegittimità dell'**art. 50, co. 8, D.Lgs. 123/2025**.
- **Ratio**: con tassi legali sotto l'unità il coefficiente di attualizzazione produceva una base imponibile
  «spropositata rispetto alla vita media», con effetto che la Corte definisce «*addirittura deteriore di
  quello "confiscatorio"*» — l'imposta poteva **superare il valore del legato**. Il floor del 2,5% introdotto
  dal D.Lgs. 139/2024 è assunto come punto di riferimento già presente nell'ordinamento e **proiettato
  all'indietro** sui rapporti **non esauriti**.
- 🎯 **Effetto operativo — è una leva difensiva, non un aggiornamento formale**: per le **successioni aperte
  ante 1/1/2025 con pratica non definita** (contenzioso o attesa di avviso di liquidazione) il valore della
  rendita vitalizia da legato **va ricalcolato con il floor 2,5%**. DEAS applica già il floor per le
  successioni **dal 2025 in avanti** (DM MEF 24/12/2025); le **pratiche ante-2025 non esaurite il software
  non le ricalcola da sé** — lì l'intervento è manuale.
- ⚠️ **Anomalia operativa da conoscere prima, non da scoprire allo scarto** (verificata il 19/08/2026):
  **manca ancora la prassi AdE** che recepisca la sentenza. L'ultimo atto in materia è la **Circ. 3/E del
  16/04/2025**, anteriore al deposito. Chi liquida oggi una rendita vitalizia applica un floor imposto dalla
  Consulta ma **non ancora tradotto in istruzioni operative**.
- ⚠️ **Riserva tecnica dichiarata**: l'**art. 17 D.Lgs. 346/1990** — l'articolo colpito in via principale — è
  stato letto sul dispositivo della sentenza, **non** sul testo consolidato di normattiva (difetto di
  costruzione del permalink URN dei testi unici, risolto in `scripts/fonti_fetch.py` il 21/08/2026). Prima di
  trascriverlo in un atto, rileggerlo live.

### 2.6 TU imposte indirette — D.Lgs. 01/08/2025 n. 123: efficacia 1/1/2027 e abrogazione del TUS
<!-- tag: materia=successioni -->

- **Estremi** [PRIMARIA, ELI normattiva `25G00124`]: *Testo unico delle disposizioni legislative in materia di
  imposta di registro e di altri tributi indiretti*, G.U. 12/08/2025, **in vigore 13/08/2025**. Attua la
  delega ex art. 21 L. 111/2023. Perimetro: registro, ipotecaria e catastale, **successioni e donazioni**,
  bollo, IVAFE.
- ✅ **Efficacia rinviata al 1° gennaio 2027 — dato CERTO, letto sul testo coordinato post-conversione**
  [PRIMARIA, 08/08/2026]: l'**art. 4, co. 5, del D.L. 31/12/2025 n. 200** (Milleproroghe, cod. red.
  **25G00213**, G.U. S.G. n. 302 del 31/12/2025) dispone: «*All'articolo 205, comma 1, del testo unico … di
  cui al decreto legislativo 1° agosto 2025, n. 123, le parole: «1° gennaio 2026» sono sostituite dalle
  seguenti: «1° gennaio 2027».*» Il **testo coordinato** con la legge di conversione **L. 27/02/2026 n. 26**
  (atto 26A01010, G.U. S.G. n. 49 del 28/02/2026) riporta il comma **identico**: la conversione **non l'ha
  toccato**. Il rinvio riguarda **cinque testi unici tributari insieme** (sanzioni 173/2024; tributi erariali
  minori 174/2024; giustizia tributaria 175/2024; versamenti e riscossione 33/2025; imposte indirette
  123/2025).
- ⚠️ **Trappola di citazione, l'errore è nella fonte**: l'intestazione del testo coordinato pubblicata in G.U.
  scrive «*decreto-legge **1° dicembre** 2025, n. 200*», mentre l'atto originario è del **31 dicembre 2025**.
  Lo conferma il richiamo alla G.U. n. 302 del 31/12/2025 contenuto nella stessa intestazione e l'aritmetica
  costituzionale (un D.L. del 1° dicembre sarebbe decaduto il 30 gennaio, mentre la conversione è del 27
  febbraio). **Citare sempre D.L. 31/12/2025 n. 200.**
- **Abrogazioni — art. 204** [PRIMARIA, letto integralmente il 04/08/2026]: incipit «*A decorrere dalla data
  di cui all'articolo 205 sono abrogate le seguenti disposizioni*» → il rinvio dell'art. 205 sposta **anche**
  le abrogazioni. Cadono: **lett. l)** artt. 1-3, 4-bis-9, 11-33, 36-46, 48, 49, 55, 56, 57-59-bis, 62 e il
  **prospetto dei coefficienti** del **TUS D.Lgs. 346/1990**; **lett. m)** gran parte del D.Lgs. 347/1990
  (ipotecaria e catastale); **lett. f)** gran parte del d.P.R. 131/1986 (registro); **lett. rrr)** l'art. 9,
  co. 4, D.Lgs. 139/2024. Il **co. 2** contiene la clausola di rinvio automatico (i richiami alle norme
  abrogate si intendono fatti alle corrispondenti del testo unico).
- ✅ **Regola operativa fino al 31/12/2026: si lavora sul TUS D.Lgs. 346/1990.** Nulla da riscrivere oggi nelle
  schede successorie; la **migrazione dei riferimenti** (346/1990 → 123/2025; 131/1986 → 123/2025; 347/1990 →
  123/2025) è **lavoro pianificato con scadenza 31/12/2026**, non emergenza.
- 📌 Promemoria tecnico: il D.Lgs. 123/2025 **non va pre-warmato** prima di dicembre 2026 — metterlo in cache
  indurrebbe la lente L1 a servirlo come diritto vigente.

### 2.7 TU adempimenti e accertamento — D.Lgs. 05/08/2026 n. 141 (in vigore 07/08/2026)
<!-- tag: materia=successioni -->

- **Estremi** [PRIMARIA, scheda ELI letta il 12/08/2026]: *Approvazione del testo unico delle disposizioni
  legislative in materia di adempimenti e accertamento e disposizioni di coordinamento e correttive relative
  ai testi unici di cui all'articolo 21, comma 1, della legge 9 agosto 2023, n. 111*. **G.U. S.G. n. 181 del
  06/08/2026, Suppl. Ordinario n. 28** (⚠️ **non** «28/L»: rettifica del 12/08/2026), cod. red. **26G00160**.
  **Entrata in vigore del provvedimento: 07/08/2026.**
- **L'art. 4** modifica il D.Lgs. 123/2025 (TU registro) e le relative tariffe e si articola in **cinquantasei
  lettere, da a) a ggg)** [PRIMARIA: letto integralmente il 18/08/2026 via lo schema `caricaArticolo` della
  G.U.]. Lettere che toccano la materia successoria:
  - **lett. m) n. 2** — art. 50 del D.Lgs. 123/2025: «*il comma 8 è abrogato*»; **lett. q) n. 2** — art. 102:
    «*il comma 4 è soppresso*». Sono **esattamente** le due disposizioni già travolte dai capi 4 e 5 del
    dispositivo di **C.Cost. 89/2026**: **doppia caducazione convergente** con due tecniche diverse
    (incostituzionalità *erga omnes* dal 04/06/2026 sui rapporti non esauriti; abrogazione espressa dal
    07/08/2026). **Nessun conflitto interpretativo residuo** — ma la *causa* va citata correttamente a seconda
    della data-evento. Nota: quelle norme non erano comunque ancora operative (efficacia differita al
    1/1/2027).
  - **lett. u)** — art. 115, co. 1: «*il certificato di morte*» → «*la **dichiarazione sostitutiva** di
    certificazione di morte*»; «*il certificato di stato di famiglia*» → «*la **dichiarazione sostitutiva** di
    stato di famiglia*»; **co. 3 abrogato**.
  - **lett. t)** — art. 114, co. 1: **lettera e) soppressa** (l'elenco dei documenti perde una voce).
  - **lett. s), z), bb)** — artt. 112, 120, 133: i rinvii agli **artt. 34 e 35 del TUS 346/1990** diventano
    rinvii agli **artt. 309 e 310** del nuovo TU adempimenti e accertamento.
  - **lett. aa)** — art. 127, co. 1: «*le aliquote*» → «*l'aliquota e la franchigia*».
- 🎯 **Rilievo operativo — è un drift DIFFERITO, con la data addosso**: **oggi non cambia nulla** di ciò che si
  deposita. **Dal 1/1/2027** la dichiarazione di successione non allega più *certificato* di morte e
  *certificato* di stato di famiglia ma le **dichiarazioni sostitutive**. Verificato in negativo che l'art. 4
  **non tocca gli artt. 204-205** del D.Lgs. 123/2025 e non contiene occorrenze di «1° gennaio 2027»: la
  decorrenza **non è stata prorogata di nuovo**.
- ⚠️ **Riserva dichiarata (debito aperto)**: l'art. 9 del 141/2026 fissa l'**entrata in vigore** al 07/08/2026
  (letto), ma la clausola di **efficacia differita al 1/1/2027 dell'intero testo unico allegato** (presumibilmente
  nell'ultimo articolo dell'allegato) **non è stata letta**. Il pattern «entrata in vigore immediata / efficacia
  2027» è confermato per il gemello D.Lgs. 123/2025; per il 141/2026 **non va citato come accertato**.
- ⚠️ **Flag di fonte, valido al 19/08/2026**: **normattiva non ha ancora recepito il 141/2026** nelle schede di
  D.Lgs. 123/2025 e 139/2024, che portano «*ultimo aggiornamento all'atto pubblicato il 03/06/2026*» — data
  che coincide con la pubblicazione in G.U. di C.Cost. 89/2026. Quelle schede **non sono ferme per inerzia**:
  sono aggiornate *fino a e includendo* la sentenza, e **manca il recepimento del correttivo di agosto**. Chi
  cita oggi l'art. 50 o l'art. 102 del 123/2025 da normattiva cita una versione **non coordinata**.

---

## 3. LOCAZIONI
<!-- tag: materia=locazioni -->

### 3.1 Disciplina sostanziale
<!-- tag: materia=locazioni -->
- L. 392/1978 (non abitative) e L. 431/1998 (abitative): in larga parte invariata.

### 3.2 Convalida di sfratto — Correttivo D.Lgs. 164/2024
<!-- tag: materia=locazioni -->
- ✅ In caso di opposizione del conduttore: **mutamento del rito** verso il **rito locatizio** (art. 447-bis CPC), salvo applicabilità del semplificato 281-decies; verificare art. 667 CPC vigente. Competenza **funzionale inderogabile** del luogo dell'immobile (art. 661).
- ✅ **Decreto ingiuntivo contestuale** per i canoni scaduti (art. 664), provvisoriamente esecutivo, su richiesta del locatore.

### 3.3 Termine di grazia (art. 55 L. 392/78)
<!-- tag: materia=locazioni -->
- ✅ Su istanza del conduttore, termine max **90 giorni** per sanare la morosità; la sanatoria in udienza
  può avvenire **per non più di 3 volte nel quadriennio** (4 volte, con termine fino a **120 giorni**, se
  la morosità dipende dalle precarie condizioni economiche qualificate del co. 5). ⚠️ Corretto il
  12/07/2026 su testo vigente normattiva: la versione precedente di questa voce ("una sola concessione nel
  quadriennio") era ERRATA.

### 3.4 Cedolare secca
<!-- tag: materia=locazioni -->
- Aliquote **21%** (canone libero) / **10%** (concordato in comuni ad alta tensione, L. 431/98 art. 2 c. 3).

### 3.5 Locazioni brevi/turistiche — CIN
<!-- tag: materia=locazioni -->
- ✅ **CIN** (Codice Identificativo Nazionale, art. 13-ter D.L. 145/2023 conv. L. 191/2023): registrazione ed esposizione obbligatorie su ogni annuncio.

### 3.6 Canoni concordati
<!-- tag: materia=locazioni -->
- Contratti tipo concordati (art. 2 c. 3 L. 431/98), durata 3+2; **attestazione di rispondenza** per i benefici fiscali.

---

## 4. IMMIGRAZIONE
<!-- tag: materia=immigrazione -->

### 4.1 Decreto Cutro — D.L. 20/2023 conv. L. 50/2023
<!-- tag: materia=immigrazione -->
- ✅ **Protezione speciale ristretta** (art. 19 c. 1.1 TUI modificato: eliminato il riferimento autonomo a "vita privata e familiare"); resta il divieto di respingimento per persecuzione/tortura/trattamenti inumani e per violazione art. 8 CEDU, con interpretazione più rigorosa. Verificare letture costituzionalmente orientate recenti.
- ✅ **Procedure accelerate** (art. 28-bis D.Lgs. 25/2008): termine ricorso ridotto a **14 giorni** (art. 35-bis c. 2); **effetto sospensivo NON automatico** (c. 3), da richiedere al giudice (decisione entro 5 gg).

### 4.2 Paesi di origine sicuri — D.L. 158/2024 conv. L. 187/2024
<!-- tag: materia=immigrazione -->
- ✅ Dopo CGUE 04/10/2024 (C-406/22), elenco adottato **con legge**. Il giudice può disapplicare la qualifica se non rispetta i criteri della dir. 2013/32/UE (art. 37, all. I). Verificare elenco aggiornato e pronunce SS.UU. 2024-2025.

### 4.3 Protocollo Italia-Albania — L. 14/2024
<!-- tag: materia=immigrazione -->
- ✅ Trattenimento extraterritoriale per procedure accelerate di frontiera; provvedimenti di non convalida (Trib. Roma sez. immigrazione, 2024) e sviluppi 2025-2026 da verificare.

### 4.4 Permessi di soggiorno
<!-- tag: materia=immigrazione -->
- ✅ "Protezione umanitaria" abolita nel 2018 (D.L. 113/2018) → "protezioni speciali" oggi ristrette. Conversioni: art. 32 c. 3-bis D.Lgs. 25/2008 e art. 6 c. 1-bis TUI, caso per caso.

### 4.5 Decreto Flussi — D.L. 145/2024 conv. L. 187/2024
<!-- tag: materia=immigrazione -->
- Nulla osta al lavoro, click-day, quote annuali (DPCM). Verificare le quote vigenti.

### 4.6 Rito processuale immigrazione
<!-- tag: materia=immigrazione -->
- ✅ Rito **camerale** (art. 737 CPC) dinanzi al Tribunale, **sezione specializzata immigrazione**; decreto non reclamabile in appello (art. 35-bis c. 13); ricorso per Cassazione entro 30 gg.

### 4.7 Contrasto all'immigrazione irregolare — D.L. 28/03/2025 n. 37 conv. L. 23/05/2025 n. 75
<!-- tag: materia=immigrazione -->

> **Lacuna del ground truth colmata il 08/08/2026**: il changelog copriva il decreto Cutro (20/2023) e i paesi
> sicuri (187/2024) e **si fermava lì**. Fra il 2023 e oggi c'era **almeno un intervento non tracciato**, in
> una materia a volatilità ALTA. Contenuto ricostruito sul **dossier dei Servizi Studi della Camera dei
> deputati** (fonte istituzionale, agg. 13/05/2025) — il testo del decreto **non è stato letto articolo per
> articolo**: verificare live prima di spenderlo in un ricorso.

- **Estremi**: *Disposizioni urgenti per il contrasto dell'immigrazione irregolare*, G.U. 28/03/2025, cod. red.
  **25G00050**, in vigore **29/03/2025**; conv. con modif. dalla **L. 23/05/2025 n. 75**, G.U. S.G. n. 118 del
  23/05/2025 (approvazione definitiva del Senato il 20/05/2025).
- Contenuto rilevante per lo Studio:
  - **estende la categoria** di persone conducibili nelle strutture di trattenimento in **Albania** (Protocollo
    6/11/2023, ratificato con L. 14/2024), includendo i destinatari di provvedimenti di trattenimento
    **convalidati o prorogati**;
  - salva la facoltà di **trasferimento in altro centro** senza che venga meno il trattenimento né serva nuova
    convalida;
  - consente la **permanenza in Albania anche dopo la domanda di asilo** se vi sono fondati motivi per
    ritenerla **dilatoria**;
  - in caso di **mancata convalida** con domanda sospettata di essere dilatoria, consente un **nuovo
    provvedimento di trattenimento** per altro motivo di legge;
  - 🎯 **estende l'applicazione della procedura accelerata** di esame delle domande di asilo **alla frontiera**;
  - **proroga al 2026** la facoltà di deroga per realizzazione/localizzazione/ampliamento dei **CPR**.
- ➜ **Perché non è una curiosità**: le ultime due voci toccano diritto processuale che lo Studio usa —
  convalida del trattenimento e **procedura accelerata alla frontiera**, cioè il presupposto dei ricorsi ex
  **art. 35-bis D.Lgs. 25/2008** e dei termini dimezzati. Una scheda che ragiona sul Cutro 2023 senza il
  37/2025 lavora su un impianto **superato di un anno**.
- **C.Cost. sent. n. 40/2026** (dep. 27/03/2026) [PRIMARIA: scheda-pronuncia letta il 03/08/2026]: norma
  impugnata l'**art. 6, co. 2-bis, D.Lgs. 142/2015**, introdotto dall'art. 1, co. 2-bis, lett. a), del D.L.
  37/2025 (permanenza nel CPR del richiedente dopo la **mancata convalida**, fino alla decisione sul nuovo
  trattenimento disposto dal questore). Esito: **inammissibilità con monito espresso al legislatore** — «*l'
  inammissibilità delle questioni non esime questa Corte dal riconoscere la necessità che il legislatore
  intervenga a rivedere la disciplina in materia*» (richiamo a sent. 275/2017). ➜ La norma **resta in
  vigore**: si cita come **precedente di monito** in argomentazione, **mai** come base di illegittimità.

---

## 5. SOCIETARIO / CRISI D'IMPRESA
<!-- tag: materia=societario -->

### 5.1 CCII — D.Lgs. 14/2019 (15/07/2022) e correttivi (D.Lgs. 83/2022, 136/2024)
<!-- tag: materia=societario -->
- ⛔ Citare il **R.D. 267/1942** ("legge fallimentare") come vigente (salvo procedure pendenti pre-15/07/2022).
- ✅ **Liquidazione giudiziale** (artt. 121 ss. CCII) al posto del "fallimento"; debitore "in liquidazione giudiziale"; resta il curatore nel quadro CCII.
- ✅ **Concordato preventivo** (artt. 84 ss.): distinzione **continuità** (art. 84 c. 2) vs **liquidatorio** (c. 4, apporto esterno ≥10% e soddisfazione ≥20% chirografari).
- ✅ **Composizione negoziata** (artt. 12-25-undecies): volontaria, esperto indipendente, piattaforma telematica; sbocchi incl. concordato semplificato per la liquidazione (art. 25-sexies).
- ✅ **Adeguati assetti art. 2086 c.c. c. 2**: dovere di assetto organizzativo/amministrativo/contabile adeguato; violazione → responsabilità amministratori (2476 SRL, 2392-2395 SPA).

### 5.2 Operazioni straordinarie transfrontaliere — D.Lgs. 19/2023 (03/07/2023)
<!-- tag: materia=societario -->
- ✅ Disciplina organica di trasformazioni/fusioni/scissioni transfrontaliere UE (dir. 2019/2121): progetto, certificato preliminare notarile, efficacia con iscrizione nello Stato di destinazione.

### 5.3 SRLS e capitale ridotto
<!-- tag: materia=societario -->
- ✅ **SRLS art. 2463-bis c.c.**: capitale 1-9.999,99 €, modello standard non derogabile, solo persone fisiche. SRL ordinaria con capitale < 10.000 €: art. 2463 c. 4 (accantonamento 1/5 utili).

### 5.4 Whistleblowing — D.Lgs. 24/2023
<!-- tag: materia=societario -->
- ✅ Sostituisce la L. 179/2017: obbligati enti pubblici ed enti privati con ≥50 lavoratori (o settori specifici, o MOG 231 anche sotto 50); canale interno + procedura; sanzioni ANAC fino a 50.000 €.

### 5.5 Modello 231 — D.Lgs. 231/2001
<!-- tag: materia=societario -->
- ✅ Catalogo reati presupposto in **continua espansione** (tributari 25-quinquiesdecies, contrabbando 25-sexiesdecies, cyber, ambientali 25-undecies, ecc.). Verificare SEMPRE l'ultima versione su normattiva prima di redigere/aggiornare un MOG.

---

## 6. NORME TRASVERSALI

- **Privacy**: GDPR Reg. UE 2016/679 + D.Lgs. 196/2003 adattato dal D.Lgs. 101/2018 ("informativa ex artt. 13-14 GDPR").
- **Cartabia penale**: D.Lgs. 150/2022 (riti alternativi, giustizia riparativa, procedibilità a querela ampliata) — per atti penali rivedere termini e riti.

### 6.1 Equo compenso e deontologia — due piani da non confondere
<!-- tag: materia=deontologia|parcella -->

- **Piano civilistico — invariato**: **L. 49/2023** (clienti "forti"); nullità delle clausole con compensi non
  equi rispetto al DM 55/2014 mod. DM 147/2022.
- 🆕 **Piano disciplinare — cambiato nel 2026** [PRIMARIA: G.U. letta il 31/07/2026]: l'**art. 25-bis del
  Codice deontologico forense** («Violazione delle disposizioni in materia di equo compenso») è stato
  **riscritto**, **esplicitando i soggetti ai quali si applica**. Veicolo: **delibera CNF n. 959 del
  23/01/2026** (all'esito della consultazione ex art. 35, co. 1, lett. d, L. 247/2012), pubblicata come
  **comunicato CNF 26A00480 in G.U. Serie Generale n. 29 del 05/02/2026**; il Codice è in vigore nel testo
  aggiornato **dal 7 aprile 2026**; perimetro applicativo chiarito dalla **Circolare CNF n. 1-C-2026
  dell'08/04/2026**.
- ⚠️ **Prima di spendere l'argomento *disciplinare* verso un cliente "forte"** va letta la Circolare 1-C-2026
  (perimetro soggettivo). Nessuna tabella parametrica è toccata: `parcella/tabelle-vigenti.md` resta valido.
- 🔴 **Nota anti-confusione**: il decreto CNF sul **Codice deontologico** pubblicato in **G.U. n. 29 del
  05/02/2026** è atto **distinto** e **non tocca i parametri di liquidazione**. Falso positivo ricorrente
  nelle ricerche sui «parametri forensi 2026».

### 6.2 Riforma dell'ordinamento forense — L. 28/07/2026 n. 137 (delega, in vigore 16/08/2026)
<!-- tag: materia=deontologia|parcella -->

- **Estremi** [PRIMARIA, scheda ELI letta il 12/08/2026]: *Delega al Governo per la riforma dell'ordinamento
  forense*, cod. red. **26G00153**, **G.U. Serie Generale n. 177 del 01/08/2026**, **in vigore 16/08/2026**.
  Iter: Camera 27/05/2026, approvazione definitiva del Senato **22/07/2026** (A.S. 1917); formula di
  promulgazione «*Data a Roma, addì 28 luglio 2026*».
  - ❌ **Da non riproporre**: la citazione «L. 137/2026 del 27/07/2026, cod. red. 26G00148». Il codice 26G00148
    appartiene alla **L. 16 luglio 2026 n. 132** (giornata nazionale della memoria), atto del tutto estraneo:
    era una conflazione da snippet, sciolta su primaria il 09/08/2026.
- **Delega**: decreti legislativi **entro sei mesi** dall'entrata in vigore → **termine 16/02/2027** (con
  scorrimento di 30 giorni se il termine per i pareri parlamentari scade a ridosso); su proposta del Ministro
  della giustizia, **sentito il CNF**; parere delle Commissioni entro 30 giorni; correttivi entro 12 mesi.
- 🎯 **Il punto che tocca lo Studio — art. 2, co. 1, lett. g)** [PRIMARIA: testo dell'art. 2 letto su
  normattiva il 19/08/2026]:
  - **n. 1**: libera pattuizione salvi i casi di **equo compenso**; compenso adeguato a quantità e qualità
    della prestazione, anche parametrato al raggiungimento degli obiettivi, fermi l'**art. 1261 c.c.** e la
    proporzionalità ex **art. 2233 c.c.**;
  - **n. 2**: si delega a prevedere che «*il Ministro della giustizia, su proposta del Consiglio nazionale
    forense, adotti **ogni due anni** un decreto contenente i parametri per il calcolo del compenso
    dell'avvocato, da applicare in assenza di pattuizione scritta o comunque consensuale del compenso nonché
    nei casi di liquidazione giudiziale dello stesso*». ➜ **Il successore del DM 147/2022 non arriverà più
    come decreto isolato**: passerà da qui, con cadenza **biennale strutturale**;
  - **n. 3**: **solidarietà passiva** di tutti i soggetti coinvolti in un procedimento definito con accordo,
    per il pagamento del compenso agli avvocati creditori, salvo diverso accordo;
  - **n. 5**: obbligo di rimborso delle spese sostenute/anticipate e delle **spese forfetarie** nell'importo
    determinato con DM giustizia;
  - **lett. c)**: il CNF **emana e aggiorna periodicamente il codice deontologico** (si salda con §6.1).
- ⛔ **Due contenuti che la stampa dà per acquisiti e nel testo NON ci sono** (verificati sul testo in G.U. il
  02/08/2026):
  1. «il **parere di congruità** dell'Ordine costituisce **titolo esecutivo**» → l'art. 2, lett. g), n. 4 dice
     soltanto «***valutare la possibilità** di razionalizzare la disciplina dei casi di rilascio di un parere
     di congruità … al fine di agevolare il recupero dei crediti professionali*». Criterio **facoltativo e
     programmatico**;
  2. «**tariffa oraria 200-500 €**» → **non compare** nella legge delega. Il range **esiste ma appartiene al
     DM 147/2022** (per ogni ora o frazione superiore ai 30 minuti), insieme al riconoscimento della fase di
     studio all'avvocato che subentra a causa già avviata. **Citabile — ma con l'attribuzione giusta.**
- ✅ **Effetto sulle tabelle: nessuno.** Fino ai decreti delegati e al conseguente DM si liquida **solo con il
  DM 147/2022**. La solidarietà passiva (n. 3) e il rimborso forfetario (n. 5) sono **criteri di delega, non
  norme applicabili**. Al 20/08/2026 **nessuno schema attuativo** risulta pubblicato o trasmesso alle Camere
  (controlli negativi eseguiti sulle G.U. n. 189 del 17/08 e n. 190 del 18/08, sommari letti per intero).

### 6.3 Esame di avvocato — contributo di partecipazione (D.L. 100/2026 e DM 3 agosto 2026)
<!-- tag: materia=deontologia, ambito=manutenzione -->

- **DM Giustizia-MEF 3 agosto 2026**, *Determinazione delle modalità di versamento del contributo per la
  partecipazione all'esame di avvocato*, cod. red. **26A04073**, **G.U. Serie Generale n. 186 del 12/08/2026**,
  pag. 59 [PRIMARIA: testo integrale letto il 15/08/2026 via lo schema `caricaArticolo` della G.U.]:
  - **Art. 1**: le spese per la sessione dell'esame di Stato sono «*poste a carico del candidato nella misura
    forfetaria di **euro 62,00***» ai sensi dell'**art. 1, comma 18, del D.L. 12 giugno 2026, n. 100**, e sono
    versate **all'entrata del bilancio dello Stato, capitolo 2413 art. 14**, mediante **pagamento digitale
    tramite PagoPA** (art. 5 CAD, D.Lgs. 82/2005). Il co. 2 **sostituisce l'art. 1 del DM Giustizia-MEF 16
    settembre 2014** e si applica **a decorrere dalla sessione del corrente anno**.
  - **Art. 2**: entrata in vigore il giorno successivo alla pubblicazione → **13 agosto 2026**. Firmato Nordio
    e Giorgetti.
- ✅ **L'importo di € 62 fa prova** e si cita con questi estremi (fino al 15/08/2026 circolava solo su fonte
  secondaria e non era utilizzabile).
- ⚠️ Il **D.L. 12 giugno 2026, n. 100** (*Misure urgenti in materia di giustizia e per l'attuazione del Patto
  dell'Unione europea sulla migrazione e l'asilo del 14 maggio 2024*), che riforma l'esame di abilitazione,
  **non è ancora tracciato nel merito**: ne è attestato l'art. 1 co. 18 dal preambolo del DM. Prove,
  commissioni e resto della disciplina: **da leggere prima dell'uso**.

### 6.4 Testi unici fiscali 2026 — esistenza attestata, contenuto NON letto
<!-- tag: materia=successioni -->

> ⚠️ **[ESTREMI PRIMARI, CONTENUTO NON LETTO]** — emersi il 18/08/2026 dalla lettura integrale dell'art. 4 del
> D.Lgs. 141/2026, che vi rinvia ripetutamente. Estremi accertati su primaria il 19/08/2026. **Fanno prova
> dell'esistenza, non del contenuto: non citabili nel merito.** Rilevanza per lo Studio: **minima e indiretta
> fino al 1/1/2027** (profili fiscali accessori in pratiche successorie, societarie e contrattuali; nessun
> impatto su rito, termini o istituti civili).

- **D.Lgs. 19 giugno 2026, n. 117** — *Testo unico delle disposizioni legislative in materia di imposte sui
  redditi*: **G.U. n. 152 del 03/07/2026, Suppl. Ord. n. 26**, cod. red. **26G00131**; entrata in vigore
  **04/07/2026**. Prende il posto del **d.P.R. 917/1986 (TUIR)**.
- **D.Lgs. 19 gennaio 2026, n. 10** — *Testo unico delle disposizioni legislative in materia di imposta sul
  valore aggiunto*: **G.U. S.G. n. 24 del 30/01/2026, Suppl. Ord. n. 4**, cod. red. **26G00022**; entrata in
  vigore **31/01/2026**. Prende il posto del **d.P.R. 633/1972**.
- **D.Lgs. 5 novembre 2024, n. 173** — testo unico delle sanzioni tributarie amministrative e penali (citato
  dall'art. 4 lett. uu del 141/2026; anch'esso assente dal ground truth).
- ⚠️ **Da NON citare come accertati**: l'efficacia sostanziale **1/1/2027** e le abrogazioni (art. 376 del
  117/2026 per il d.P.R. 917/1986; artt. 170-171 del 10/2026 per il d.P.R. 633/1972 e il D.L. 331/1993).
  Poggiano su **fonti secondarie concordi**, non sugli articoli di decorrenza, che **non sono stati letti**.

---

## 7. GIURISPRUDENZA — pattern di errore frequenti
Il modello tende a: **inventare numeri di sentenza** plausibili (sospetto verso "Cass. civ. sez. III, [data], n. [5 cifre]" non confermata su Italgiure); confondere **SS.UU. con sezioni semplici**; spacciare pronunce di merito per Cassazione; **applicare orientamenti superati** (responsabilità medica, danno non patrimoniale, prescrizione: evoluzione continua); riferire **massime parziali/estrapolate**. Mitigazione: lente **L3** in [`../protocolli/lenti-verifica.md`](../protocolli/lenti-verifica.md) (verifica datata: esistenza + attualità dell'orientamento alla data; superamento da SS.UU./Corte Cost./CGUE/sopravvenienza normativa/revirement consolidato).

### 7.1 🔴 I due registri della Corte costituzionale — trappola strutturale, non incidente

**Il registro ordinanze (atti di promovimento) e il registro pronunce hanno numerazioni autonome.** Lo stesso
numero identifica due atti diversi. Caso reale, verificato il 12/08/2026 su primaria:

- **`reg. ord. n. 39/2026`** = ordinanza di rimessione del **Tribunale di Livorno**, art. 8 L. 604/1966;
- **`sent. n. 39/2026`** = pronuncia della Corte del **27/03/2026** sull'**art. 23-quater D.L. 137/2020**
  (misure emergenziali Covid) — **materia del tutto estranea**.

🔒 **Regola: mai risolvere il numero senza dire di quale registro si parla.** Nelle schede e negli atti scrivere
sempre `reg. ord. n. X/AAAA` oppure `sent./ord. n. X/AAAA`, mai «Corte cost. X/AAAA» nudo.

🔒 **Corollario, imparato a caro prezzo (due errori di attribuzione in una settimana, sullo stesso filone):**
una **rimessione entra in watchlist o in una scheda solo dopo lettura su fonte primaria**. Gli snippet
indicizzati attribuiscono numeri di registro sbagliati con disinvoltura: il 13/08 la ord. 131/2026 era stata
attribuita alla rimessione di Livorno (in realtà decide quella di **Padova, reg. ord. 212/2025**); il 19/08 è
emerso che la **reg. ord. 41/2026**, data per pendente sulle tutele crescenti, è del **Trib. di Campobasso sez.
immigrazione** e riguarda la **cittadinanza iure sanguinis**.

### 7.2 Falsi positivi schedati — da riconoscere a vista e scartare

| Falso positivo | Che cos'è davvero | Dove ricompare |
|---|---|---|
| «SS.UU. su fideiussione di **confidi minore**» | **SS.UU. 15/03/2022 n. 8472**: riserva di attività su credito **non bancario**. Materia diversa dallo schema ABI | ricerche «fideiussioni SS.UU.» |
| «le SS.UU. confermano la nullità parziale…» (2026) | Riferito in realtà alla **preesistente SS.UU. 41994/2021** | titoli di rassegna |
| **SS.UU. n. 12704/2026** (5/5/2026) come pronuncia sul **comporto** | Riguarda la **giurisdizione sulle ore di sostegno scolastico** | ricerche «comporto SS.UU. 2026» |
| «Parametri forensi, decreto firmato» (fiscoetasse) | Articolo del **30/08/2022**, riferito al **DM 147/2022** stesso. Riemerge in cima a ogni ricerca | ricerche «nuovo DM parametri» |
| «Parametri forensi **2026**» (avvocatoandreani / professionegiustizia) | **Calcolatori aggiornati all'anno corrente**, non un nuovo DM | idem |
| AVOC.IT, *Compensi Avvocato 2026* | Attribuisce i parametri a un inesistente «**DM 82/2022**», tabelle non conformi | idem — **fonte da escludere** |
| «Modulo di controllo AdE 2.3.1 rilasciato il **17 marzo 2026**» | La data letta sulla tabella dell'Agenzia è l'**11/03/2026** | rassegne di software house |
| «Via libera della Commissione UE ai bonus Giovani e Donne» | Comunicato del **31/01/2025**, misura diversa e anteriore all'art. 4 D.L. 62/2026 | ricerche sull'esonero stabilizzazioni |

⚠️ **Saldatura da non fare**: l'**esonero contributivo per la stabilizzazione** (art. 4 D.L. 62/2026, finestra
1/8–31/12/2026) e la **scadenza della causale individuale** (31/12/2026) sono **istituti distinti**: la
coincidenza di date è casuale. Sull'esonero, per di più, c'è un punto da dire bene al cliente: l'art. 4, co. 5,
ne subordina l'efficacia all'**autorizzazione della Commissione europea**, che **non è intervenuta**; la misura
è operativa perché l'**INPS, con circolare n. 72 del 03/07/2026** (§ 9, letta integralmente l'11/08/2026),
sostiene che l'autorizzazione non serva, non essendo la misura sussumibile fra quelle dell'**art. 107 TFUE**
(non selettiva). ⚠️ **La circolare argomenta ex art. 107, non ex art. 108 par. 3**: la stringa «articolo 108»
non vi compare — se lo si scrive a un cliente va citato l'articolo giusto. Domande aperte dal **29/07/2026**
(msg. INPS n. 2518, letto su primaria il 13/08/2026: esonero 100%, esclusi INAIL, per stabilizzazione di
under 35 mai occupati a tempo indeterminato, fino a 24 mesi, massimale 500 €/mese). **Rischio da dichiarare:
recupero retroattivo** se la qualificazione «non aiuto di Stato» risultasse errata.

---

## 8. Fonti per la verifica
In ordine di priorità: 1) **normattiva.it** (testi consolidati, vigenza, multivigenza "vigente al"); 2) **italgiure.giustizia.it** (Cassazione); 3) **gazzettaufficiale.it** (norme recenti); 4) **eur-lex.europa.eu** (UE); 5) **cortecostituzionale.it**; 6) giustizia-amministrativa.it; 7) brocardi.it (pre-verifica); 8) altalex.com / diritto.it (commenti). Se la fonte primaria non conferma → HARD-FAIL anche se la secondaria sembra confermare. Per pagine JS → Claude in Chrome.

**Come si aprono davvero queste fonti** — acquisizioni operative dei giri della Sentinella, in
[`../protocolli/nucleo-verifica.md` §3-septies](../protocolli/nucleo-verifica.md): schema `caricaArticolo`
della G.U. (rende superfluo il PDF), permalink URN di normattiva via `scripts/fonti_fetch.py`, regola mite sul
ritentativo prima di dichiarare una pagina illeggibile.

---

## 9. Manutenzione
Aggiornare **manualmente** a ogni riforma rilevante: questo file è la rete di sicurezza contro le allucinazioni del modello, che non lo aggiorna da sé. La **Sentinella normativa** ([`../../skills/sentinella-normativa/`](../../skills/sentinella-normativa/)) propone gli aggiornamenti (tell-only) e aggiorna il sidecar `changelog-riforme.meta.json`; l'avvocato approva. Mantenere la data "Ultimo controllo" in cima e revisionare le voci ad alta volatilità secondo `vigenza-watchlist.md`.

**Dove vive il lavoro in corso.** Il **debito di verifica** della Sentinella — cosa resta da leggere su
primaria, con scadenze e stato — sta in [`sentinella-debito.json`](sentinella-debito.json), non in coda
all'ultimo drift-report. La **narrazione datata** di ogni giro sta in [`drift-reports/`](drift-reports/); la
**cronaca per-voce** del sidecar in [`note-storiche-sidecar.md`](note-storiche-sidecar.md).

⚠️ **Lezione di metodo da tenere presente quando si aggiorna questo file** (emersa due volte in due giri, il
9 e il 10/08/2026, con ritardi di sei settimane e di due anni): *una verifica può essere fresca e incompleta
insieme*. In entrambi i casi il giro precedente aveva **riletto l'articolo per la regola che cercava** e
trascritto il resto a memoria — senza vedere una nota di aggiornamento o un periodo aggiunto **due righe più
sotto, nello stesso comma**. Un gate a date non protegge da questo: solo la **rilettura del testo**. Per
questo il sidecar porta il campo `verificato_su`, che registra **cosa** copre una verifica e non solo quando.
