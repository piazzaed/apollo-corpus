# Catalogo modelli d'atto — strategia e manutenzione (v0.6)
<!-- tag: tipo_atto=*, rito=*, fase=*, materia=*, foro=*, ambito=manutenzione -->

## Idea in una riga
La selezione del modello d'atto passa da **"cerca sul web ogni volta"** a **"catalogo locale prima"**:
206 formule del processo civile diventano la **prima scelta** (veloce, offline, funziona **anche senza One
Legale**); il web e One Legale restano **fallback/arricchimento on-demand**, fuori dal percorso caldo.

## Come funziona la selezione (F1 del collegio-redazione)
1. **Catalogo locale** (`catalogo.json`) → match per materia/tipo/keywords/norme → proponi 1-3 schede.
2. **Gate di freschezza** (`scripts/freshness.py --modelli`): FRESCO → usa il *Testo del modello* come scaffold;
   SCADUTO/SOSPETTO → arricchisci on-demand prima di usarlo.
3. **Adatta** al foro reale + al `changelog-riforme.md` (il fac-simile non è fonte di diritto; rito/competenza li
   decide **F1.5**).
4. **Fallback web/One Legale** solo se il locale manca o è scaduto (`references/ricerca-modello-web.md`).
Dettaglio operativo: `skills/collegio-redazione/references/selezione-modello-locale.md`.

## Perché la freschezza è quasi gratis
Ogni modello dichiara le voci del changelog da cui dipende (`changelog_deps`, es. `cartabia_processo_civile`,
`correttivo_cartabia`). La freschezza del modello è **derivata** da quelle voci: se una riforma si muove, i
modelli che vi dipendono risultano automaticamente "da rivedere". Nessuna rete di verifica separata.

## Aggiornamento nel tempo (Sentinella + scheduled task)
- La **Sentinella normativa** (tell-only) fa, dopo il pass NORME, un **pass MODELLI**
  (`skills/sentinella-normativa/references/modelli-pass.md`): elenca i modelli scaduti e **propone** le
  correzioni; non riscrive nulla senza l'avvocato.
- **Scheduled task giornaliero/settimanale**: lancia la Sentinella (norme + modelli). In cloud (senza filesystem
  locale) vale come **solo-notifica** "è ora di lanciare la Sentinella"; l'esecuzione che tocca i file resta
  locale/on-demand (vedi `skills/sentinella-normativa/references/runbook.md`).
- **Giurisprudenza**: NON pre-caricata per tutti i 206 (violerebbe il pavimento anti-allucinazione). La sezione
  «Giurisprudenza» di ogni scheda è `da_popolare` e si riempie **on-demand in redazione** (verifica-fonti / One
  Legale) sulla *specifica* sub-questione dell'atto, dove la massima è davvero pertinente e verificabile.

## Con e senza One Legale
- **Senza** One Legale: catalogo locale + fonti pubbliche → piena funzione.
- **Con** One Legale: strato di arricchimento opzionale (formule commentate, giurisprudenza) attivabile per
  sessione (`config-fonti.json` → `one_legale.sessione=onelegale`). Mai sul percorso caldo di ogni atto.

## Come aggiungere / aggiornare un modello
1. Metti il nuovo modello in `civile/<id>-<slug>.md` (frontmatter come gli altri: `changelog_deps`, `volatilita`,
   `verificato_il`, `prossima_verifica`, `stato`).
2. Aggiungi la voce corrispondente in `catalogo.json` (indice) e in `modelli.meta.json` (freschezza).
3. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/freshness.py --modelli` per verificare che risulti FRESCO.
(La rigenerazione batch delle schede è documentata nel changelog del plugin.)

## Mappa dei file
```
wiki-studio/modelli/
  catalogo.json            indice di selezione (F1)
  modelli.meta.json        sidecar freschezza (freshness.py --modelli)
  INDEX-MODELLI.md         indice umano per materia
  STRATEGIA-CATALOGO.md    questo file
  README.md                sintesi operativa
  civile/<id>-<slug>.md    206 schede-modello
skills/collegio-redazione/references/selezione-modello-locale.md   protocollo F1 local-first
skills/sentinella-normativa/references/modelli-pass.md             pass freschezza modelli
scripts/freshness.py --modelli                                     verdetto freschezza modelli
```
