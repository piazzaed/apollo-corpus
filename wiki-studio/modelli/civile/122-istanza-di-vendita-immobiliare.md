---
{
  "id": "122",
  "numero": 122,
  "sub": null,
  "titolo": "Istanza di vendita immobiliare",
  "tipo_atto": "istanza",
  "forma_introduttiva": "istanza",
  "rito": "esecuzione",
  "fase": "esecuzione forzata",
  "materia": "esecuzione (titolo, precetto, pignoramento, opposizioni)",
  "competenza_orientativa": "Tribunale ordinario, monocratico",
  "norme_chiave": [
    "art. 567 c.p.c.",
    "art. 569 c.p.c.",
    "d.P.R. 115/2002"
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
    "esecuzione",
    "immobiliare",
    "istanza",
    "vendita"
  ]
}
---

# 122 · Istanza di vendita immobiliare

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
- art. 567 c.p.c.
- art. 569 c.p.c.
- d.P.R. 115/2002

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
122.	Istanza di vendita immobiliare
(art. 567 c.p.c.)
Al sig. giudice dell’esecuzione
	in composizione monocratica ..........
	del tribunale ordinario di .................

Oggetto: proc. esecutiva n. ........../.......... contro soc. .................. 
ISTANZA DI VENDITA DI BENI PIGNORATI
L’avv. .................... c.f. ..................., procuratore e difensore della soc. .................... c.f. ................., come da mandato a margine dell’atto di precetto, indirizzo di p.e.c. comunicato al proprio ordine ...........
CHIEDE
a norma dell’art. 567 del codice di procedura civile che sia fissata l’udienza di comparizione delle parti per la fissazione della vendita dei beni pignorati in data ........... in danno della società .................... con sede in ...................., via....................
Si dichiara che il contributo unificato è di euro ......... ex art. 13, comma 2, d.P.R. 115/2002.

Data ....................	Avv. ....................
Tribunale ordinario di ....................

Il giudice dell’esecuzione, in funzione di giudice unico;
letta l’istanza che precede;
visto l’art. 569 c.p.c.;
FISSA
per l’audizione delle parti l’udienza del ........................................... 
Si comunichi

Data ...................	Il giudice dell’esecuzione ...........
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
