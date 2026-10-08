---
{
  "id": "035",
  "numero": 35,
  "sub": null,
  "titolo": "Iscrizione a ruolo – Tabelle del cu",
  "tipo_atto": "atto",
  "forma_introduttiva": "atto",
  "rito": "ordinario di cognizione",
  "fase": "cognizione di primo grado",
  "materia": "cognizione ordinaria",
  "competenza_orientativa": "Tribunale ordinario, monocratico",
  "norme_chiave": [
    "art. 473-bis.51 c.p.c.",
    "art. 492-bis c.p.c.",
    "d.P.R. 115/2002",
    "d.lgs. 195/2005",
    "d.lgs. 104/2010",
    "D.LGS. 168/2003"
  ],
  "changelog_deps": [
    "cartabia_processo_civile",
    "parametri_forensi"
  ],
  "volatilita": "alta",
  "fonte": "Catalogo dei modelli d'atto (testi di febbraio 2026)",
  "data_formulario": "2026-02",
  "verificato_il": "2026-07-04",
  "prossima_verifica": "2027-07-04",
  "stato": "congelato",
  "giurisprudenza_stato": "da_popolare",
  "selezione_keywords": [
    "atto",
    "cognizione",
    "iscrizione",
    "ruolo",
    "tabelle"
  ]
}
---

# 35 · Iscrizione a ruolo – Tabelle del cu

> Scheda-modello **local-first**. Scaffold verificato per la **selezione** in F1 del `collegio-redazione`.
> L'inquadramento autorevole (tipo · rito · competenza · struttura) resta di **F1.5** (albero `struttura-atti.md` + round di verifica: Livello 0 + due agenti). Un fac-simile **non e' fonte di diritto**.

## Quando si usa
- Materia: **cognizione ordinaria** · Fase: **cognizione di primo grado**
- Forma introduttiva tipica: **atto** · Rito: **ordinario di cognizione**

## Inquadramento (orientativo — decide F1.5)
- Competenza orientativa: **Tribunale ordinario, monocratico**
- Rito: **ordinario di cognizione**
- ⚠️ Verifica in **F1.5**: GATE intertemporale (data di instaurazione), competenza per valore/materia/territorio, forma dell'atto.

## Normativa di riferimento (ancore estratte dal modello)
- art. 473-bis.51 c.p.c.
- art. 492-bis c.p.c.
- d.P.R. 115/2002
- d.lgs. 195/2005
- d.lgs. 104/2010
- D.LGS. 168/2003

Dipendenze di freschezza (changelog): **cartabia_processo_civile, parametri_forensi** — cfr. `wiki-studio/normativa/changelog-riforme.md`.
La freschezza del modello e' derivata da queste voci (vedi `scripts/freshness.py --modelli`).

## Note e trappole post-Cartabia
- La **citazione** introduce il rito **ordinario** (art. 163 c.p.c.). Non confondere col **semplificato** ex art. 281-decies, che si introduce con **RICORSO** (281-undecies).
- Memorie: art. **171-ter** c.p.c. (post-Cartabia). Il vecchio schema 183 c.6 non esiste piu'.
- **GATE intertemporale**: per i giudizi instaurati **prima del 28/02/2023** vale il regime previgente (es. 702-bis). L'inquadramento definitivo lo fa **F1.5**.

## Giurisprudenza
⏳ **Da popolare con giurisprudenza VERIFICATA** (One Legale on-demand in fase di redazione, oppure Sentinella).
Regola anti-allucinazione: **nessuna massima non verificata** entra in questa sezione.

## Testo del modello (fac-simile — Formulario del processo civile (ed. febbraio 2026))
```
35.	Iscrizione a ruolo – Tabelle del cu
(Min. giust., circolare 12 maggio 2014)
CONTRIBUTO UNIFICATO
Processo civile ordinario
Valore	Primo grado	Impugnazione	Cassazione
Processi di valore fino a € 1.100,00	€ 43,00	€ 64,50	€ 86,00
Processi di valore superiore a
€ 1.100,00 e fino a € 5.200,00	€ 98,00	€ 147,00	€ 196,00
Processi di valore superiore a
€ 5.200,00 e fino a € 26.000,00	€ 237,00	€ 355,50	€ 474,00
Processi di valore superiore a
€ 26.000,00 e fino a € 52.000,00	€ 518,00	€ 777,00	€ 1.036,00
Processi di valore superiore a
€ 52.000,00 e fino a € 260.000,00	€ 759,00	€ 1.138,50	€ 1.518,00
Processi di valore superiore a
€ 260.000,00 e fino a € 520.000,00	€ 1.214,00	€ 1.821,00	€ 2.428,00
Processi di valore superiore a
€ 520.000,00	€ 1.686,00	€ 2.529,00	€ 3.372,00
Processi di valore indeterminabile	€ 518,00	€ 777,00	€ 1.036,00

Marca da bollo da euro 27,00 per le spese di giustizia
CONTRIBUTO RIDOTTO RISPETTO AL PROCESSO CIVILE ORDINARIO
Valore	Riduzione del
contributo
Procedimenti Speciali previsti nel Libro IV titolo I c.p.c. anche se proposti nella causa di merito:
Procedimento d’ingiunzione
Procedimento per la convalida di sfratto
Procedimento cautelare
Provvedimenti possessori	50%
Giudizio di opposizione a decreto ingiuntivo	50%
Giudizio di sfratto per morosità	50%
Giudizio di sfratto per finita locazione	50%
Giudizio di opposizione alla sentenza dichiarativa di fallimento	50%
Controversie individuali di lavoro o concernenti rapporti di pubblico impiego, salvo quanto previsto dall’art. 9, comma 1-bis del d.P.R. 115/2002	50%
(segue)


CONTRIBUTO ORDINARIO 
Per i processi in materia di locazione
Per i processi in materia di comodato
Per i processi in materia di occupazione senza titolo
Per i processi in materia di impugnazione di delibere condominiali
PROCEDIMENTI DI SEPARAZIONE E DIVORZIO
Procedimento	Contributo
Separazione consensuale (domanda congiunta, art. 473-bis.51 c.p.c.)	€ 43,00
Divorzio su domanda congiunta (art. 473-bis.51 c.p.c.)	€ 43,00
Procedimento di divorzio
(scioglimento matrimonio; cessazione degli effetti civili del matrimonio concordatario)	€ 98,00
Separazione giudiziale	€ 98,00

ALTRI PROCEDIMENTI
Procedimento	Importo del contributo
Procedimenti di volontaria giurisdizione	€ 98,00
Reclami contro i provvedimenti cautelari
(circ. min. 31 luglio 2002, n. 5)	€ 147,00
Il reclamo è considerato, ai fini del CU, strumento di impugnazione e
dunque il contributo va
incrementato della metà
Regolamento di competenza e regolamento di giurisdizione	CU ordinario
Opposizione ad ordinanza-ingiunzione	CU ordinario
oltre a spese forfetizzate secondo l’importo di cui all’art. 30 d.P.R. 115/2002

PROCEDIMENTI DI ESECUZIONE
Procedimento	Importo del contributo
Processi di esecuzione per consegna o rilascio	€ 139,00
Processi di esecuzione mobiliare di valore inferiore a € 2.500,00	€ 43,00
Processi di esecuzione mobiliare di valore superiore a € 2.500,00	€ 139,00
Esecuzione forzata di obblighi di fare o non fare	€ 139,00
Processi di esecuzione immobiliare	€ 278,00
Processi di opposizione agli atti esecutivi	€ 168,00
Ricerca con modalità telematiche dei beni da pignorare (art. 492-bis c.p.c.)	€ 43,00

PROCEDIMENTI DI DIRITTO FALLIMENTARE
Procedimento	Importo del contributo
Insinuazione tempestiva al passivo	Esente
Dalla sentenza dichiarativa di fallimento alla chiusura	€ 851,00
Opposizione alla sentenza dichiarativa di fallimento alla chiusura	CU ridotto della metà
Istanza di fallimento	€ 98,00

PROCEDIMENTI ESENTI
Procedimento	Importo del
contributo
Procedimenti di rettificazione di stato civile	Esente
Processi in materia tavolare	Esente
Procedimenti di cui al libro IV, titolo II, capi II, III, IV e V, del c.p.c., tra cui:
Procedimenti di assenza e morte presunta
Procedimenti di assenza e morte presunta	Esente
Procedimenti in materia di assegni per il mantenimento della prole o riguardanti la stessa	Esente
Processi di cui all’art. 3, della legge 24 marzo 2001, n. 89 (legge “Pinto”)	Esente
Procedure di lavoro con i requisiti di cui all’art. 9, comma 1-bis T.U. 115/2002
Procedimenti relativi alla esecuzione mobiliare o immobiliare delle sentenze o ordinanze emesse nei giudizi di lavoro	Esente

PROCEDIMENTI DI LAVORO, PREVIDENZA E ASSISTENZA OBBLIGATORIA
Procedimento	Importo del
contributo
Controversie di previdenza ed assistenza obbligatorie
(Per i decreti ingiuntivi l’importo è ridotto della metà)	€ 43,00
Controversie individuali di lavoro o concernenti rapporti di pubblico impiego	CU ridotto del 50% rispetto al processo civile ordinario
Esecuzione mobiliare o immobiliare delle sentenze o ordinanze emesse nei giudizi di lavoro	Esente
Giudizio di Cassazione	CU ordinario

PROCEDIMENTI DAVANTI AL T.A.R. E AL CONSIGLIO DI STATO
Procedimento	Importo del contributo
Ricorsi in materia di accesso ai documenti amministrativi	€ 300,00
Ricorsi avverso il silenzio	€ 300,00
Ricorsi di esecuzione della sentenza o ottemperanza del giudicato	€ 300,00
Ricorsi avverso il diniego di accesso alle informazioni di cui al d.lgs. 195/2005, di attuazione della direttiva 2003/4/CE sull’accesso del pubblico all’informazione ambientale	Esente
Ricorsi aventi ad oggetto rapporti di pubblico impiego	Contributo ridotto a metà, salvo quanto previsto dall’art. 9, comma 1-bis
Ricorsi cui si applica il rito abbreviato comune a determinate materie previsto dal libro IV, titolo V, del decreto legislativo 2 luglio 2010, n. 104, nonché da altre disposizioni che richiamino il citato rito	€ 1.800,00
Ricorsi avverso i provvedimenti previsti dall’art. 119, comma 1, lettere a), b) del d.lgs. 104/2010: a) i provvedimenti concernenti le procedure di affidamento di pubblici lavori, servizi e forniture, salvo quanto previsto dagli articoli 120 e seguenti; b) i provvedimenti adottati dalle Autorità amministrative indipendenti, con esclusione di quelli relativi al rapporto di servizio con i propri dipendenti
Valore della controversia uguale o inferiore ad € 200.000,00
Valore della controversia tra € 200.000,00 ed € 1.000.000,00
Valore della controversia superiore ad € 1.000.000,00	€ 2.000,00
€ 4.000,00
€ 6.000,00
Ricorso straordinario al Presidente della Repubblica	€ 650,00
Altri ricorsi	€ 650,00
Nei casi di cui all’art. 13, comma 6-bis, d.P.R. 115/2002 (contributo unificato per i ricorsi proposti davanti T.A.R. e Consiglio di Stato) il contributo è aumentato della metà per i giudizi di impugnazione	

RICORSI PRINCIPALI E INCIDENTALI AVANTI ALLE 
COMMISSIONI TRIBUTARIE PROVINCIALI E REGIONALI
Valore	Importo del
contributo
Controversie di valore fino ad € 2.583,28	€ 30,00
Controversie di valore superiore ad € 2.583,28 e fino a € 5.000,00	€ 60,00
Controversie di valore superiore ad € 5.000,00 e fino a € 25.000,00	€ 120,00
Controversie di valore superiore a € 25.000,00 e fino a € 75.000,00	€ 250,00
Controversie di valore superiore a € 75.000,00 e fino a € 200.000,00	€ 500,00
Controversie di valore superiore ad € 200.000,00	€ 1.500,00


IMPRESA (D.LGS. 168/2003)
Per i processi di competenza delle sezioni specializzate in materia di impresa, il CU è il doppio rispetto al processo ordinario (v. legge 24 marzo 2012, n. 27).

AZIONE CIVILE NEL PROCEDIMENTO PENALE
Il contributo unificato è dovuto in misura pari al CU ordinario ma solo se è formulata richiesta di condanna al pagamento di una somma di danaro e la domanda è accolta. In caso di richiesta di condanna generica, il CU non è dovuto.
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
