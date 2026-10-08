---
{
  "id": "039",
  "numero": 39,
  "sub": null,
  "titolo": "Successione nel processo",
  "tipo_atto": "atto",
  "forma_introduttiva": "atto",
  "rito": "ordinario di cognizione",
  "fase": "cognizione di primo grado",
  "materia": "cognizione ordinaria",
  "competenza_orientativa": "Tribunale ordinario, monocratico",
  "norme_chiave": [
    "art. 110 c.p.c.",
    "art. 581 c.c."
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
    "atto",
    "cognizione",
    "processo",
    "successione"
  ]
}
---

# 39 · Successione nel processo

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
- art. 110 c.p.c.
- art. 581 c.c.

Dipendenze di freschezza (changelog): **cartabia_processo_civile, correttivo_cartabia** — cfr. `wiki-studio/normativa/changelog-riforme.md`.
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
39.	Successione nel processo
(artt. 110 e segg. c.p.c.)
Al tribunale ordinario
di ................................
COMPARSA DI COSTITUZIONE VOLONTARIA
(art. 110 c.p.c.)
per ...................., nato il ..................... residente in .............................. c.f. ................................. in proprio e quale rapp.te legale dei figli minori ............................ rapp.ti e difesi dall’avv. ............................ c.f. .................................per procura nel suo studio legale in ........................., p.e.c. ..........
CONTRO
............... avv. ..................
Udienza................; g.i. dott. ....................; r.g. ......................

Il sottoscritto avvocato, nella qualità spiegata, si costituisce, a norma degli artt. 110, 111, 299 e 302 c.p.c., per ...................., vedova di ...................., deceduto, e per i figli minori ...................., eredi ex art. 581 c.c., per un terzo il coniuge e per due terzi i figli.
IN FATTO E DIRITTO
Impugna ancora l’atto di citazione notificato il .................... da .................... a.................... si riporta alla comparsa di costituzione e di risposta con domanda riconvenzionale, depositata in cancelleria il ...................., ed ai motivi ivi riportati; conclude perché il sig. giudice voglia così accogliere le seguenti
CONCLUSIONI:
A – rigettare la domanda dell’attrice perché infondata in fatto ed in diritto;
B – accogliere la domanda riconvenzionale e condannare ........................ al pagamento, in favore degli eredi ...................., delle somme dovute ed accertate con interessi e svalutazione monetaria;
C – condannare ......................................., al risarcimento dei danni, in favore degli istanti, così come determinati, a titolo di penalità, in € ...................., con interessi e svalutazione monetaria;
D – condannare ...................., al pagamento delle spese e compensi di causa, registrazione ed imposte.

Luogo e data ....................	Avv. ............
```

## Aggiornamenti
- 2026-07-04 — importato nel catalogo (testo 2026-02); normativa agganciata al changelog verificato; giurisprudenza da popolare (on-demand/Sentinella).
