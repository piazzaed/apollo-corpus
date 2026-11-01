---
{
  "id": "006",
  "numero": 6,
  "sub": null,
  "titolo": "Parcella",
  "tipo_atto": "atto",
  "forma_introduttiva": "atto",
  "rito": "n/a",
  "fase": "rapporto col cliente",
  "materia": "attivita' preliminare / patrocinio",
  "competenza_orientativa": "Tribunale ordinario, monocratico",
  "norme_chiave": [
    "d.m. 55/2014"
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
    "attivita'",
    "atto",
    "parcella"
  ]
}
---

# 6 · Parcella

> Scheda-modello **local-first**. Scaffold verificato per la **selezione** in F1 del `collegio-redazione`.
> L'inquadramento autorevole (tipo · rito · competenza · struttura) resta di **F1.5** (albero `struttura-atti.md` + round di verifica: Livello 0 + due agenti). Un fac-simile **non e' fonte di diritto**.

## Quando si usa
- Materia: **attivita' preliminare / patrocinio** · Fase: **rapporto col cliente**
- Forma introduttiva tipica: **atto** · Rito: **n/a**

## Inquadramento (orientativo — decide F1.5)
- Competenza orientativa: **Tribunale ordinario, monocratico**
- Rito: **n/a**
- ⚠️ Verifica in **F1.5**: GATE intertemporale (data di instaurazione), competenza per valore/materia/territorio, forma dell'atto.

## Normativa di riferimento (ancore estratte dal modello)
- d.m. 55/2014 (art. 2, comma 2: rimborso spese forfettarie del 15%; art. 4: parametri generali e compenso per fasi; testo in vigore dal 23/10/2022)
- art. 13 l. 247/2012 (compenso pattuito per iscritto; parametri in mancanza di determinazione scritta)
- art. 9 d.l. 1/2012 (tariffe delle professioni regolamentate abrogate)
- art. 15 d.P.R. 633/1972 (anticipazioni in nome e per conto escluse dalla base imponibile)

Dipendenze di freschezza (changelog): **cartabia_processo_civile, parametri_forensi** — cfr. `wiki-studio/normativa/changelog-riforme.md`.
La freschezza del modello e' derivata da queste voci (vedi `scripts/freshness.py --modelli`).

## Note e trappole post-Cartabia
- **GATE intertemporale**: per i giudizi instaurati **prima del 28/02/2023** vale il regime previgente (es. 702-bis). L'inquadramento definitivo lo fa **F1.5**.

## Giurisprudenza
⏳ **Da popolare con giurisprudenza VERIFICATA** (One Legale on-demand in fase di redazione, oppure Sentinella).
Regola anti-allucinazione: **nessuna massima non verificata** entra in questa sezione.

## Testo del modello (fac-simile — Formulario del processo civile (ed. febbraio 2026))
```
6.	Parcella
(artt. 2 e 4 d.m. 55/2014; art. 13 l. 247/2012) 
PARCELLA 
Ex d.m. 55/2014

Causa promossa da .................... contro ....................
Ufficio giudiziario: .................... R.G. n. ............ · Valore della causa: € .................... (scaglione da € ............ a € ............; oppure: valore indeterminabile) · Tabella n. ...... allegata al d.m. 55/2014

Compenso: pattuito per iscritto il .................... (art. 13, commi 2 e 3, l. 247/2012), come segue: ....................
(oppure, in mancanza di determinazione scritta: liquidato secondo i parametri del d.m. 55/2014, art. 13, comma 6, l. 247/2012)

	Compenso
	professionale
	(per fasi: art. 4, comma 5, d.m. 55/2014)
1. FASE DI STUDIO DELLA CONTROVERSIA	.........
(esame e studio degli atti, consultazione con il cliente, ricerca dei documenti, relazione o parere)

2. FASE INTRODUTTIVA DEL GIUDIZIO	.........
(atto introduttivo o di costituzione, notificazioni, iscrizione a ruolo, formazione del fascicolo)

3. FASE ISTRUTTORIA	.........
(richieste di prova, memorie, interrogatorio formale, prove testimoniali, giuramento, assistenza alle udienze istruttorie; si liquida quando effettivamente svolta)

4. FASE DECISIONALE	.........
(precisazione delle conclusioni, memorie conclusionali e repliche, discussione orale, nota spese, esame e registrazione o pubblicazione della sentenza, ritiro del fascicolo)
(eventuale) Conciliazione giudiziale o transazione: compenso della fase decisionale aumentato di un quarto (art. 4, comma 6, d.m. 55/2014)	.........

5. PROCEDIMENTO ESECUTIVO (tabella n. ......)
Fase di studio e introduttiva (disamina del titolo esecutivo, notificazione con il precetto, pignoramento, iscrizioni e trascrizioni)	.........
Fase istruttoria e di trattazione (assistenza alle udienze e agli atti esecutivi)	.........

Aumenti o diminuzioni sui valori medi (art. 4, commi 1-4, d.m. 55/2014): ........% per ....................	.........
Totale compenso	.........
Rimborso spese forfettarie (15% del compenso totale: art. 2, comma 2, d.m. 55/2014)	.........
Contributo integrativo Cassa forense (4%)
(su compenso e rimborso spese forfettarie)	.........
IVA (22%)
(su compenso, rimborso spese forfettarie e contributo integrativo)	€ ..........
Spese documentate anticipate in nome e per conto del cliente (contributo unificato, notificazioni, ecc.: fuori dalla base imponibile IVA, art. 15, primo comma, n. 3, d.P.R. 633/1972)	€ ..........
.......................................................................................................................................
TOTALE GENERALE	€ ..........

Avv. ............................
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
- 2026-11-01 — parcella rifatta sui compensi per fasi: tolta l'impostazione su «diritti e onorari» e le voci a prestazione della tariffa (tariffe delle professioni regolamentate abrogate dall'art. 9, co. 1, D.L. 1/2012); fasi dell'art. 4, co. 5, d.m. 55/2014 (lett. a-d per il giudizio, e-f per l'esecuzione), aumenti e diminuzioni dell'art. 4, co. 1-4, conciliazione o transazione dell'art. 4, co. 6, rimborso spese forfettarie del 15% dell'art. 2, co. 2 (testo in vigore dal 23/10/2022); compenso pattuito per iscritto o, in mancanza, parametri (art. 13, co. 2, 3 e 6, l. 247/2012); spese anticipate fuori dalla base imponibile IVA (art. 15, primo comma, n. 3, d.P.R. 633/1972); tolta la «formula esecutiva» fra le voci dell'esecuzione. Testi letti con norma.py alla versione vigente.
