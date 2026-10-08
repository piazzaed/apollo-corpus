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
- d.m. 55/2014

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
(d.m. 55/2014) 
PARCELLA 
Ex d.m. 55/2014

Causa promossa da .................... contro ....................

	Compenso
	professionale
1. DISAMINA – FASE DI STUDIO
Mandato	.........
Esame docum.	.........

2. INTRODUZIONE DEL GIUDIZIO
Citazione o ricorso	.........
Form. Fascicolo	.........
Contributo unificato	.........

3. FASE ISTRUTTORIA
Memorie difensive	.........
Interrogatorio formale	.........
Prove testimoniali	.........
Giuramento	.........

4. FASE DECISORIA
Part. udienze	.........
Precisazione delle conclusioni	.........
Memorie illustrative	.........
Discussione orale	.........
Ritiro fascicolo	.........
Citazione testi	.........
Esame e registrazione sentenza	.........

5. FASE ESECUTIVA 
Precetto	.........
Form. esecut.	.........
Pignoramento	.........
Iscrizioni e trascrizioni	.........
Totale onorari	.........
CNA (4%)
(su diritti e onorari)	.........
IVA (22%)
(su diritti e onorari + CNA)	€ ..........
Spese vive
(esenti da IVA e CNA)	€ ..........
.......................................................................................................................................
TOTALE GENERALE	€ ..........

Avv. ............................
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
