---
alias: "istruzioni-tegm-2016"
nome: "Istruzioni per la rilevazione dei tassi effettivi globali medi ai sensi della legge sull'usura — luglio 2016 (in vigore dalle segnalazioni del 1° ottobre 2016)"
famiglia: "istruzioni-tegm-2016"
genere: "istruzioni"
struttura: "sezioni"
fonte: "www.bancaditalia.it"
url: "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/contrasto-usura/cusu-istr-tassi/Istruzioni_rilevazione_TEGM_luglio_2016.pdf"
scaricato_il: "2026-09-19T22:36:20"
sha256_fonte: "7efba35320a03266e0c53740572694513cdf7b3ebf51775b3909e4b6db5869df"
fedelta: "verificata"
citazione: "Istruzioni TEGM 2016"
sinonimi: ["istruzioni banca d'italia tegm 2016", "istruzioni tegm 2016", "istruzioni usura 2016", "istruzioni per la rilevazione dei tassi effettivi globali medi"]
vigente_al: "2026-09-19"
formato: "pdf"
origine: "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/contrasto-usura/cusu-istr-tassi/Istruzioni_rilevazione_TEGM_luglio_2016.pdf"
---
ISTRUZIONI PER LA RILEVAZIONE
DEI TASSI EFFETTIVI GLOBALI MEDI
AI SENSI DELLA LEGGE SULL’USURA



             - luglio 2016 -
                                                                             INDICE


SEZIONE I .................................................................................................................................................. 3
ISTRUZIONI PER LA SEGNALAZIONE..................................................................................................... 3
        A)         GENERALITÀ DELLA RILEVAZIONE ...................................................................................... 3
             A1. Oggetto...................................................................................................................................................... 3
             A2. Soggetti tenuti alla rilevazione .................................................................................................................... 3
             A3. Periodicità di segnalazione e termini di inoltro ............................................................................................ 3
             A4. Modalità di inoltro ..................................................................................................................................... 4
        B)         CLASSIFICAZIONE DELLE OPERAZIONI PER CATEGORIE.................................................. 4
             B1. Operazioni incluse...................................................................................................................................... 4
             B2. Operazioni escluse ..................................................................................................................................... 7
             B3. Controparte rilevante .................................................................................................................................. 9
             B4. Classi di importo ...................................................................................................................................... 10
        C) OGGETTO DELLA RILEVAZIONE E CALCOLO DEI TASSI .........................................................11
             C1. Dati da segnalare ...................................................................................................................................... 11
             C2. Base di calcolo dei dati da segnalare ......................................................................................................... 12
             C3. Calcolo del TEG ...................................................................................................................................... 13
             C4. Trattamento degli oneri e delle spese nel calcolo del TEG.......................................................................... 15
             C5. Calcolo dell’importo erogato. ................................................................................................................... 17
             C6. Calcolo del compenso di mediazione (MED) ............................................................................................. 18
        D) NORME TRANSITORIE .................................................................................................................18
             D1. Periodo transitorio (1° ottobre 2016 – 31 marzo 2017)............................................................................... 18
             D2. Primo invio dei dati in base alle presenti Istruzioni .................................................................................... 19


SEZIONE II ................................................................................................................................................24
MODALITÀ TECNICO-OPERATIVE PER L’INOLTRO DELLE INFORMAZIONI ................................24
        Premessa .............................................................................................................................................24
        Modalità di segnalazione dei dati.........................................................................................................24
        Sistema delle codifiche.........................................................................................................................24
             a) classi di importo (codice campo 599 - lunghezza 2) ..................................................................................... 24
             b) tipo importo (codice campo 350 - lunghezza 3)............................................................................................ 25
             c) durata (prevista nella parte fissa del “record movimento” - lunghezza 2)....................................................... 25
             d) residenza e valuta (previste nella parte fissa del “record movimento” - lunghezza 1) ..................................... 25
        Schemi di segnalazione ........................................................................................................................25
                                                    Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016



                                                  SEZIONE I
                 ISTRUZIONI PER LA SEGNALAZIONE
A)         GENERALITÀ DELLA RILEVAZIONE
A1. Oggetto
      La rilevazione ha per oggetto i tassi effettivi globali medi praticati dal sistema bancario e
finanziario in relazione alle categorie omogenee di operazioni creditizie, ripartite nelle classi di
importo e dettagliate nella scheda in allegato 1.

A2. Soggetti tenuti alla rilevazione
       La segnalazione deve essere effettuata dalle banche iscritte nell’albo previsto dall’art. 13 del
d. lgs. 385 del 1993 (testo unico delle leggi in materia bancaria e creditizia - TUB), dagli
intermediari finanziari iscritti nell’albo ex art. 106 TUB (1) e dai soggetti iscritti nell’elenco di cui
all’art. 111 comma 1 TUB (Microcredito) (2).
     Le banche e gli intermediari finanziari iscritti nel corso del trimestre di riferimento che non
abbiano iniziato l’attività sono esonerati dall'invio della segnalazione.

A3. Periodicità di segnalazione e termini di inoltro
         La segnalazione ha cadenza trimestrale e deve fare riferimento ai seguenti periodi di tempo:
a)       1° gennaio - 31 marzo;
b)       1° aprile - 30 giugno;
c)       1° luglio - 30 settembre;
d)       1° ottobre - 31 dicembre.
      I dati devono pervenire alla Banca d’Italia entro il giorno 25 del mese successivo alla fine del
trimestre di riferimento.




1
    Sono altresì tenuti alla segnalazione gli intermediari già iscritti nei cessati elenchi di cui alla previgente formulazione
    degli artt. 106 e 107 TUB i quali abbiano in corso un procedimento amministrativo per l’iscrizione nel nuovo albo e
    siano pertanto abilitati ad operare in conformità del previgente regime normativo, fino alla conclusione del
    procedimento amministrativo (cfr. art. 10, comma 4, lett. d, ultimo periodo del d.lgs 141/2010).
    Fanno eccezione le società costituite ai sensi dell’art. 7-bis della Legge 130/99 (Covered Bond) e le società fiduciarie
    iscritte nella sezione dell’albo ex art. 106 TUB, di cui all’art. 199, comma 2 del d.lgs. 58/1998, che non sono tenute
    alla segnalazione.
    I Confidi e le società di servicing in operazioni di cartolarizzazione iscritti all’albo di cui all’art. 106 del TUB sono
    tenuti alla segnalazione trimestrale. Nel caso in cui essi non effettuino attività di erogazione diretta di finanziamenti,
    dovranno darne comunicazione trimestrale mediante l’utilizzo della specifica voce “segnalazione negativa”. In ogni
    caso, non è dovuta la segnalazione anti-usura da parte dei Confidi iscritti all’elenco di cui all’art. 155, comma 4 del
    TUB e, da quando sarà istituito l’elenco ex art. 112 TUB, non sarà dovuta la segnalazione da parte dei Confidi minori
    iscritti a detto elenco.
2
    Sono esclusi gli operatori di finanza mutualistica e solidale di cui all’art. 16 del D.M.176/2014 e i soggetti giuridici
    senza fini di lucro di cui all’art. 111 comma 4 del TUB.


                                                                 -3-
                                                    Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

A4. Modalità di inoltro
     I dati devono essere inviati alla Banca d’Italia - Servizio Rilevazioni Statistiche - secondo le
modalità e gli schemi di cui alla Sezione II delle presenti istruzioni.


B)        CLASSIFICAZIONE DELLE OPERAZIONI PER CATEGORIE
B1. Operazioni incluse
      Le operazioni di finanziamento oggetto della rilevazione vanno classificate all’interno delle
categorie secondo le modalità di seguito indicate (3):

Cat. 1. Aperture di credito in conto corrente
      Rientrano in tale categoria di rilevazione le operazioni regolate in conto corrente in base alle
quali l’intermediario, ai sensi dell’art. 1842 e ss. del c.c., si obbliga a tenere a disposizione del
cliente una somma di denaro per un dato periodo di tempo ovvero a tempo indeterminato e il cliente
ha facoltà di ripristinare le disponibilità.
      Vanno inseriti in tale categoria anche i passaggi a debito di conti non affidati nonché gli
sconfinamenti sui conti correnti affidati rispetto al fido accordato.
       È richiesta separata evidenza delle operazioni con garanzia e senza garanzia (Cat.1a e 1b). Per
operazioni “con garanzia” si intendono quelle assistite da garanzie reali ovvero da garanzie prestate
da banche, imprese di investimento, società e enti di assicurazione, confidi e intermediari finanziari
iscritti all’albo unico (4). Vanno segnalate tra le operazioni con garanzia anche quelle parzialmente
garantite.
        È richiesta altresì separata evidenza dei passaggi a debito di conti senza affidamento (Cat. 1c).
       Qualora su uno stesso conto corrente non affidato si registrino saldi a debito nel trimestre di
riferimento e successiva concessione di fido nel medesimo trimestre devono essere considerate due
distinte operazioni, ciascuna nella rispettiva sotto-categoria. Parimenti, il mancato rientro di
un’apertura di credito scaduta o revocata dovrà essere segnalato, dalla data di scadenza o di revoca,
tra i passaggi a debito dei conti non affidati.

Cat. 2. Finanziamenti per anticipi su crediti e documenti e sconto di portafoglio commerciale;
     finanziamenti all’importazione e anticipo fornitori
      Rientrano in questa categoria di rilevazione i finanziamenti a valere su effetti, altri titoli di
credito e documenti s.b.f., le operazioni di finanziamento poste in essere sulla base di un contratto di
cessione del credito ex art. 1260 c.c. diverse dal factoring e le operazioni di sconto di portafoglio
commerciale (5) (Cat. 2a).



3
     I criteri di classificazione riguardano la fase di acquisizione dei dati; la pubblicazione dei tassi avviene, di norma, in
     forma più aggregata.
4
     Tale previsione si applica anche alle garanzie prestate dagli intermediari finanziari iscritti nel cessato elenco speciale
     di cui alla previgente formulazione dell’art. 107 TUB, i quali abbiano in corso un procedimento amministrativo per
     l’iscrizione nel nuovo albo e siano pertanto abilitati ad operare in conformità del previgente regime normativo, fino
     alla conclusione del procedimento amministrativo (cfr. art. 10, comma 4, lett. d, ultimo periodo del d.lgs 141/2010).
5
     Le operazioni di forfaiting in euro in base alle quali l’intermediario segnalante concede all’esportatore italiano un
     finanziamento basato sullo sconto pro-soluto di documenti prodotti dall’importatore estero (effetti cambiari, lettere
     di credito o altre garanzie bancarie) vanno segnalate nella categoria relativa alla forma tecnica adottata.


                                                                 -4-
                                           Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

      Deve essere fornita separata evidenza dei finanziamenti a valere su effetti e fatture di cui il
soggetto finanziato non è creditore (per esempio anticipi fornitori, anticipi a valere su documenti
rappresentativi di merci e finanziamenti all’importazione) (Cat. 2b).
      Tali operazioni rientrano in questa categoria anche quando sono contabilmente gestite sul
conto corrente ordinario.

Cat. 3. Credito personale
       Rientrano in questa categoria di rilevazione i prestiti nei confronti delle famiglie consumatrici
(cfr. punto B3) che:
-     siano destinati a finanziare generiche esigenze di spesa o di consumo personali o familiari;
-     siano erogati in un’unica soluzione e prevedano il rimborso in base a un piano di
      ammortamento.
     Il cliente, una volta ottenuti i fondi, potrà disporne per la finalità comunicata al finanziatore,
oppure per altre finalità.
      Se il credito personale viene erogato sotto forma di apertura di credito in conto corrente il
finanziamento rientra nella categoria delle aperture di credito in conto corrente (Cat. 1).

Cat. 4. Credito finalizzato
      Rientrano in questa categoria di rilevazione i finanziamenti rateali destinati all’acquisto di uno
o più specifici beni o al pagamento di specifici servizi, fino a un importo di 75.000 euro.
       I crediti inseriti in questa categoria sono caratterizzati da una stretta connessione tra l'acquisto
di un bene o di un servizio e la concessione del credito la cui erogazione avviene, da parte
dell'intermediario, con il pagamento del corrispettivo all'esercente.

Cat. 5. Factoring
      Rientrano in questa categoria di rilevazione gli anticipi erogati a fronte di un trasferimento di
crediti commerciali effettuati con la clausola “pro solvendo” o “pro soluto”, dal soggetto titolare
(impresa fattorizzata) a un intermediario specializzato (factor).
      Si ricomprendono in tale categoria tutti gli anticipi erogati a fronte di operazioni riconducibili
a un rapporto di factoring, anche se non effettuate ai sensi della legge n. 52 del 1991.

Cat. 6. Leasing
      Rientrano in questa categoria di rilevazione i finanziamenti realizzati con contratti di
locazione di beni materiali (mobili e immobili) o immateriali (ad es. software), acquisiti o fatti
costruire dal locatore su scelta e indicazione del conduttore che ne assume tutti i rischi e con facoltà
di quest’ultimo di divenire proprietario dei beni locati al termine della locazione, dietro versamento
di un prezzo prestabilito. Non rientrano nella rilevazione le operazioni di leasing operativo
caratterizzate dall’assenza dell’opzione finale di acquisto.
      È richiesta separata evidenza per il leasing immobiliare a tasso fisso e variabile, il leasing
aero-navale e su autoveicoli e il leasing strumentale.




                                                        -5-
                                                  Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

Cat. 7. Mutui
        Rientrano in questa categoria di rilevazione i contratti di finanziamento che:
a)      abbiano durata superiore a cinque anni;
b)      siano assistiti da garanzia ipotecaria (6);
c)      prevedano il rimborso tramite il pagamento di rate comprensive di capitale e interessi.
       È richiesta separata evidenza per i mutui a tasso fisso e quelli a tasso variabile; all’interno di
tale ripartizione deve essere poi fornita evidenza separata dei finanziamenti concessi alle “famiglie
consumatrici” e alle “unità produttive private” (cfr. successivo punto B3).
        Per tasso variabile si intende il tasso ancorato all’andamento di un parametro predefinito.
      I mutui che prevedono contrattualmente un periodo in cui la rata corrisposta dal cliente è
calcolata in base a un tasso fisso e un periodo nel quale la rata è determinata utilizzando un tasso
variabile (cd. mutui a tasso misto) sono segnalati tra i mutui a tasso variabile. Tuttavia, ove il
contratto preveda che le rate siano calcolate in base a un tasso fisso per un periodo pari o superiore a
tre anni e in base a un tasso variabile per il restante periodo, la segnalazione va effettuata imputando
l’operazione nella categoria a tasso fisso.
      I mutui che prevedono contrattualmente che ciascuna rata corrisposta dal cliente sia calcolata
in base a un tasso fisso per una certa percentuale di importo e in base ad un tasso variabile per la
restante percentuale (c.d. mutui bilanciati) sono segnalati tra i mutui a tasso variabile se la
percentuale di importo su cui si calcola il tasso variabile è uguale o superiore al 30%, negli altri casi
sono segnalati tra i mutui a tasso fisso.
      I mutui che prevedono l’esercizio di un’opzione sul tasso applicato sono segnalati nella
categoria relativa alla tipologia di tasso previsto per la prima rata di rimborso.

Cat. 8. Prestiti contro cessione del quinto dello stipendio e della pensione
      Rientrano in questa categoria i prestiti contro cessione del quinto dello stipendio e della
pensione concessi sulla base del D.P.R. n. 180 del 1950 (7). La segnalazione è effettuata dal titolare
del rapporto di finanziamento anche se il prestito è erogato per il tramite di società con esso
convenzionate e deve riflettere l’onere complessivo gravante sul debitore.
      È richiesta separata evidenza per i prestiti contro cessione del quinto dello stipendio e quelli
contro cessione del quinto della pensione.

Cat. 9. Credito revolving e finanziamenti con utilizzo di carte di credito
      Rientrano in questa categoria le operazioni di credito revolving e i finanziamenti a valere
sull’utilizzo di carte di credito.
      Si definisce operazione di credito revolving la messa a disposizione di una linea di fido,
diversa dalle aperture di credito in conto corrente, da utilizzare interamente o parzialmente, anche in
tempi diversi, per l’acquisto di beni e servizi presso venditori convenzionati o per l’acquisizione di
disponibilità monetarie. I versamenti rateali del cliente, dei quali è fissato contrattualmente




6
     L’iscrizione ipotecaria, anche se differita, è comunque volta a garantire il finanziamento che, pertanto, deve essere
     segnalato in questa categoria qualora siano rispettate anche le condizioni a) e c).
7
     Così come modificato dai provvedimenti legislativi (art. 1 comma 137 della legge 311/2004 e legge 80/2005) che
     hanno esteso la normativa ai pensionati e dipendenti privati.


                                                               -6-
                                                  Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

l’importo minimo periodico, ripristinano la disponibilità sulla linea di fido; l’operazione può essere
connessa con l’utilizzo di una carta di credito (Cat. 9a).
      Rientrano in questa categoria, con separata evidenza, i finanziamenti a valere sull’utilizzo di
carte di credito con durata predeterminata e piano di ammortamento predefinito (Cat. 9b).

Cat. 10. Altri finanziamenti
       La categoria ha carattere residuale; vi rientrano tutte le forme di finanziamento non
riconducibili ad una delle categorie precedenti (ad es. le operazioni di credito su pegno, il
portafoglio finanziario, i crediti concessi con delegazione di pagamento, i mutui chirografari, i
prestiti vitalizi ipotecari, i finanziamenti concessi ai debitori ceduti sotto forma di dilazione di
pagamento, i finanziamenti per leasing in construendo e quelli relativi a immobili “in attesa di
locazione” 8, i mutui che prevedono l’erogazione "a stato avanzamento lavori" 9, nonché quelli
aventi un piano di ammortamento che preveda il pagamento della quota capitale per intero alla data
di scadenza del prestito).
       Deve essere fornita evidenza separata dei finanziamenti concessi alle “famiglie consumatrici”
e alle “unità produttive private” (cfr. successivo punto B3).
                                                              ° ° °
       I prefinanziamenti, cioè i finanziamenti che si configurano come autonome operazioni di
prestito (in genere a breve scadenza) che soddisfano in via temporanea i fabbisogni del soggetto
debitore in attesa della concessione di finanziamenti a rimborso rateale in corso di istruttoria o già
deliberati, vanno segnalati nella categoria di operazioni relativa alla forma tecnica utilizzata nel
prefinanziamento senza tenere conto della categoria dell'operazione “principale” (ad es. i
prefinanziamenti sulle cessioni del quinto dello stipendio possono essere inclusi in cat. 10 o in altre
categorie a seconda della forma tecnica).
      Le operazioni in pool, cioè i finanziamenti erogati da due o più intermediari con assunzione di
rischio a proprio carico sulla base di contratti di mandato o di rapporti con effetti equivalenti, sono
segnalate dall’intermediario capofila con riferimento all’intero ammontare del finanziamento.

B2. Operazioni escluse
      Tenuto conto delle specifiche caratteristiche delle singole tipologie di finanziamento, sono
escluse dall’obbligo di segnalazione per la rilevazione a fini statistici, ma non dall’applicazione
della Legge 108/96, le seguenti operazioni (10):

1)      Operazioni in valuta.
      Per operazioni in valuta si intendono i finanziamenti denominati in valute diverse dall’euro, il
cui tasso d’interesse remunera, oltre che il rischio di credito, anche il rischio di cambio.




8
     Al momento del contratto definitivo di leasing, l’operazione andrà segnalata nella rispettiva categoria di leasing
     secondo il bene dato in locazione.
9
     Per i mutui a SAL la segnalazione è dovuta solo all’atto della stipula e non per l’erogazione delle singole tranches e
     per le successive operazioni di frazionamento con accollo, se le condizioni economiche sono già previste nel
     contratto iniziale.
10
     Ai fini della definizione delle voci 2 e 3, per quanto qui non espressamente previsto, si fa riferimento alla Circolare
     della Banca d’Italia “Matrice dei conti” (n. 272 del 30.07.2008) e al “Manuale per la compilazione delle segnalazioni
     di vigilanza per gli intermediari finanziari, per gli istituti di pagamento e per gli IMEL” (Circolare della Banca
     d’Italia n. 217 del 5.8.1996).


                                                               -7-
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

      Devono essere considerate come in valuta anche le operazioni che prevedono clausole di
indicizzazione finanziaria collegate all’andamento del tasso di cambio dell’euro con una
determinata valuta o con un paniere di valute.

2)      Posizioni classificate a sofferenza.
      Per posizioni classificate a sofferenza si intendono le esposizioni nei confronti di soggetti in
stato di insolvenza (anche non accertato giudizialmente) o in situazioni sostanzialmente
equiparabili, indipendentemente dalle eventuali previsioni di perdita formulate dall’azienda.
      Sono esclusi dalla rilevazione i rapporti classificati a sofferenza alla fine del trimestre di
riferimento.

3)      Esposizioni oggetto di concessioni deteriorate.
      Per esposizioni oggetto di concessioni deteriorate si intendono le esposizioni che soddisfano
la definizione di “Non performing exposures with forbearance measures” di cui all’Allegato V,
Parte 2, paragrafo 180 del Regolamento di esecuzione (UE) n. 680/2014 della Commissione, e
successive modificazioni e integrazioni.
      Sono esclusi dalla rilevazione le esposizioni oggetto di concessioni deteriorate alla fine del
trimestre di riferimento.

4)      Operazioni a tasso agevolato.
      Per operazioni a tasso agevolato si intendono i finanziamenti eseguiti a tasso inferiore a quello
di mercato in virtù di provvedimenti legislativi che dispongono la concessione del concorso agli
interessi e/o l’impiego di fondi di provenienza statale o regionale ovvero di altri enti della pubblica
amministrazione. Ai fini della rilevazione, sono assimilati a tali finanziamenti quelli erogati a
condizioni di favore in considerazione di calamità naturali o altri eventi di carattere straordinario e
le operazioni di acquisto crediti assistiti da garanzia dello Stato ai sensi dell’art. 37 del D.L. 24
aprile 2014 n. 66.

5)      Operazioni a tassi di favore.
       Per operazioni a tassi di favore si intendono i finanziamenti concessi a tassi pari o al di sotto
del tasso Euribor o del tasso Eurirs o di altri parametri di mercato relativi al costo della provvista
omogenei “per durata” ai finanziamenti stessi purché opportunamente documentati e motivati (11).
Sono altresì considerati a tassi di favore i contratti stipulati a condizioni inferiori a quelle di mercato
in virtù di una provvista fondi a tassi agevolati ottenuta tramite organismi senza finalità di lucro (12).
       Ai fini segnaletici le operazioni con tasso annuo nominale pari a zero non vanno escluse se
l’inclusione di eventuali oneri (polizze assicurative o altre componenti di costo) determina un TEG a
tassi di mercato.
      Nel caso di operazioni che prevedono l’applicazione di tassi di favore per un numero limitato
di rate e di tassi di mercato per le rate rimanenti, si precisa che il tasso complessivo va calcolato



11
     È possibile fare ricorso ad un tasso calcolato sulla base di interpolazioni o al tasso di mercato con durata più vicina a
     quella effettiva del finanziamento; nel caso di finanziamenti a revoca, si deve far riferimento a tassi di mercato di
     durata pari a 12 mesi.
12
     I finanziamenti a piccole e medie imprese, concessi sulla base delle convenzioni tra la Cassa Depositi e Prestiti e
     l’Associazione Bancaria Italiana non vanno in genere esclusi, in quanto trattasi di finanziamenti oggetto di autonoma
     negoziazione tra le parti interessate. Tali finanziamenti non vanno segnalati solo se le condizioni applicate alle PMI
     sono oggettivamente inferiori a quelle di mercato.


                                                                -8-
                                          Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

sull’intera linea di credito e che l’esclusione dell’operazione dalla rilevazione dipende dalla misura
del tasso complessivo. Lo stesso dicasi per i casi in cui sulla medesima linea di credito (per esempio
in un credito connesso con una carta revolving) si verifichino utilizzi a tasso promozionale e utilizzi
a tasso ordinario.

6)    Posizioni relative a utilizzi per soli saldi liquidi, che non hanno fatto registrare saldi contabili
      a debito.

7)    Posizioni affidate con utilizzo contabile nullo nel periodo di riferimento.

8)    Finanziamenti infragruppo.
      Per finanziamenti infragruppo si intendono le operazioni di credito effettuate nei confronti di
società del gruppo di appartenenza.

9)    Finanziamenti effettuati con fondi raccolti mediante emissioni di "obbligazioni di serie
      speciale con la clausola di convertibilità in azioni di società terze", regolati a condizioni
      prossime a quelle della relativa provvista.

10)   Crediti rinegoziati a condizioni fissate per legge.

11)   Finanziamenti oggetto di interventi di sospensione/allungamento concordati a livello di
      sistema.

      Per finanziamenti oggetto di interventi di sospensione si intendono quelli per cui è concessa la
sospensione del pagamento della quota capitale delle rate di mutuo e della quota capitale dei canoni
di operazioni di leasing e l’allungamento delle scadenze del credito, sulla base di accordi
caratterizzati da natura straordinaria, limitati nel tempo e concordati a livello di sistema.

12)   Crediti di firma.

13)   Microcredito destinato a promuovere progetti di inclusione sociale e finanziaria (cd.
      microcredito sociale).
      Sono esclusi dalla segnalazione i finanziamenti di Microcredito erogati a favore di persone
fisiche in condizioni di particolare vulnerabilità economica o sociale prestati a condizioni più
favorevoli rispetto a quelle prevalenti sul mercato ai sensi del comma 3 dell’art. 111 TUB.

B3. Controparte rilevante
      Formano oggetto di rilevazione le operazioni poste in essere con le “famiglie consumatrici”
residenti e le “unità produttive private” residenti, come definite dalle istruzioni relative alla
classificazione della clientela per settori e gruppi di attività economica, emanate dalla Banca d’Italia
con la circolare n. 140 dell’11.2.1991 e successivi aggiornamenti. Ove non diversamente richiesto,
la segnalazione va riferita congiuntamente alle due categorie di operatori.
      In particolare, appartengono alla categoria “famiglie consumatrici” i soggetti classificati al
Settore 006, Sottogruppo 600; fanno parte delle “unità produttive private” le imprese private
(Settore 004, Sottosettore 058), le quasi-società non finanziarie (Settore 004 - Sottosettori 048 e
049) e le “famiglie produttrici” (Settore 006, Sottosettore 061).
      Sono pertanto esclusi i rapporti di credito intrattenuti con:




                                                       -9-
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

-       le Amministrazioni pubbliche (Settore 001);
-       le Società finanziarie (13) (Settore 023);
-       le Associazioni fra imprese non finanziarie (Settore 004 - Sottosettore 045);
-       le Imprese pubbliche (Settore 004 - Sottosettore 057);
-       le Istituzioni senza scopo di lucro al servizio delle famiglie (Settore 008);
-       i non residenti (14) (Resto del mondo - Settore 007);
-       le Unità non classificabili e non classificate (Settore 099).


B4. Classi di importo
     Le categorie omogenee di operazioni creditizie sono ripartite in classi di importo. Le classi di
importo variano a seconda di ciascuna categoria e sono indicate nell'allegato 1.
      Ogni singolo finanziamento (“rapporto”) deve essere attribuito alla relativa classe di importo
sulla base dell’ammontare del fido accordato.
      Per fido accordato si intende l’ammontare del fido utilizzabile dal cliente in quanto riveniente
da un contratto perfetto ed efficace (cd. accordato operativo 15)..
     Il fido accordato da prendere in considerazione è quello al termine del periodo di riferimento
(ovvero l’ultimo nel caso dei rapporti estinti 16).
      Nel caso di finanziamenti rientranti nelle categorie 3), 4), 6), 7), 8), 9b) e 10) la classe di
importo deve essere individuata in base al capitale finanziato (per es. nei finanziamenti contro
cessione del quinto dello stipendio si deve prendere in considerazione il montante lordo meno gli
interessi).
       Nel caso di passaggi a debito di conti non affidati o comunque se si verificano utilizzi di
finanziamento senza che sia stato precedentemente determinato l’ammontare del fido accordato,
l’attribuzione alla classe di importo va effettuata prendendo in considerazione l’utilizzo effettivo nel
corso del trimestre di riferimento (ad es. nel caso di passaggi a debito di conti correnti non affidati e
degli sconfinamenti rispetto al fido accordato deve essere considerato il saldo liquido massimo di
segno negativo; nel caso di operazioni di factoring su crediti acquistati a titolo definitivo 17 e di




13
     Con riferimento agli ausiliari finanziari (brokers, cambiavalute, agenti di assicurazione, promotori finanziari, ecc..),
     vanno segnalate le operazioni effettuate verso soggetti che non rientrano tra le “Società finanziarie” (ausiliari
     finanziari senza addetti e non organizzati in forma societaria).
14
     Gli intermediari che effettuano esclusivamente operazioni in valuta con non residenti non sono esentati dagli
     obblighi segnaletici ma sono tenuti a inviare una segnalazione negativa.
15
     Ai fini della definizione di accordato operativo, per quanto qui non espressamente previsto, si fa riferimento alla
     Circolare della Banca d’Italia n. 139 dell’11/2/1991 (Centrale dei rischi).
16
     Nel caso di un ampliamento temporaneo dell’accordato operativo, che non sia stato formalizzato contrattualmente, la
     classe di importo resta determinata secondo l’ammontare originariamente determinato. Nei casi in cui la variazione
     dell’accordato, ancorché temporanea, sia stata formalizzata contrattualmente, vanno segnalate due operazioni
     distinte, riferite ai due contratti prima e dopo la variazione dell’accordato.
17
     Per "crediti acquistati a titolo definitivo" si intendono quelli acquistati dall’intermediario segnalante che non danno
     luogo a posizioni debitorie nei confronti del cedente.


                                                               - 10 -
                                                     Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

sconto di effetti deve essere considerato l’importo erogato 18; nel caso di operazioni di factoring che
danno luogo a posizioni debitorie del cedente va considerata l’esposizione massima). In caso di
presentazione di effetti allo sconto da parte di un cliente occasionale la classe d’importo è
determinata in base all’importo erogato per ogni singola presentazione sul complesso degli effetti
ceduti nell’arco di una giornata lavorativa, ancorché gli stessi siano emessi da soggetti diversi e per
differenti scadenze.
      Con riferimento alle operazioni di leasing la classe di importo va individuata facendo
riferimento all’importo del finanziamento al lordo del cd. "maxicanone" e/o di eventuali anticipi e al
netto delle imposte.
      Nelle operazioni di credito revolving e nei finanziamenti a valere sull’utilizzo di carte di
credito, qualora un singolo rapporto preveda il rilascio di più carte di credito (ad esempio “carte
aziendali”), la classe d’importo va individuata facendo riferimento all’ammontare complessivo del
fido accordato.
      I mutui che prevedono l’erogazione "a stato avanzamento lavori" e le operazioni di leasing in
construendo vanno segnalati nella classe d’importo corrispondente al totale del finanziamento
accordato.
      In caso di “fidi promiscui”, che prevedono cioè per il cliente la possibilità di utilizzare
secondo diverse modalità un’unica linea di fido, la classe d’importo cui ricondurre ciascuna
modalità di utilizzo è data dal totale del fido accordato. Nel caso siano previste alcune limitazioni
per singola modalità di utilizzo, la classe di importo va individuata con riferimento a tale limite se le
modalità di utilizzo sono riferite a categorie diverse, in caso contrario si dovrà considerare
l’accordato totale per categoria.


C) OGGETTO DELLA RILEVAZIONE E CALCOLO DEI TASSI
C1. Dati da segnalare
        Per ciascuna categoria di operazioni devono essere segnalate le seguenti informazioni:
1)      tasso effettivo globale, espresso su base annua, praticato in media dall’intermediario. Il dato è
        calcolato come media aritmetica semplice dei tassi effettivi globali applicati ad ogni singolo
        rapporto (TEG);
2)      numero di rapporti che hanno concorso alla determinazione del tasso effettivo globale
        praticato in media dall’intermediario;
3)      importo erogato medio nei rapporti che hanno concorso alla determinazione del tasso effettivo
        globale, calcolato come media aritmetica semplice degli importi erogati in ogni singolo
        rapporto;
4)      compenso medio percentuale per l’attività di mediazione. Il dato è calcolato come media
        aritmetica semplice dei compensi di mediazione in percentuale dell’accordato applicati ad
        ogni singolo rapporto (MED);
5)      numero di rapporti che hanno concorso alla determinazione del compenso medio di cui al
        punto 4);




18
     Per importo erogato si intende il valore attuale degli effetti presentati allo sconto.


                                                                 - 11 -
                                                  Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

      Le informazioni di cui ai punti 1), 2) e 3) devono essere disaggregate per le classi d’importo
previste.
      Qualora non siano state effettuate, nel trimestre di riferimento, operazioni da segnalare, deve
essere prodotta una segnalazione negativa secondo le modalità definite nella Sezione II.

C2. Base di calcolo dei dati da segnalare

Sono assoggettati alla rilevazione:

a)      per le operazioni rientranti nelle Cat. 1, Cat. 2, Cat. 5 e Cat. 9a, tutti i rapporti di
        finanziamento intrattenuti nel trimestre di riferimento (ancorché estinti nel corso del
        trimestre)(19). Nei rapporti di factoring che non diano luogo a posizioni debitorie per il
        cedente e nel caso di operazioni rientranti nella Cat. 2, ad eccezione degli anticipi s.b.f., sono
        da segnalare i rapporti per i quali si è verificata almeno una presentazione nel periodo di
        riferimento. Solo nei casi in cui manchi un preesistente affidamento, per calcolare il numero di
        rapporti si considerano le singole presentazioni di effetti o cessioni di crediti.
b)      per le altre categorie di operazioni, esclusivamente i nuovi rapporti di finanziamento accesi
        nel periodo di riferimento (20). Devono inoltre essere segnalati, nelle rispettive categorie di
        finanziamento, tutti i rapporti per i quali, nel trimestre, risulta variata una condizione
        contrattuale relativa a durata, importo erogato, tasso d’interesse e spese, i cui termini non
        siano già previsti nel contratto originario (ad es. vanno incluse nella rilevazione le dilazioni di
        pagamento non previste contrattualmente e i prestiti personali con possibilità di ricarica al
        momento dell’esercizio dell’opzione), fatte salve le operazioni escluse riportate nel par. B2
        (21). Nelle nuove operazioni da segnalare, per stabilire la classe d’importo e il TEG, dovrà
        essere preso in considerazione il piano di ammortamento modificato per effetto delle
        variazioni contrattuali, riferito alla sola durata residua del finanziamento (22).




19
     Le operazioni incluse nelle categorie richiamate sono soggette a verifica trimestrale sul rispetto delle soglie vigenti
     in ciascun periodo.
20
     I finanziamenti si intendono accesi all’atto della stipula del contratto, pertanto l’erogazione differita del mutuo non
     ha rilievo ai fini della segnalazione.
21
     I crediti ceduti a società veicolo che non superano le regole IAS per la derecognition e sono mantenuti sui libri
     dell’intermediario cedente, se sono oggetto di rinegoziazioni vanno considerati, ai fini segnaletici, in capo
     all’intermediario sulla base dei criteri utilizzati per la redazione del bilancio.
     Le variazioni contrattuali dei tassi cap o floor intervenute senza alcun impatto sul tasso effettivamente praticato al
     cliente non richiedono una nuova segnalazione.
     La modifica del piano di ammortamento, quando costituisce una facoltà già prevista contrattualmente, non determina
     l’obbligo di produrre una nuova segnalazione.
     Il recesso da una polizza assicurativa abbinata ad un contratto di finanziamento, laddove non dia luogo ad una
     variazione di elementi essenziali del contratto (modifica del TAN o della durata), non determina l’obbligo di
     produrre una nuova segnalazione.
     In caso di estinzione anticipata parziale del finanziamento non occorre effettuare una nuova segnalazione, sempre
     che per la quota non estinta del finanziamento non cambino le condizioni contrattuali.
22
     Nel caso di rinegoziazione, la tipologia di operazione da segnalare resta quella definita dal contratto originario a
     meno che non cambi la forma tecnica; ad esempio un mutuo ipotecario rinegoziato dovrà essere segnalato nella
     Categoria 7, anche nel caso di durata residua del finanziamento inferiore a 5 anni.


                                                               - 12 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

C3. Calcolo del TEG
      La metodologia di calcolo del TEG varia a seconda delle diverse categorie di operazioni
individuate. In particolare devono essere adottate le metodologie di seguito indicate:

     a) Cat. 1, Cat. 2, Cat. 5, Cat. 9a e operazioni rientranti nella altre categorie ma che presentano
     un utilizzo flessibile del fido accordato senza un piano di rientro predefinito.
        La formula per il calcolo del TEG è la seguente:
                                     Interessi  36.500 Oneri su base annua  100
                           TEG                        
                                      Numeri debitori           Accordato
        dove:
-       gli interessi sono dati dalle competenze maturate nel trimestre di riferimento,
        indipendentemente dal momento in cui diventano esigibili. Per le operazioni rientranti nelle
        Cat. 2 e 5, nelle quali gli interessi sono stati determinati con la formula dello sconto, per
        interessi si intendono il totale delle competenze calcolate;
-       i numeri debitori sono dati dal prodotto tra i “capitali” ed i “giorni” sulla base dei quali sono
        maturati gli interessi. Nel caso di operazioni rientranti nelle Cat. 2 e 5 i numeri debitori sono
        comprensivi esclusivamente dei giorni strettamente necessari per l’incasso (23); qualora la
        determinazione degli interessi sia effettuata con la formula dello sconto, i numeri debitori
        andranno ricalcolati in funzione del valore attuale degli effetti, anziché di quello “facciale”;
-       tutti gli oneri diversi dagli interessi, compresa la Commissione di Istruttoria Veloce (CIV),
        entrano nel calcolo del TEG su base annua moltiplicando per 4 gli oneri trimestrali, a meno
        che gli stessi siano previsti contrattualmente una tantum nell’anno, nel qual caso vanno
        ripetuti nei tre trimestri successivi (24);
-       per la definizione di accordato si rimanda al precedente punto B4.
      Nell’Allegato 2 sono riportati alcuni esempi di calcolo del TEG per le aperture di credito in
conto corrente, per gli sconfinamenti su conti correnti affidati e per i passaggi a debito di conti non
affidati.




23
     I giorni strettamente necessari per l’incasso sono computati considerando quelli solari minimi, sulla base delle
     pratiche di mercato, per la ricezione degli effetti dall’eventuale corrispondente che cura l’incasso.
     Per le operazioni di factoring, è possibile utilizzare le modalità di calcolo del conto “scalare” per la determinazione
     dei numeri debitori.
24
     Gli oneri pluriennali sostenuti in via anticipata e in un’unica soluzione (per esempio le spese per la costituzione della
     garanzia nelle aperture di credito ipotecarie o le garanzie prestate da un Confidi) devono essere inclusi nel TEG pro-
     quota in base alla durata del finanziamento ovvero, se non definita, alla durata media stimata dall’intermediario per i
     contratti in essere della stessa tipologia; l’importo annuo così calcolato va incluso nel calcolo del TEG per tutta la
     durata del finanziamento.
     Gli oneri con cadenza infra-annuale vanno riportati ad anno e inclusi in tutti i trimestri del periodo a cui si
     riferiscono.
     In assenza di un affidamento, gli oneri connessi con la presentazione di effetti allo sconto da parte di un cliente
     occasionale devono essere inclusi nel TEG per gli importi effettivamente addebitati per la singola presentazione,
     intesa come complesso degli effetti ceduti nell’arco di una giornata lavorativa, senza annualizzazione.


                                                               - 13 -
                                                      Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

b)       Cat. 3, Cat. 4, Cat. 6, Cat. 7, Cat. 8, Cat. 9b, Cat. 10 e operazioni rientranti nelle categorie di
         cui al punto a) che prevedono il rimborso del prestito con un piano di rientro predefinito.
      In analogia a quanto previsto dal Provvedimento della Banca d’Italia del 15.7.2015 per il
calcolo del TAEG (25), la formula per il calcolo del TEG è la seguente:
                                                                           '
                                                  m
                                                        Ak         m
                                                                            A' k '
                                                
                                                k 1 (1  i )
                                                              tk
                                                                                 t'
                                                                  k ' 1 (1  i )
                                                                                   k




         dove:
i        è il TEG annuo, che può essere calcolato quando gli altri termini dell’equazione sono noti nel
         contratto o altrimenti;
k        è il numero d’ordine di un “prestito”;
k’       è il numero d’ordine di una “rata di rimborso”;
Ak       è l’importo del “prestito” numero K;
A’k’ è l’importo della “rata di rimborso” numero K’;
m        è il numero d’ordine dell’ultimo “prestito”;
m’       è il numero d’ordine dell’ultima “rata di rimborso”;
tk       è l’intervallo espresso in anni e frazioni di anno tra la data del “prestito” n.1 e le date degli
         ulteriori “prestiti” da 2 a m;
tk’      è l’intervallo espresso in anni e frazioni di anni tra la data del “prestito” n.1 e le date delle
         “rate di rimborso” da 1 a m’.
      Per “rata di rimborso” si intende ogni pagamento a carico del cliente relativo al rimborso del
capitale, degli interessi e degli oneri inclusi di cui al punto C4.
      Per “prestito” si intende ciascuna erogazione eseguita dal creditore per effetto di uno stesso
contratto.
      Nel caso di dilazioni o di rinegoziazioni, gli oneri riferiti all’intera durata del finanziamento
dovranno essere inseriti nel TEG in base ad una stima della quota dell’onere imputabile al solo
periodo futuro.
      Ove al momento dell’accensione del rapporto di finanziamento non siano determinabili alcuni
dei termini della formula di calcolo si può procedere, nel calcolo del tasso, a ipotesi esemplificative
coerenti con l’ammontare del fido accordato al cliente e con l’importo minimo della rata di rimborso
previsto dal contratto. In generale, in presenza di elementi non determinabili, si può ritenere che il
cliente adotti la scelta meno onerosa.
    Nei finanziamenti a tasso misto le rate di rimborso devono essere desunte da un piano di
ammortamento del prestito, riferito all’intero periodo e calcolato sulla base dei diversi tassi previsti




25
      Il calcolo del TAEG ai fini di trasparenza e del TEG a fini anti-usura può differire, sulla stessa operazione di
      finanziamento, per diverse motivazioni; tra le altre, per un diverso trattamento degli oneri e delle spese (a titolo di
      esempio le imposte e tasse sono incluse nel TAEG ai fini di trasparenza, mentre sono escluse dal TEG ai fini anti-
      usura ai sensi della Legge 108/96).


                                                                  - 14 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

contrattualmente. I tassi variabili devono essere considerati al valore assunto dal parametro di
riferimento alla data di accensione del prestito.
      In presenza di eventuali opzioni che riconoscono la possibilità di scegliere, successivamente
alla data di accensione del prestito, tra due o più tassi, il piano di ammortamento dovrà essere
calcolato sulla base del minor valore dei tassi stessi alla data di accensione del prestito ovvero sulla
base del tasso contrattualmente previsto in caso di mancato esercizio del diritto di opzione (c.d.
tasso di salvaguardia).
      Nel caso in cui sia stato sottoscritto uno strumento finanziario derivato, al fine di coprirsi dalle
eventuali oscillazioni che il tasso di interesse contemplato dal contratto di finanziamento potrebbe
subire nel corso del rapporto (ad es. interest rate swap che colleghi un finanziamento a tasso
variabile a un tasso fisso predeterminato), ai fini della segnalazione non va considerato il tasso di
interesse risultante a seguito del contratto derivato ma il tasso del finanziamento al momento
dell’apertura del rapporto.

C4. Trattamento degli oneri e delle spese nel calcolo del TEG
      Il calcolo del tasso deve tener conto delle commissioni, remunerazioni a qualsiasi titolo e delle
spese, escluse quelle per imposte e tasse, collegate all’erogazione del credito e sostenute dal cliente,
di cui il soggetto finanziatore è a conoscenza, anche tenuto conto della normativa in materia di
trasparenza.
        In particolare, sono inclusi:
     1) le spese di istruttoria e di revisione del finanziamento (per il factoring le spese di “istruttoria
        cedente”, per il revolving la quota annuale per la parte direttamente connessa con il
        finanziamento 26);
     2) le spese di chiusura della pratica (per il leasing le spese forfettarie di “fine locazione
        contrattuale”);
     3) le spese di riscossione dei rimborsi e di incasso delle rate e degli effetti anche se sostenute
        per il tramite di un corrispondente che cura la riscossione (27); le spese per il servizio di
        trattenuta dello stipendio o della pensione;
     4) il costo dell’attività di mediazione sostenuto dal cliente, in via diretta o tramite
        l’intermediario (28); nell’ambito del rapporto con il mediatore, gli intermediari provvedono
        ad acquisire le necessarie informazioni riguardo ai compensi corrisposti dal cliente;
     5) le spese per assicurazioni o garanzie intese ad assicurare il rimborso totale o parziale del
        credito ovvero a tutelare altrimenti i diritti del creditore, se la conclusione del contratto
        avente ad oggetto il servizio assicurativo è contestuale alla concessione del finanziamento
        ovvero obbligatoria per ottenere il credito o per ottenerlo alle condizioni contrattuali offerte,
        indipendentemente dal fatto che la polizza venga stipulata per il tramite del finanziatore o



26
     Sono escluse le quote riconducibili a servizi non finanziari offerti alla clientela (per es. servizi di pagamento,
     turistici, ecc.).
27
     Non vanno computate le spese effettivamente necessarie per l’incasso nei casi in cui la presentazione degli effetti
     avvenga nell’ambito di un complessivo rapporto di finanziamento ad utilizzo flessibile (ad es. castelletto finalizzato
     all’attivazione di un affidamento in conto corrente).
28
     Eventuali servizi di consulenza prestati dal mediatore non vanno inclusi nel TEG, sempre che si tratti di servizi
     fatturati a parte e non direttamente collegati all’attività di mediazione. Laddove non sia possibile distinguere in modo
     chiaro tra consulenza e mediazione, i relativi oneri vanno inclusi nel TEG. Nel caso in cui sia stato erogato un pre-
     finanziamento, i costi di mediazione vanno inclusi nel TEG del finanziamento “principale”.


                                                               - 15 -
                                                    Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

          direttamente dal cliente (29). Le assicurazioni sul credito (le cosiddette CPI - Cost Protection
          Insurance o PPI - Payment Protection Insurance) e quelle per furto e incendio sono ritenute
          connesse con il finanziamento, e quindi incluse nel calcolo del TEG, anche nei casi in cui il
          beneficiario della polizza non sia l’ente creditore (30);
      6) le spese per servizi accessori, anche se forniti da soggetti terzi, connessi con il contratto di
         credito (ad es. spese di custodia pegno 31, perizie 32, spese postali);
      7) gli oneri per la messa a disposizione dei fondi, le commissioni di istruttoria veloce applicate
         nel caso di passaggio a debito di conti non affidati o negli sconfinamenti rispetto al fido
         accordato;
      8) ogni altra spesa ed onere contrattualmente previsti, connessi con l’operazione di
         finanziamento (33).




29
     Nelle operazioni di prestito indicate nella Cat. 8 le spese per assicurazione in caso di morte, invalidità, infermità o
     disoccupazione del debitore rientrano nel calcolo del tasso.
30
     I contratti assicurativi di carattere del tutto accessorio (per esempio polizze sanitarie, polizze a tutela degli acquisti e
     prelievi effettuati con carta di credito), sia pure contestuali al finanziamento, in cui la polizza non è finalizzata in
     alcun modo al rimborso totale o parziale del credito non rilevano ai fini del calcolo del TEG. Parimenti, non vanno
     inclusi nel calcolo del TEG, le coperture assicurative obbligatorie per legge (es. RC auto) non direttamente connesse
     al rapporto di finanziamento.
     Solo in caso di obiettive difficoltà di stima degli oneri assicurativi per furto ed incendio relativi all’intera durata del
     contratto, è possibile includere nel calcolo del TEG unicamente il premio assicurativo noto relativo al primo anno
     (cfr. Nota Metodologica allegata al DM del 24/12/2009).
31
     Per le spese di custodia pegno l’onere addebitato al cliente deve essere incluso nel calcolo del TEG in una
     proporzione pari al rapporto tra importo finanziato e valore stimato del bene, indipendentemente dalle modalità di
     calcolo delle spese.
32
     Nel caso di perizie con oggetto più esteso rispetto a quanto richiesto per l’ottenimento del credito, potrà essere
     incluso soltanto un costo stimato della quota necessaria per l’erogazione del finanziamento. Qualora l’intermediario
     lasci al cliente la facoltà di avvalersi di un professionista di fiducia per la determinazione del valore dell’immobile
     offerto a cauzione, l’onere riferito a perizie può essere stimato basandosi sugli oneri per un analogo servizio offerto
     dal soggetto finanziatore o su valori medi di mercato.
33
     La polizza SACE, posta a garanzia dell’operazione di esportazione, non deve essere inclusa nel calcolo del TEG, se
     stipulata a copertura del rischio relativo all’operazione di esportazione e non direttamente connessa con il
     finanziamento. L’eventuale polizza a tutela del creditore e connessa con l’operazione di finanziamento deve rientrare
     invece nel calcolo del TEG.
     Le assicurazioni di tipo all risk, stipulate dal cliente volte a coprire l’intera attività aziendale, il cui beneficiario è
     l’azienda e non l’intermediario, vanno escluse dal calcolo del TEG, a meno che siano richieste in via obbligatoria per
     l’ottenimento del credito o per l’applicazione di determinate condizioni contrattuali.
     Per i mutui a s.a.l. i costi assicurativi, quelli relativi a perizie intermedie e al frazionamento del mutuo diversi da
     quelli sostenuti o conosciuti in sede di accensione del mutuo, laddove sussistano oggettive difficoltà di stima,
     possono essere esclusi dal calcolo del TEG.
     Nel caso di “pacchetti assicurativi complessi” sarà necessario distinguere – eventualmente facendo ricorso a stime –
     la parte di polizza connessa con il finanziamento, da quella accessoria (ad es. kasko) includendo nel TEG solo la
     prima parte.
     Le spese relative all’eventuale certificazione degli interessi sui mutui non devono essere incluse nel TEG.
     Nel caso di stipula di due mutui con ipoteca sullo stesso immobile e contestuale polizza assicurativa vincolata ad
     entrambi i mutui, i costi della polizza da inserire in ciascun TEG devono essere determinati in proporzione
     all’ammontare dei due capitali finanziati. Nel caso di stipula di un secondo mutuo con ipoteca di 2° grado su un
     immobile già assicurato in occasione del primo mutuo, va incluso nel TEG il premio assicurativo per il mutuo
     stipulato successivamente relativo alla sola estensione.


                                                                 - 16 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

       Nel caso di fidi promiscui gli oneri, qualora non specificamente attribuibili a una categoria di
operazioni, vanno imputati per intero a ciascuna di esse. Tali oneri sono invece imputati pro quota
qualora per talune categorie di operazioni siano previste limitazioni per singola modalità di utilizzo;
la ripartizione pro quota andrà riferita anche al fido accordato.


        Sono esclusi:
a)      le imposte e tasse (34);
b)      le spese notarili (ad es. onorario, visure catastali, iscrizione nei pubblici registri, spese relative
        al trasferimento della proprietà del bene oggetto di leasing);
c)      i costi di gestione del conto sul quale vengono registrate le operazioni di pagamento e di
        prelievo, i costi relativi all’utilizzazione di un mezzo di pagamento che permetta di effettuare
        pagamenti e prelievi e gli altri costi relativi alle operazioni di pagamento, a meno che il conto
        non sia a servizio esclusivo del finanziamento (35);
d)      gli interessi di mora e gli oneri assimilabili contrattualmente previsti per il caso di
        inadempimento di un obbligo;
e)      con riferimento al factoring e al leasing, i compensi per prestazioni di servizi accessori di tipo
        amministrativo non direttamente connessi con l'operazione di finanziamento.
      Le penali a carico del cliente previste in caso di estinzione anticipata del rapporto, laddove
consentite, sono da ritenersi meramente eventuali, e quindi non vanno aggiunte alle spese di
chiusura della pratica.

C5. Calcolo dell’importo erogato.
     La metodologia di calcolo dell’importo erogato varia a seconda delle diverse categorie di
operazioni individuate:




     Le spese di gestione e amministrazione titoli e gli eventuali costi di movimentazione (compravendita titoli) applicate
     in caso di garanzia con pegno su titoli già presenti in un deposito amministrato dalla banca – che sarebbero percepite
     indipendentemente dalla circostanza che il deposito amministrato sia posto a garanzia – non devono essere
     considerate qualora il deposito non sia a servizio esclusivo del finanziamento.
     Nelle operazioni di prestito su pegno le spese sostenute da soggetti garanti, diversi dal cliente finanziato, sono da
     escludere dal calcolo del TEG a meno che non ricadano, anche in via indiretta, sul soggetto finanziato. Le
     commissioni di carattere eventuale previste in caso di vendita di beni in pegno non riscattati (es.: rimborso spese per
     l’attività di vendita e rimborso spese esposizione) sono da escludere dal calcolo del TEG, al pari delle altre spese
     addebitate in caso di un inadempimento contrattuale.
     Per i finanziamenti garantiti dai Confidi o da Fondi di garanzia gli oneri sostenuti dal cliente sono da includere nel
     TEG per la parte direttamente riferibile alla specifica operazione di finanziamento; in particolare vanno incluse le
     spese di istruttoria accessorie alla pratica e le commissioni di garanzia corrisposte all’atto dell’erogazione del
     prestito. Sono invece esclusi l’acquisto di azioni o di quote sociali, il versamento di depositi cauzionali una tantum e
     le spese ricorrenti genericamente connesse con la partecipazione del socio ai benefici della mutualità e con la
     prestazione di ulteriori servizi.
34
     Il costo di bollatura delle cambiali deve essere escluso dal calcolo del TEG. Parimenti deve essere escluso il costo
     del contrassegno telematico per effetto della sua natura di prelievo fiscale, in quanto sostitutivo delle marche da
     bollo cartacee.
35
     Ad esempio in caso di credito revolving o di finanziamento con utilizzo di carta di credito sono escluse le spese di
     produzione e invio dell’estratto conto, le commissioni sugli acquisti di carburante e gli oneri per l’anticipo di
     contante in quanto relativi all’utilizzo della carta di credito come mezzo di pagamento.


                                                               - 17 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

a)      Cat. 1, Cat. 5 e Cat. 9a
       Nell’ambito di ciascun rapporto, per importo erogato si intende il saldo medio nel trimestre
calcolato rapportando i numeri debitori (di cui al precedente punto C3) al numero di giorni effettivi
del trimestre. Nei casi di passaggio a debito di conti non affidati i giorni da considerare sono quelli
sui quali sono maturati gli interessi a debito. Nel caso di operazioni di factoring che non diano luogo
a posizioni debitorie nei confronti del cedente il valore da prendere in considerazione è la somma
degli anticipi erogati nel trimestre.

b)      Cat. 2a
      Nell’ambito di ciascun rapporto, ad eccezione degli anticipi s.b.f., per importo erogato si
intende la somma degli importi concessi a fronte dello sconto effetti. Per gli anticipi s.b.f. per
importo erogato si intende il saldo medio nel trimestre.

c)        Altre categorie di operazioni
        Per importo erogato si intende il fido accordato o il capitale finanziato (cfr. punto B4).


     Nel caso di fidi promiscui, relativi a categorie di finanziamento diverse, va considerato
l’importo erogato per ciascuna categoria.

C6. Calcolo del compenso di mediazione (MED)
     Il compenso di mediazione, che rileva ai fini della presente rilevazione, comprende sia la
commissione a carico del soggetto finanziatore sia quella a carico del cliente, a fronte di una attività
di mediazione svolta dai mediatori creditizi iscritti nell’elenco istituito ai sensi dell’art. 128-sexies
del TUB.
     Per ciascuna operazione finanziaria il compenso percepito per l’attività di mediazione (36)
deve essere rapportato all’ammontare finanziato utilizzato per individuare la classe d’importo (cfr.
punto B4) e segnalato in misura percentuale:

                                                       Commissione  100
                                         MED =
                                                      Ammontare finanziato

D) NORME TRANSITORIE
D1. Periodo transitorio (1° ottobre 2016 – 31 marzo 2017)
      Fino al 31 marzo 2017, al fine di verificare il rispetto del limite oltre il quale gli interessi sono
sempre usurari ai sensi dell’articolo 2, comma 4, della legge 7 marzo 1996, n. 108, gli intermediari
devono attenersi ai criteri indicati nelle Istruzioni della Banca d'Italia pubblicate nella G.U. n. 200
del 29 agosto 2009.




36
     Eventuali servizi di consulenza prestati dal mediatore non vanno inclusi nel MED, sempre che si tratti di servizi
     fatturati a parte e non direttamente collegati all’attività di mediazione. Laddove non sia possibile distinguere in modo
     chiaro tra consulenza e mediazione, i relativi oneri vanno inclusi nel MED. Nel caso in cui sia stato erogato un pre-
     finanziamento, i costi di mediazione vanno inclusi nel MED del finanziamento “principale”.


                                                               - 18 -
                                          Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

D2. Primo invio dei dati in base alle presenti Istruzioni
      I dati determinati in base alle presenti Istruzioni devono essere segnalati a partire dal trimestre
ottobre-dicembre 2016 (scadenza 25 gennaio 2017).




                                                      - 19 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016


                                                                                                                  Allegato 1

                             SEGNALAZIONI AI SENSI DELLA LEGGE SULL'USURA
                                        Categorie e classi d'importo

       CATEGORIA OPERAZIONI                                         CLASSI DI IMPORTO (in unità di euro)
                                                                                >25.000-       >50.000-
                                                     0-5.000    >5.000-25.000                                            >100.000
                                                                                 50.000        100.000
1-a   Apertura di credito in c/c con garanzia           X            X             X               X                         X
1-b   Apertura di credito in c/c senza garanzia         X            X             X               X                         X
                                                     0-1.500      1.500-5.000       >5.000-25.000         >25.000
      Passaggi a debito di conti senza
1-c                                                     X               X                  X                  X
      affidamento
                                                                                       >50.000-          >100.000-
                                                    0-25.000 >25.000-50.000                                              >200.000
                                                                                       100.000            200.000
      Finanziamenti per anticipi su crediti e
2a    documenti - sconto di portafoglio                 X               X                  X                  X              X
      commerciale

2b    Finanziamenti all’importazione e anticipo         X               X                  X                  X              X
      fornitori
                                                                                       >15.000-
                                                     0-5.000    >5.000-15.000                             >25.000
                                                                                        25.000
3     Credito personale                                 X               X                 X                   X
                                                     0-1.500      1.500-5.000           >5.000
4     Credito finalizzato                               X             X                  X
                                                                   >50.000-           >100.000-
                                                    0-50.000                                             >500.000
                                                                   100.000             500.000
5     Factoring                                         X             X                  X                  X
                                                                                      >25.000-           >50.000-            >
                                                     0-5.000    >5.000-25.000
                                                                                       50.000            100.000          100.000
6-a   Leasing strumentale                               X               X                X                  X                X

                                                                                      >50.000-
                                                    0-25.000 >25.000-50.000                              >100.000
                                                                                       100.000
6-b   Leasing autoveicoli-aeronavale                    X             X                  X                    X
                                                       0-          >100.000-          >250.000-
                                                                                                         >500.000
                                                     100.000        250.000            500.000
6-c   Leasing immobiliare a tasso fisso                 X             X                  X                    X
6-d   Leasing immobiliare a tasso variabile             X             X                  X                    X
                                                       0-          >100.000-          >250.000-
                                                                                                         >500.000
                                                     100.000        250.000            500.000
      Mutui a tasso fisso - unità produttive
7-a                                                     X               X                  X                  X
      private
      Mutui a tasso fisso - famiglie
7-b                                                     X               X                  X                  X
      consumatrici
      Mutui a tasso variabile - unità produttive
7-c                                                     X               X                  X                  X
      private
      Mutui a tasso variabile - famiglie
7-d                                                     X               X                  X                  X
      consumatrici
                                                                                       >15.000-
                                                     0-5.000    >5.000-15.000                             >25.000
                                                                                        25.000
      Prestiti contro cessione del quinto dello
8-a                                                     X               X                  X                  X
      stipendio e della pensione - stipendi
      Prestiti contro cessione del quinto dello
8-b                                                     X               X                  X                  X
      stipendio e della pensione - pensioni


                                                               - 20 -
                                                   Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

                                                                                                         >10.000-
                                                     0-1.500     >1.500-5.000       >5.000-10.000                        > 25.000
                                                                                                          25.000
9-a   Credito revolving                                 X               X                 X                 X                X
9-b   Finanziamenti a valere su carte di credito        X               X                 X                 X                X
                                                                                       >25.000-          >50.000-            >
                                                     0-5.000    >5.000-25.000
                                                                                        50.000           100.000          100.000
10-a Altri finanziamenti - unità prod. private          X               X                  X                  X              X
10-b Altri finanziamenti – fam. consumatrici            X               X                  X                  X              X




                                                               - 21 -
                                              Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

                                                                                                            Allegato 2


                     ESEMPI DI CALCOLO DEL TEG PER LA CATEGORIA 1


    A) TEG - APERTURE DI CREDITO IN CONTO CORRENTE ENTRO IL FIDO

Esempio 1

Accordato                                                                                                    10.000 euro

Tasso debitore nominale annuo %                                                                                    12,00

Commissione messa a disposizione fondi                                         0,5% dell’accordato, su base trimestrale

Numeri debitori                                                                                                  455.000

Interessi                                                                           455.000 * 12% / 365 = 149,59 euro

Commissione messa a disposizione fondi addebitata nel
                                                                                           0,5% * 10.000 = 50,00 euro
trimestre

                                                                        149,59  36.500 (50  4) 100
TEG %                                                                                                 14,00
                                                                           455.000         10.000



    B) TEG - APERTURE DI CREDITO IN CONTO CORRENTE OLTRE IL FIDO

Esempio 2

Accordato                                                                                                    10.000 euro

Saldo liquido massimo di segno negativo                                                                      13.000 euro

Tasso debitore nominale annuo %                                                                                    12,00

Commissione messa a disposizione fondi                                         0,5% dell’accordato, su base trimestrale

Commissione di Istruttoria Veloce (CIV)                                              60,00 euro per ogni sconfinamento

Numeri debitori                                                                                                  455.000

Interessi                                                                           455.000 * 12% / 365 = 149,59 euro

Commissione messa a disposizione fondi addebitata nel
                                                                                           0,5% * 10.000 = 50,00 euro
trimestre

CIV (2 eventi nel trimestre)                                                                                 120,00 euro



                                                          - 22 -
                                          Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

                                                       149,59  36.500 (50  4  120  4)  100
TEG %                                                                                           17,23
                                                          455.000              13.000




    C) TEG - PASSAGGIO A DEBITO DI UN CONTO CORRENTE NON AFFIDATO

Esempio 3

Saldo liquido massimo di segno negativo                                                                   6.000 euro

Tasso debitore nominale annuo %                                                                                 12,00

Commissione di Istruttoria Veloce (CIV)                                          60,00 euro per ogni sconfinamento

Numeri debitori                                                                                              455.000

Interessi                                                                       455.000 * 12% / 365 = 149,59 euro

CIV (2 eventi nel trimestre)                                                                             120,00 euro

                                                                  149,59  36.500 (120  4) 100
TEG %                                                                                            20,00
                                                                     455.000          6.000




                                                      - 23 -
                                          Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016


                                       SEZIONE II
           MODALITÀ TECNICO-OPERATIVE PER
            L’INOLTRO DELLE INFORMAZIONI
Premessa
       I dati dovranno essere inviati alla Banca d’Italia - Servizio Rilevazioni ed Elaborazioni
Statistiche attraverso il canale Internet avvalendosi della procedura ”INFOSTAT” accessibile dal
sito web dell’Istituto.

Modalità di segnalazione dei dati
      I tassi e i compensi di mediazione vanno segnalati in percentuale con tre cifre decimali senza
indicazione della virgola; il numero dei rapporti in unità. L’importo erogato medio va segnalato in
unità di euro.
     La rilevazione va effettuata anche nel caso in cui le singole istituzioni non abbiano dati da
comunicare. Tale evenienza va segnalata mediante l’utilizzo della voce “segnalazione negativa”
(31440/00), inserendo convenzionalmente il valore 1 nel campo riservato all’importo.

Sistema delle codifiche
a) classi di importo (codice campo 599 - lunghezza 2)
       L’informazione è richiesta per ciascuna delle categorie di operazioni. I valori previsti sono:
69 -    fino a 1.500 euro
97 -    fino a 5.000 euro
98 -    fino a 25.000 euro
88 -    fino a 50.000 euro
38 -    fino a 100.000 euro
40 -    da oltre 1.500 euro fino a 5.000 euro
22 -    da oltre 5.000 euro fino a 10.000 euro
42 -    da oltre 5.000 euro fino a 15.000 euro
43 -    da oltre 5.000 euro fino a 25.000 euro
23 -    da oltre 10.000 euro fino a 25.000 euro
44 -    da oltre 15.000 euro fino a 25.000 euro
45 -    da oltre 25.000 euro fino a 50.000 euro
76 -    da oltre 50.000 euro fino a 100.000 euro
19 -    da oltre 100.000 euro fino a 200.000 euro
39 -    da oltre 100.000 euro fino a 250.000 euro
21 -    da oltre 100.000 euro fino a 500.000 euro
94 -    da oltre 250.000 euro fino a 500.000 euro
68 -    oltre 5.000 euro

                                                      - 24 -
                                          Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

18 -    oltre 25.000 euro
77 -    oltre 100.000 euro
20 -    oltre 200.000 euro
95 -    oltre 500.000 euro

b) tipo importo (codice campo 350 - lunghezza 3)
       Individua il contenuto dell’importo segnalato. I valori previsti sono:
013 - tasso effettivo globale medio;
014 - numero rapporti su cui è stato calcolato il tasso effettivo globale medio;
017 - importo erogato medio;
018 - compenso medio percentuale per l’attività di mediazione;
019 - numero di rapporti che hanno concorso alla determinazione del compenso medio.

c) durata (prevista nella parte fissa del “record movimento” - lunghezza 2)
       L’informazione non è richiesta ai fini delle segnalazioni. Indicare convenzionalmente “3”.

d) residenza e valuta (previste nella parte fissa del “record movimento” - lunghezza 1)
      Le informazioni non sono richieste ai fini delle segnalazioni. Indicare convenzionalmente “1”
per entrambe le informazioni.

Schemi di segnalazione
       Gli schemi di segnalazione sono riportati nell’allegato 3.




                                                      - 25 -
                                     Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

                                                                                                      Allegato 3

                        SEGNALAZIONI AI SENSI DELLA LEGGE SULL'USURA

                                   Schemi di segnalazione
                                                                                          D   D   R     C    T    P
                                                                                          U   I   E     L    I    E
                                                                                          R   V   S     A    P    R
                                                                                          A   I   I     S    O    I
                                                                                          T   S   D     S         O
                                                                            VOCE          A   A   E     E     I   D
                                                                                                  N          M    I
                       Forma tecnica                                                              Z      I   P    C
                                                                                                  A     M    O    I
                                                                                                        P    R    T
                                                                                                        O    T    A'
                                                                                                        R    O
                                                                                                        T
                                                                               SOTVOC
                                                                                                        O

                                                        C odice variabile                               5    3
                                                                                                        9    5
                                                                                                        9    0
APERTURA DI CREDITO IN C/C:                                                  31400
  - CON GARANZIA                                                                     02   3   1   1     X    X    T
  - SENZA GARANZIA                                                                   04   3   1   1     X    X    T
  - PASSAGGI A DEBITO DI CONTI SENZA AFFIDAMENTO                                     06   3   1   1     X    X    T

FINANZIAMENTI:                                                               31405
 - PER ANTICIPI SU CREDITI E DOCUMENTI - SCONTO DI
   PORTAFOGLIO COMMMERCIALE                                                          02   3   1   1     X    X    T
 - FINANZIAMENTI ALL'IMPORTAZIONE E ANTICIPO FORNITORI                               04   3   1   1     X    X    T

CREDITO PERSONALE                                                            31410 02     3   1   1     X    X    T

CREDITO FINALIZZATO                                                          31415 03     3   1   1     X    X    T

FACTORING                                                                    31420 00

LEASING:                                                                     31425
 - STRUMENTALE                                                                       02   3   1   1     X    X    T
 - IMMOBILIARE:
   - A TASSO FISSO                                                                   07   3   1   1     X    X    T
   - A TASSO VARIABILE                                                               09   3   1   1     X    X    T
 - AUTOVEICOLI-AERONAVALE                                                            10   3   1   1     X    X    T

MUTUI:                                                                       31430
A TASSO FISSO:
 - UNITA' PRODUTTIVE PRIVATE                                                         06   3   1   1     X    X    T
 - FAMIGLIE CONSUMATRICI                                                             08   3   1   1     X    X    T
A TASSO VARIABILE:
 - UNITA' PRODUTTIVE PRIVATE                                                         10   3   1   1     X    X    T
 - FAMIGLIE CONSUMATRICI                                                             12   3   1   1     X    X    T

PRESTITI CONTRO CESSIONE DEL QUINTO DELLO STIPENDIO
E DELLA PENSIONE:                                                            31432
 - STIPENDI                                                                          02   3   1   1     X    X    T
 - PENSIONI                                                                          04   3   1   1     X    X    T

CREDITO REVOLVING E CON UTILIZZO DI CARTE DI CREDITO                         31434
 - CREDITO REVOLVING                                                                 02   3   1   1     X    X    T
 - FINANZIAMENTI A VALERE SULL'UTILIZZO DI CARTE DI
   CREDITO CON DURATA PREDETERMINATA E PIANO DI AMMORTAMENTO
   PREDEFINITO                                                                       04   3   1   1     X    X    T

ALTRI FINANZIAMENTI:                                                         31438
 - UNITÀ PRODUTTIVE PRIVATE                                                          02   3   1   1     X    X    T
 - FAMIGLIE CONSUMATRICI                                                             04   3   1   1     X    X    T



                                                 - 26 -
                                     Istruzioni per la rilevazione dei tassi effettivi globali medi – luglio 2016

                                                                                              Allegato 3 (segue)

                        SEGNALAZIONI AI SENSI DELLA LEGGE SULL'USURA

                                   Schemi di segnalazione
                                                                                          D    D    R   C    T    P
                                                                                          U    I    E   L    I    E
                                                                                          R    V    S   A    P    R
                                                                                          A    I    I   S    O    I
                                                                                          T    S    D   S         O
                                                                            VOCE          A    A    E   E     I   D
                                                                                                    N        M    I
                       Forma tecnica                                                                Z    I   P    C
                                                                                                    A   M    O    I
                                                                                                        P    R    T
                                                                                                        O    T    A'
                                                                                                        R    O
                                                                                                        T
                                                                               SOTVOC
                                                                                                        O

                                                        C odice variabile                               5    3
                                                                                                        9    5
                                                                                                        9    0
COMPENSO DI MEDIAZIONE:                                                      31437
 - APERTURA DI CREDITO IN C/C:                                                       02   3     1   1   -    X    T
 - FINANZIAMENTI PER ANTICIPI SU CREDITI E DOCUMENTI
   E SCONTO DI PORTAFOGLIO COMMERCIALE                                               04   3     1   1   -    X    T
 - CREDITO PERSONALE                                                                 06   3     1   1   -    X    T
 - CREDITO FINALIZZATO                                                               08   3     1   1   -    X    T
 - FACTORING                                                                         10   3     1   1   -    X    T
 - LEASING                                                                           12   3     1   1   -    X    T
 - MUTUI                                                                             14   3     1   1   -    X    T
 - PRESTITI CONTRO CESSIONE DEL QUINTO DELLO STIPENDIO E DELLA
   PENSIONE                                                                          16   3     1   1   -    X    T
 - CREDITO REVOLVING E CON UTILIZZO DI CARTE DI CREDITO                              18   3     1   1   -    X    T
 - ALTRI FINANZIAMENTI:
   - FAMIGLIE                                                                        22   3     1   1   -    X    T
   - IMPRESE                                                                         24   3     1   1   -    X    T

SEGNALAZIONE NEGATIVA                                                        31440 00     3     1   1   -    -    T
(Da compilare unicamente se tutte le voci da 31400 a
 31438 presentano importi nulli. In tal caso va
 convenzionalmente indicato il valore "1" nel campo importo)

Legenda
X : informazione richiesta
- : informazione non richiesta


N.B.:
  - I tassi e i compensi di mediazione vanno segnalati in percentuale con tre cifre decimali
    senza indicazione della virgola (es: 10% = 10000);
  - il numero dei rapporti va segnalato in unità;
  - l'importo erogato medio va segnalato in unità di euro.




                                                 - 27 -
