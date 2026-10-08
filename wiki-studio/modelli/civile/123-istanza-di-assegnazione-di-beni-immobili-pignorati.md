---
{
  "id": "123",
  "numero": 123,
  "sub": null,
  "titolo": "Istanza di assegnazione di beni immobili pignorati",
  "tipo_atto": "istanza",
  "forma_introduttiva": "istanza",
  "rito": "esecuzione",
  "fase": "esecuzione forzata",
  "materia": "esecuzione (titolo, precetto, pignoramento, opposizioni)",
  "competenza_orientativa": "Tribunale ordinario, monocratico",
  "norme_chiave": [
    "art. 589 c.p.c."
  ],
  "changelog_deps": [
    "cartabia_processo_civile",
    "correttivo_cartabia"
  ],
  "volatilita": "media",
  "fonte": "Catalogo dei modelli d'atto (testi di febbraio 2026)",
  "data_formulario": "2026-02",
  "verificato_il": "2026-07-04",
  "prossima_verifica": "2027-07-04",
  "stato": "congelato",
  "giurisprudenza_stato": "da_popolare",
  "selezione_keywords": [
    "assegnazione",
    "beni",
    "esecuzione",
    "immobili",
    "istanza",
    "pignorati"
  ]
}
---

# 123 · Istanza di assegnazione di beni immobili pignorati

> Scheda-modello **local-first**. Scaffold verificato per la **selezione** in F1 del `collegio-redazione`.
> L'inquadramento autorevole (tipo · rito · competenza · struttura) resta di **F1.5** (albero `struttura-atti.md` + round di verifica: Livello 0 + due agenti). Un fac-simile **non e' fonte di diritto**.

## Quando si usa
- Materia: **esecuzione (titolo, precetto, pignoramento, opposizioni)** · Fase: **esecuzione forzata**
- Forma introduttiva tipica: **istanza** · Rito: **esecuzione**

## Inquadramento (orientativo — decide F1.5)
- Competenza orientativa: **Tribunale ordinario, monocratico**
- Rito: **esecuzione**
- ⚠️ Verifica in **F1.5**: GATE intertemporale (data di instaurazione), competenza per valore/materia/territorio, forma dell'atto.

## Normativa di riferimento (ancore estratte dal modello)
- art. 589 c.p.c.

Dipendenze di freschezza (changelog): **cartabia_processo_civile, correttivo_cartabia** — cfr. `wiki-studio/normativa/changelog-riforme.md`.
La freschezza del modello e' derivata da queste voci (vedi `scripts/freshness.py --modelli`).

## Note e trappole post-Cartabia
- Titolo esecutivo, notifica del precetto e termini ex art. 480 c.p.c.; per il monitorio verificare prova scritta (633/634) e termini di opposizione (641/650).
- **GATE intertemporale**: per i giudizi instaurati **prima del 28/02/2023** vale il regime previgente (es. 702-bis). L'inquadramento definitivo lo fa **F1.5**.

## Giurisprudenza
⏳ **Da popolare con giurisprudenza VERIFICATA** (One Legale on-demand in fase di redazione, oppure Sentinella).
Regola anti-allucinazione: **nessuna massima non verificata** entra in questa sezione.

## Testo del modello (fac-simile — Formulario del processo civile (ed. febbraio 2026))
```
123.	Istanza di assegnazione di beni immobili pignorati
(art. 589 c.p.c.)
Al tribunale ordinario civile di ....................
	in composizione monocratica
ISTANZA DI ASSEGNAZIONE
(ART. 589 C.P.C.)

Ill.mo Sig. giudice dell’esecuzione,
in funzione di giudice unico nell’espropriazione immobiliare
in danno di .................... distinta al n. .................... R.E.

La ditta ............................. & C. s.r.l. in persona del suo amministratore unico ......................... con sede in .................................. via ....................., n. ........ c.f. ............. ed elettivamente domiciliato presso lo studio dell’avv. .................. c.f. ............., in ..................., p.e.c. ............... che la rappresenta e difende come da procura a margine alla domanda di intervento 
PREMESSO
– che nel processo di espropriazione immobiliare n. ....................... iniziato con pignoramento eseguito da .......................... nei confronti del sig. ................. gli incanti disposti per il ........................... e successivamente per il ............................. sono andati deserti per mancanza di valide offerte;
– che l’istante è titolare di un credito di € ...................., in virtù di domanda di intervento del ....................
CHIEDE
che venga disposta l’assegnazione in suo favore dell’immobile sottoposto ad esecuzione ai sensi dell’art. 589 c.p.c.
Con osservanza.

Luogo e data ....................	L’amministratore unico ...................

depositata in cancelleria oggi ....................

Il cancelliere ....................................
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
