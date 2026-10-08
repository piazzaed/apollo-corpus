# Changelog Normativo — Successioni e DEAS

**Fonte di verità per lo swarm di verifica.** Ogni norma, termine, importo o regola citati nella Scheda DEAS devono essere coerenti con questo changelog. In caso di discrepanza, l'agente di verifica solleva un rilievo 🔴.

**Ultimo aggiornamento manuale**: vedere la data in fondo. Se sono passati più di ~30 giorni, eseguire/attendere il task di monitoraggio normativo (vedi SKILL.md → "Monitoraggio normativo").

---

## ⚠️ DISCRIMINANTE FONDAMENTALE: data di apertura della successione

Quasi tutte le regole fiscali dipendono dalla **data del decesso**. Lo spartiacque attuale è **1° gennaio 2025** (riforma D.Lgs. 139/2024). Determinare SEMPRE per prima cosa se il decesso è **ante 1/1/2025** o **dal 1/1/2025**.

| Aspetto | Decesso ANTE 1/1/2025 | Decesso DAL 1/1/2025 |
|---|---|---|
| Imposta di successione | Liquidata dall'**Ufficio** (avviso di liquidazione) | **Autoliquidata** dal contribuente in dichiarazione (quadro EF Sez. V-bis) |
| Coacervo successorio (donatum nel calcolo successione) | Questione dibattuta; DEAS lo calcolava per prudenza | **ABOLITO**: le donazioni NON si sommano all'asse né erodono la franchigia in successione |
| Quadro EF Sez. V-bis (EF18-bis/ter) | **Non si compila** | **Si compila** (imposta calcolata + pagamento) |
| Termine versamento imposta successione | Entro 60 gg dalla notifica avviso ufficio | Entro **90 gg** dal termine di presentazione (12 mesi + 90 gg) |
| Tassa servizi ipotecari/catastali | €90 / €35 senza volture (fino 31/12/2024) | **€120** / **€65** senza volture, per circoscrizione |
| Tributi speciali attestazione presentazione | €12,40 + €0,62/pagina | **€16,00 fissi** |
| Rigo EF17 Formalità ipotecarie | Presente | **Eliminato** (non più dovuto) |

---

## D.Lgs. 18 settembre 2024, n. 139 — Riforma imposte indirette (in vigore dal 1/1/2025)

Si applica alle **successioni aperte dal 1° gennaio 2025**. Chiarimenti: **Circolare AdE n. 3/E del 16 aprile 2025**.

### 1. Autoliquidazione dell'imposta di successione
- L'imposta di successione **non è più liquidata dall'Ufficio**: è calcolata e versata dal contribuente in base alla dichiarazione.
- **Codice tributo F24: 1539** — "Successioni – Imposta sulle successioni – autoliquidazione".
- **Versamento**: entro **90 giorni dal termine di presentazione** della dichiarazione (termine presentazione = 12 mesi dall'apertura; quindi al massimo 12 mesi + 90 giorni dal decesso).
- **Rateizzazione**: acconto minimo **20%** dell'imposta; la parte residua (imposta da versare − acconto) è rateizzabile solo se ≥ **€1.000**:
  - residuo **fino a €20.000** → max **8 rate trimestrali**;
  - residuo **oltre €20.000** → max **12 rate trimestrali**.
- **Imposta non dovuta / imposta minima** (EF18-bis) — due meccanismi distinti nel tracciato:
  - **flag "Imposta non dovuta"** (in alternativa ai campi dell'imposta calcolata): quando non è dovuta imposta (asse nel perimetro di franchigie/esenzioni); obbligatorio nel caso trust con disabilità (presentatore carica 9 + casella disabilità su tutti i righi EA). Gli altri campi della sezione non si compilano;
  - **importo ≤ €10,00**: NON passa dal flag — il campo "Imposta da versare" si azzera (resta compilata la struttura dell'imposta calcolata).

### 2. Coacervo
- **Coacervo successorio ABROGATO** (art. 8, c. 4, TUS soppresso): per le successioni dal 1/1/2025 le donazioni in vita **non** rientrano nel calcolo dell'imposta di successione né erodono la franchigia successoria. È la conferma normativa dell'orientamento Cass. 26050/2016 e 24940/2016.
- **Coacervo donativo**: resta in vigore ai soli fini dell'imposta di **donazione** (erosione della franchigia tra più donazioni dallo stesso donante allo stesso beneficiario).
- **Conseguenza operativa**: nel tracciato SUC13 v14 (modello 2025) il quadro **ES non esiste più** (i quadri trasmissibili sono solo Frontespizio, EA, EB, EC, ED, EE, EF, EG, EH, EI, EL, EM, EN, EO, EP, EQ, ER). Le donazioni pregresse restano rilevanti come dato informativo: coacervo per i decessi ante 2025 (prassi previgente, DEAS lo calcolava), riduzione art. 25 c. 1 (estremi della donazione/successione precedente), profili civilistici (collazione, lesione di legittima) e imposta di donazione — ma NON determinano più maggiore imposta di successione per i decessi dal 2025.

### 3. Aliquote e franchigie (CONFERMATE, ora codificate nel TUS)
| Rapporto col de cuius | Aliquota | Franchigia per beneficiario |
|---|---|---|
| Coniuge / unito civilmente / parenti in linea retta (figli, ascendenti) | 4% | €1.000.000 |
| Fratelli / sorelle | 6% | €100.000 |
| Altri parenti fino al 4° grado; affini in linea retta; affini in linea collaterale fino al 3° grado | 6% | nessuna |
| Tutti gli altri soggetti | 8% | nessuna |
| Portatori di handicap grave (L. 104/92) | come da rapporto | €1.500.000 |

### 4. Trust testamentario
- **Successioni aperte dal 1/1/2025** (il discrimine del tracciato è la data del decesso, non la data di istituzione del trust): si applica l'autoliquidazione; il trustee compila il quadro EF Sez. V-bis indicando imposta e modalità di pagamento. L'imposta è di regola dovuta al trasferimento ai beneficiari finali, ma il trustee può **optare per il pagamento anticipato** (rigo EF18-ter, "Pagamento anticipato trust"). Optando per l'anticipo, NON si tiene conto di riduzioni/esenzioni (verifica rinviata al trasferimento finale), e la fruizione di esenzioni/agevolazioni è preclusa anche al successivo trasferimento.
- **Successioni aperte ante 1/1/2025**: l'imposta continua a essere liquidata dall'Ufficio; nella Sez. V-bis il trustee (presentatore con carica 9) può indicare solo il campo "Pagamento anticipato trust".
- **Casi in cui NON è utilizzabile il modello telematico** (serve Modello 4 cartaceo presso l'ufficio territoriale): trustee non persona fisica; trustee che coincide con un beneficiario; trust senza beneficiari individuati o individuabili (trust di scopo "puro"); presenza, oltre al trust e ai suoi beneficiari, di altri soggetti destinatari di beni nel testamento.

### 5. Imposte ipotecaria e catastale
- Misura ordinaria: **2%** (ipotecaria) + **1%** (catastale) sul valore catastale.
- Prima casa: **€200 + €200** fissi.
- Misura fissa per successioni dal 1/1/2017 in presenza dei presupposti (anche a prescindere da disabilità grave, come da modello 2025).

---

## Modulo di controllo AdE e specifiche tecniche — stato al 3 agosto 2026

**Verificato sulle pagine ufficiali dell'Agenzia delle Entrate il 3/8/2026.**

| Elemento | Versione vigente | Note |
|---|---|---|
| **Specifiche tecniche SUC13** | **2 luglio 2025** (pagina aggiornata il 15/7/2025) — v14 | È l'ultima pubblicata: **nessuna specifica 2026**. Gli XSD ufficiali di questo pacchetto sono inclusi nella skill (`specifiche-suc13/xsd/`) e usati per generare e validare il file telematico |
| **Modulo di controllo** | **2.3.1 dell'11 marzo 2026** (aggiornamento uffici) | Precedente: 2.3.0 del 15/7/2025, che ha introdotto il **calcolo automatico dell'imposta di successione** nel modulo. Uso obbligatorio **dal 26/3/2026** |
| **Modello e istruzioni** | Provv. AdE 13/2/2025; **istruzioni aggiornate al 15/7/2025** | Il provvedimento resta quello del 13/2/2025 |

🔎 **La doppia data delle specifiche, spiegata una volta per tutte** (chiusa su primaria il 2/8/2026, dopo quattro giri di dubbio): **2 luglio 2025 è la data del documento**, **15 luglio 2025 è la data di pubblicazione/aggiornamento della pagina AdE**. Il file pubblicato è `Specifiche_SUC13_20250702.pdf` (+ `SUC13_20250702.zip`), cioè **esattamente quello recepito in questa skill**. Non è una revisione successiva: **non riaprire il dubbio a ogni giro**.

**Riverifiche successive** (drift-report della Sentinella):
- **modulo di controllo**: storico completo riletto sulla pagina AdE il **18/8/2026** — la 2.3.1 dell'11/3/2026 resta la più recente, **nessuna versione successiva**; corroborato dall'archivio primario degli avvisi dei Servizi Telematici AdE, che al **11/3/2026** annuncia la nuova versione e **non riporta avvisi successivi** fino al 28/7/2026 (verifica del 19/8/2026);
- **specifiche e modello**: al **19/8/2026** le due pagine AdE dedicate rendono via JavaScript e hanno restituito un guscio vuoto → **ESITO INCONCLUSO**. L'assenza di avvisi 2026 su nuovo modello/specifiche nell'archivio primario è un **forte indizio** che la v14 sia ancora l'ultima, **non una conferma diretta**.
- ⚠️ **Regola operativa sulle pagine AdE** (dopo che una diagnosi di «difetto strutturale» è stata smentita dai fatti il 15/8/2026): se una pagina AdE torna vuota, **riprovare al giro successivo** prima di dichiarare necessario il browser. Tre fallimenti identici non dimostrano un difetto architetturale — dimostrano tre fallimenti.

🔒 **Regola operativa (causa frequentissima di scarto)**: il file `.suc` va controllato **sempre con l'ultima versione pubblicata** del modulo. Con una versione precedente lo scarto è: «*Il file non risulta controllato con l'ultima versione pubblicata*». Il modulo è distribuito tramite **Desktop Telematico**, che si aggiorna automaticamente all'avvio: prima di ogni invio verificare comunque che la versione installata sia l'ultima.

### Canali di presentazione (dal 15 luglio 2025)
- **DEAS / intermediario abilitato** (Entratel): l'imposta di successione resta **autoliquidata dal contribuente** nel quadro EF Sez. V-bis.
- **Dichiarazione di successione precompilata (web)**, attiva dal **15/7/2025** sul sito AdE per il contribuente: qui il calcolo dell'imposta è eseguito dal sistema. ⚠️ Non confondere i due canali: l'"autoliquidazione automatica" descritta da alcune fonti riguarda solo la precompilata web.
- **Ufficio territoriale**: file `.DIZ` / applicazione SUC13 (SuccessioniOnLine), obbligatorio anche quando la fornitura supera i 40 MB compressi.

### Volture catastali — dal 12 gennaio 2026
- **Voltura 2.0 è dismessa**: si usa esclusivamente **Voltura Web**. Il flusso in DEAS non cambia (esportazione del file XML e importazione in Voltura Web).
- Nuova tipologia in esportazione: **«Riunione di uso, usufrutto e abitazione»**, **esente da tributi**, da usare quando la procedura automatica non abbia trattato correttamente il decesso del titolare del diritto; in caso di riunione di diritti per morte dell'usufruttuario la tipologia è selezionata automaticamente in fase di esportazione.

### Ravvedimento operoso — interessi legali per periodo (calcolo giornaliero)
Gli interessi si calcolano **giorno per giorno** con il tasso vigente in ciascun periodo:

| Periodo | Tasso legale |
|---|---|
| fino al 31/12/2023 | 5,00% |
| anno 2024 | 2,50% |
| anno 2025 | 2,00% |
| dal 1/1/2026 | 1,60% (DM MEF 10/12/2025, G.U. 289 del 13/12/2025) |

⚠️ Da non confondere con il **floor fiscale del 2,5%** usato per usufrutto/rendite (art. 17, c. 1-ter, TUS): tassi con funzioni diverse.

---

## Modello telematico — Provvedimento AdE 13 febbraio 2025 (vigente)

Sostituisce il modello approvato l'8 novembre 2023. Allegato 1 = modello e istruzioni; Allegato 2 = specifiche tecniche. DEAS recepisce integralmente.

### Frontespizio
- Nuovo campo **"Numero chiamati"** nella sezione *Beneficiari* (oltre a "Numero eredi" e "Numero legatari"). DEAS lo compila in automatico quando in EA è presente almeno un soggetto con tipologia **Chiamato (codice 3)**.

### Quadro EF
- **Sezione III** "Tassa ipotecaria" → rinominata **"Tassa per i servizi ipotecari e catastali"**. Importi dal 1/1/2025: **€120** per circoscrizione (era €90); **€65** per circoscrizione se non si dà corso alle volture (era €35).
- **Sezione IV Tributi speciali**: eliminato il rigo **EF17 "Formalità ipotecarie"** (non più dovuto). Attestazione di avvenuta presentazione: **€16,00 fissi** (era €12,40 + €0,62/pagina).
- **Sezione V-bis "Imposta di successione"** (solo successioni dal 1/1/2025):
  - **EF18-bis (imposta calcolata)**: 1) Imposta non dovuta [flag]; 2) Imposta [calcolata DEAS]; 3) Imposta già versata [solo sostitutiva]; 4) Credito d'imposta [L. 448/1998 art. 7 c.2; D.L. 73/2021 art. 64 c.7 Sostegni bis]; 5) Imposta da versare.
  - **EF18-ter (pagamento)**: 1) Tempistica di pagamento [contestuale / successivo entro 90 gg]; 2) Pagamento rateale [n. rate]; 3) Acconto [≥20%]; 4) Pagamento anticipato trust [flag].
- **Sezione VI Sanzioni e interessi**: nuovo rigo **EF23-bis** relativo all'imposta di successione.

### Quadro EH — Agevolazioni prima casa (Sezione II)
- Recepisce **D.L. 69/2023**. Lettera d): impegno al trasferimento dell'altra casa pre-posseduta **entro due anni dal decesso** (prima era "un anno"). Nuove opzioni alla lettera f) per chi si è trasferito all'estero (residenza/lavoro in Italia ≥ 5 anni; immobile nel comune di nascita/ultima residenza/lavoro).

### Quadro EI — Dichiarazioni per voltura (ristrutturato)
- Non più testo libero, ma due sezioni:
  - **SEZIONE I — Dichiarazione di passaggi senza Atti Legali**: il dichiarante compila una dichiarazione sostitutiva di atto notorio; documentazione allegabile in **EG8 "Altro"**; le volture vengono eseguite **con riserva** e notificate agli intestatari catastali.
  - **SEZIONE II — Cronistoria discordanza Dati Intestatario**: per ogni immobile con discordanza indicare, se atto notarile/giudiziario gli **estremi di trascrizione**, se successione gli **estremi di registrazione**.

### Quadro ER — riposizionato subito dopo il quadro EC **nella sola impaginazione di stampa del modello** (prima era in penultima pagina). Nell'ordine del tracciato XSD l'ER resta l'ultimo quadro (…EN, EO, EP, EQ, ER): cambia la stampa, non la struttura del file.

### Quadro ES — **soppresso**: non esiste nel tracciato SUC13 v14 (coerente con l'abolizione del coacervo successorio).

---

## Specifiche tecniche 21 ottobre 2019 (tuttora rilevanti)
- Dal 21/10/2019 **non** è più possibile inserire in dichiarazione fabbricati regolarmente dichiarati in Catasto ma **privi di classamento/rendita**: occorre prima richiedere l'attribuzione della rendita (ex art. 12 D.L. 70/1988). Resta il campo "Determinazione rendita": definitiva / proposta / da attribuire.
- Il diritto **"Servitù"** non è più inseribile dalle specifiche del 21/10/2019.

---

## Tasso legale e coefficienti usufrutto

Il valore di usufrutto/nuda proprietà si calcola con coefficienti legati al **tasso legale**, MA ai fini fiscali (imposte indirette) la legge fissa un **floor del 2,5%**.

| Anno decesso | Tasso legale civile | Tasso ai fini coefficienti usufrutto | Note |
|---|---|---|---|
| 2024 | 2,5% | 2,5% | Prospetto coefficienti allegato al D.Lgs. 139/2024 |
| 2025 | 2,0% | **2,5%** (floor) | Coefficienti invariati rispetto al 2024 |
| 2026 | 1,6% (DM 10/12/2025) | **2,5%** (floor) | DM MEF 24/12/2025: coefficienti **invariati**, basati sul 2,5%; multiplo rendite/pensioni = 40 |

⚠ Anche se il tasso legale civilistico è sceso, i **coefficienti usufrutto ai fini fiscali restano quelli basati sul 2,5%** per 2024-2025-2026. DEAS li applica automaticamente in base alla data di morte: verificare solo che l'**età dell'usufruttuario** alla data del decesso sia corretta.

---

## 🔴 Rendite e pensioni vitalizie — Corte cost. sent. n. 89/2026: il floor 2,5% vale anche PRIMA del 2025

**È la novità con l'effetto operativo più immediato di tutto questo changelog, e riguarda le pratiche vecchie, non quelle nuove.**

**Estremi** (testo integrale letto su `cortecostituzionale.it/scheda-pronuncia/2026/89` il 15/8/2026): **sent. n. 89 del 2026**, ECLI:IT:COST:2026:89, Pres. Amoroso, Red. Antonini; camera di consiglio e decisione **23/3/2026**, **deposito 28/5/2026**, pubblicazione in **G.U. 1ª serie speciale n. 22 del 3/6/2026**. Atti decisi: reg. ord. 210/2025 (Cass. sez. trib., ord. 11/6/2025 n. 15547).

**Dispositivo — cinque capi.** È dichiarato costituzionalmente illegittimo:
1. l'**art. 17, co. 1, lett. c), del TUS (D.Lgs. 346/1990)**, *nel testo applicabile prima* della modifica introdotta dall'art. 1, co. 1, lett. r), del D.Lgs. 139/2024, **nella parte in cui non prevede che, per determinare il valore della rendita vitalizia, non possa assumersi un saggio legale d'interesse inferiore al 2,5%**;
2. in via consequenziale, l'**art. 46 del d.P.R. 131/1986** (imposta di registro), stessa parte, stesso floor;
3. in via consequenziale, l'**art. 9, co. 4, del D.Lgs. 139/2024** (disciplina transitoria);
4. in via consequenziale, l'**art. 102, co. 4, del D.Lgs. 123/2025**;
5. in via consequenziale, l'**art. 50, co. 8, del D.Lgs. 123/2025**.

**Ratio**: con tassi legali sotto l'unità il coefficiente di attualizzazione produceva una base imponibile «spropositata rispetto alla vita media», con un effetto che la Corte definisce «*addirittura deteriore di quello "confiscatorio"*» — l'imposta poteva **superare il valore del legato**. Il floor del 2,5% introdotto dal 139/2024 è assunto come punto di riferimento già presente nell'ordinamento e **proiettato all'indietro sui rapporti non esauriti**.

🎯 **Effetto operativo — che cosa cambia in pratica**
- Per le successioni **aperte dal 1/1/2025** non cambia nulla: DEAS applica già il floor 2,5% (DM MEF 24/12/2025 + art. 17 co. 1-ter TUS).
- Per le successioni **aperte ANTE 1/1/2025 con pratica non definita** (in contenzioso o in attesa di avviso di liquidazione), il valore della rendita vitalizia da legato **va ricalcolato con il floor 2,5%**. **DEAS non le ricalcola da sé**: l'intervento è manuale.
- ⛔ **NON applicare più la disciplina transitoria dell'art. 9, co. 4, D.Lgs. 139/2024** (coefficienti del DM MEF 21/12/2015 per le rendite costituite ante riforma con tasso legale ≤ 0,1%): **è caduta** (capo 3). Confermato sul testo: l'art. 9 su normattiva porta ora la nota **AGGIORNAMENTO (4)** che recepisce la sentenza (letta il 19/8/2026).

⚠️ **Anomalia da conoscere prima, non da scoprire allo scarto** (verificata il 19/8/2026): **manca ancora la prassi AdE** che recepisca la sentenza. L'ultimo atto di prassi in materia è la **Circolare 3/E del 16/4/2025**, **anteriore** al deposito. Chi liquida oggi una rendita vitalizia applica un floor imposto dalla Consulta ma **non ancora tradotto in istruzioni operative**: motivarlo in dichiarazione o in memoria, citando la sentenza.

⚠️ **Riserva tecnica**: l'art. 17 TUS — l'articolo colpito in via principale — è stato letto **sul dispositivo della sentenza**, non sul testo consolidato di normattiva. Rileggerlo live prima di trascriverlo in un atto.

---

## D.Lgs. 5 agosto 2026, n. 141 — dal 1/1/2027 cambiano i documenti da allegare

**Estremi** (scheda ELI letta il 12/8/2026): *Approvazione del testo unico delle disposizioni legislative in materia di adempimenti e accertamento…*, **G.U. S.G. n. 181 del 6/8/2026, Suppl. Ordinario n. 28** (⚠️ non «28/L»), cod. red. **26G00160**, **in vigore 7/8/2026**.

📌 **Oggi non cambia nulla di ciò che si deposita.** È un drift **differito**, ma con una data certa e un impatto diretto sulla checklist documenti.

**Dal 1° gennaio 2027**, per effetto dell'art. 4 del 141/2026 sul TU registro (D.Lgs. 123/2025), letto integralmente su primaria il 18/8/2026:
- **lett. u)** — art. 115, co. 1: alla dichiarazione non si allegano più «*il certificato di morte*» e «*il certificato di stato di famiglia*», ma **la dichiarazione sostitutiva di certificazione di morte** e **la dichiarazione sostitutiva di stato di famiglia**; il **co. 3 è abrogato**;
- **lett. t)** — art. 114, co. 1: **lettera e) soppressa** → l'elenco dei documenti perde una voce;
- **lett. s), z), bb)** — artt. 112, 120, 133: i rinvii agli **artt. 34 e 35 del TUS 346/1990** diventano rinvii agli **artt. 309 e 310** del nuovo TU adempimenti e accertamento;
- **lett. aa)** — art. 127, co. 1: «*le aliquote*» → «*l'aliquota e la franchigia*».

⚠️ **Convergenza da citare con la causa giusta**: le lett. m) n. 2 e q) n. 2 abrogano l'art. 50 co. 8 e sopprimono l'art. 102 co. 4 del D.Lgs. 123/2025 — **le stesse disposizioni** già travolte dai capi 4 e 5 di C.Cost. 89/2026. Doppia caducazione convergente con tecniche diverse: **incostituzionalità** (*erga omnes*, dal 4/6/2026, sui rapporti non esauriti) e **abrogazione espressa** (dal 7/8/2026). Stesso risultato, ma la causa va citata a seconda della **data-evento**.

⚠️ **Riserve dichiarate**: (a) l'articolo di **efficacia differita** dell'intero TU allegato non è stato letto — il pattern «entrata in vigore immediata / efficacia 1/1/2027» è confermato per il gemello D.Lgs. 123/2025, non per il 141/2026; (b) al 19/8/2026 **normattiva non ha ancora recepito** il 141/2026 nelle schede di D.Lgs. 123/2025 e 139/2024, ferme all'«ultimo aggiornamento all'atto pubblicato il **3/6/2026**» — data che coincide con la pubblicazione in G.U. della sent. 89/2026. Quelle schede **recepiscono la sentenza ma non il correttivo di agosto**.

📌 **Promemoria di calendario**: il **TU imposte indirette (D.Lgs. 123/2025)** entra in efficacia il **1/1/2027** (rinvio dell'art. 4 co. 5 D.L. 31/12/2025 n. 200, letto sul testo coordinato post-conversione: la L. 26/2026 non l'ha toccato) e il suo art. 204 abroga il **cuore del TUS 346/1990**. **Fino al 31/12/2026 si applica il TUS.** La migrazione dei riferimenti di questa skill è **lavoro pianificato entro dicembre 2026**, non un'emergenza.

---

## Punti di verifica rapida per lo swarm (red flags)
1. Decesso dal 2025 ma quadro EF Sez. V-bis non compilato → 🔴
2. Decesso dal 2025 ma imposta di successione data come "liquidata dall'ufficio" / coacervo applicato in successione → 🔴
3. Tassa servizi ipo-catastali calcolata a €90/€35 per decesso dal 2025 → 🔴 (deve essere €120/€65)
4. Tributi speciali attestazione ≠ €16,00 per modello 2025 → 🟡
5. Terreno edificabile valorizzato con valore catastale automatico → 🔴 (serve valore venale)
6. Fabbricato cat. F o privo di rendita inserito senza classamento → 🔴
7. Erede minore/incapace senza accettazione con beneficio d'inventario → 🔴
8. Coefficiente usufrutto non basato sul 2,5% per decessi 2024-2026 → 🟡
9. Trust che ricade nei casi di esclusione dal telematico, ma trattato come telematico → 🔴
10. Somma quote di devoluzione di un cespite ≠ 1/1 (o ≠ diritto del de cuius) → 🔴
11. Tipo dichiarazione indicato come "integrativa/modificativa" del nuovo modello: nel telematico esistono solo "Prima dichiarazione" e "Sostitutiva" (sottotipi 1/2/3; il 3 = integrativa per soli allegati, con soli frontespizio + EG) → 🔴
12. Quadro ES previsto come quadro da trasmettere (è soppresso nel tracciato 2025) → 🔴
13. Codici parentela/diritto/natura non riscontrati nelle liste SUC13 (`references/specifiche-suc13/`) → 🔴
14. **Rendita/pensione vitalizia in una successione aperta ANTE 1/1/2025 e non ancora definita, valorizzata con il saggio legale nudo dell'anno anziché con il floor 2,5%** → 🔴 (C.Cost. 89/2026: ricalcolo dovuto, DEAS non lo fa da sé)
15. Disciplina transitoria dell'**art. 9, co. 4, D.Lgs. 139/2024** applicata a una rendita costituita ante riforma → 🔴 (norma caduta: C.Cost. 89/2026, capo 3)
16. Documenti da allegare indicati come «certificato di morte / certificato di stato di famiglia» per una dichiarazione da presentare **dal 1/1/2027** → 🟡 (dal 2027 servono le **dichiarazioni sostitutive**: D.Lgs. 141/2026, art. 4 lett. u)
17. File `.suc` controllato con un modulo anteriore alla **2.3.1 dell'11/3/2026** → 🔴 (scarto certo dal 26/3/2026)

---

## DE.A.S. versione 2026 (pubblicata il 2 gennaio 2026) — novità operative

- **Sezione «Dichiarante/Intermediario»** (barra di navigazione e menu `Visualizza`): raccoglie in un unico punto dichiarante, intermediario, impegno alla presentazione ed **estremi del versamento (IBAN e intestatario del conto)**. Sono gli stessi dati richiesti in stampa/esportazione XML: compilarli subito evita blocchi in fase di invio.
- **`Calcoli | Visualizza Quadro EF`**: ispeziona la liquidazione delle imposte senza esportare o stampare. Da usare come check intermedio contro i calcoli della Scheda.
- **F24 per l'imposta di successione, uno per ciascun erede/legatario**, con imposta e interessi ripartiti in proporzione alla quota. ⚠️ Resta la **solidarietà** dei coeredi per l'intero (art. 36, c. 1, TUS): la ripartizione è operativa, non libera dall'obbligazione solidale.
- **Prospetto di rateizzazione con una pagina per soggetto** quando gli eredi/legatari sono più d'uno.
- **Imposta già versata in precedenti dichiarazioni**: indicabile in `Calcoli | Liquidazione imposte`, così il ravvedimento è calcolato solo sul residuo.
- **`File | Importa pratica da file .PDF`**: crea la pratica dai dati della copia semplice della dichiarazione (**quarta ricevuta**) presente nel cassetto fiscale.
- **`File | Importa pratica da file .SUC`**: crea la pratica da un file telematico conforme alle specifiche, **anche generato da altro software** — è la funzione usata dal file prodotto da `${CLAUDE_PLUGIN_ROOT}/scripts/genera_xml_suc.py`. Un file `.xml` si importa rinominandolo `.suc`. I `.DIZ` non sono importabili direttamente (vanno prima convertiti in `.SUC` col software ministeriale).
- **`Esporta pratica su file .DIZ`**: compatibile con l'applicazione SUC13 (SuccessioniOnLine) dell'AdE, per la presentazione allo sportello.
- **`Strumenti | Calcola quota di legittima e quota disponibile`** in base a coniuge, figli e/o ascendenti (art. 554 c.c.).
- Tabella dei tassi legali aggiornata; revisione tabelle uffici territoriali AdE; modello «Dichiarazione prima casa dal 1-1-2025» aggiornato; nuovo schema di procura fra i documenti integrativi; nuova colonna `Protocollo Telematico` nell'elenco dichiarazioni (richiede «Ricrea elenco (scansione cartella dati)» al primo accesso).

---

## Generatore del file telematico — allineamento alle pratiche reali (8 settembre 2026)

- **Fonte nuova**: allegato AdE «Modalità di calcolo dell'imposta di successione (autoliquidazione)» (15/7/2025), recepito in `specifiche-suc13/allegato-calcolo-imposta-successione.md` e implementato in `${CLAUDE_PLUGIN_ROOT}/scripts/suc_calcoli.py`. Esempio ufficiale (due fratelli, 400.000 di immobili, 5.000 di denaro, 1.000 di passività, agevolazione L ed imposta estera) riprodotto al centesimo: 8.865,46.
- **Elenco modifiche del 15/7/2025** alle specifiche (agevolazioni N/D/R/F/Q per grado, riduzioni art. 25 ↔ valore precedenti successioni, EF18-bis azzerato se ≤ 10 €, tempistica assente con imposta zero, tipo soggetto e disabilità coerenti su più righi, grado 35 per trust senza beneficiario, denominazione solo per non persone fisiche): tutte presenti nel pacchetto del 2/7/2025 già in skill; il generatore le applica come controlli 🔴.
- **Convenzioni DEAS** verificate su tre `.suc` trasmessi dallo studio (2024 e 2026) e documentate in `anatomia-suc-deas.md`: valori arrotondati **per eccesso**, fondi con quota esente su due righi EO, EH con `CodiceCarica` (obbligatorio nel v14), tariffe 2025 anche per decessi 2024 presentati oggi (il tracciato v14 non ammette più EF17/`Pagine_Numero`).
- **Verifica fonti dell'8/9/2026**: pagina AdE «software di controllo» → ultima versione **2.3.1 dell'11/3/2026** (storico completo riletto, nessuna successiva); archivio avvisi Servizi Telematici → unico avviso 2026 sulle successioni è quello dell'11/3/2026; Geo Network «Novità 2026» e changelog di un software concorrente (Eredito, luglio 2026) → nessuna nuova specifica né nuovo modulo dopo la 2.3.1. **SUC13 v14 (2/7/2025) resta l'ultima specifica.**

## Corpus locale della corsia successioni (18 settembre 2026, v0.24)

- **Strato 3 — testi vigenti locali** (`wiki-studio/normativa/testi/`, export Akoma Ntoso di normattiva, consolidamento
  agosto 2026, snapshot 18/9/2026): D.Lgs. 346/1990 (TUS, 66 articoli: artt. 6, 7 con aliquote e franchigie vigenti, 9,
  12, 31, 33, 34, 37, 48), D.Lgs. 347/1990 (artt. 1, 2, 10 e Tabella), D.P.R. 131/1986 (art. 52), D.L. 262/2006 (art. 2),
  D.Lgs. 139/2024, L. 104/1992 (art. 3), D.P.R. 445/2000 (artt. 46-47). `fonti_fetch.py --riferimento "art. 7 D.Lgs.
  346/1990"` risponde dal disco con data di vigenza per articolo; vita utile 45 giorni, poi si torna a normattiva
  (`codice_locale.py --costruisci tus --nel-repo` rinnova). Il round su queste norme non richiede rete.
- **Strato 4 — uffici competenti** (`uffici-competenza-successioni.json`, letto il 18/9/2026 dalle pagine AdE): provincia
  di Torino, 311 comuni e 10 circoscrizioni → UT «Atti pubblici, successioni e rimborsi IVA» **TT2** (DP I, corso Bolzano
  30, circoscrizioni 1-2-3-8-9-10 e comuni di Moncalieri/Pinerolo) o **TT3** (DP II, via Paolo Veronese 199/A,
  circoscrizioni 4-5-6-7 e comuni di Chivasso/Ciriè/Cuorgnè/Ivrea/Rivoli/Susa). Fuori provincia: sito AdE dal browser.
- Il gate di freschezza (hook) legge la data qui sotto: oltre 30 giorni esige `freshness.py --materie successioni`
  prima di scrivere il `.suc`.

**Data ultimo aggiornamento del changelog**: **18 settembre 2026** (sezione precedente: 8 settembre 2026) (sezione precedente: 21 agosto 2026) — recepimento delle proposte tell-only dei drift-report della Sentinella dal 14/7 al 20/8/2026 (`wiki-studio/normativa/drift-reports/`).

Quadro vigente alla data: modello **Provv. AdE 13/2/2025** con istruzioni al 15/7/2025; specifiche tecniche **SUC13 v14 del 2/7/2025** con XSD ufficiali integrati in `references/specifiche-suc13/`; modulo di controllo **2.3.1 dell'11/3/2026** (obbligatorio dal 26/3/2026); **DE.A.S. 2026** del 2/1/2026, ultima release **2.25i dell'8/6/2026**; **Voltura Web** esclusiva dal 12/1/2026; riforma **D.Lgs. 139/2024**; **DM MEF 24/12/2025** coefficienti 2026 e **DM MEF 10/12/2025** tasso legale 1,60%; **C.Cost. 89/2026** (floor 2,5% retroattivo sui rapporti non esauriti); **D.Lgs. 141/2026** (documenti da allegare dal 1/1/2027); **D.Lgs. 123/2025** con efficacia 1/1/2027 e abrogazione del TUS.

Fonti: specifiche SUC13 e guida DEAS (audit del 21/7/2026); pagine AdE (verifiche del 3/8, 15/8, 18/8/2026); `cortecostituzionale.it` (sent. 89/2026, letta il 15/8/2026); `gazzettaufficiale.it` (D.Lgs. 141/2026, art. 4 letto il 18/8/2026; D.L. 200/2025 e testo coordinato, letti l'8/8/2026); `normattiva.it` (art. 9 D.Lgs. 139/2024, letto il 19/8/2026).

⚠️ **Riserve aperte alla data**: (1) manca la **prassi AdE** che recepisca la sent. 89/2026; (2) le pagine AdE «modello e istruzioni» e «specifiche tecniche» non erano leggibili il 19/8/2026 → la permanenza della v14 è indizio forte, non conferma; (3) l'articolo di **efficacia differita** del D.Lgs. 141/2026 non è stato letto.
