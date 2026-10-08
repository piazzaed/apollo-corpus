# Modelli d'atto — CATALOGO LOCAL-FIRST (processo civile)
<!-- tag: tipo_atto=*, rito=*, fase=*, materia=*, foro=*, ambito=manutenzione -->

Da v0.6 questa cartella **NON** è più una drop-zone vuota: è il **catalogo locale di prima scelta**
dei modelli d'atto, letto in **F1** del `collegio-redazione` **prima** della ricerca web/One Legale.

## Cosa c'è qui
- `catalogo.json` — **indice di selezione** (id, titolo, tipo, rito, materia, competenza orientativa, norme_chiave, keywords, file). È il file che F1 scorre per proporre i candidati.
- `modelli.meta.json` — **sidecar freschezza** (per ogni modello: `changelog_deps`, `verificato_il`, `prossima_verifica`, `volatilita`, `stato`). Letto da `scripts/freshness.py --modelli`.
- `civile/<id>-<slug>.md` — **una scheda per modello** (206): frontmatter + *Quando si usa* + *Inquadramento* + *Normativa* (agganciata al changelog) + *Trappole post-Cartabia* + *Giurisprudenza* (da popolare) + *Testo del modello* (fac-simile) + *Aggiornamenti*.
- `INDEX-MODELLI.md` — indice umano per materia.
- `STRATEGIA-CATALOGO.md` — come funziona, come si aggiorna, come si aggiunge un modello.

## Come si usa (in una riga)
F1 cerca nel `catalogo.json` → propone 1-3 schede → gate freschezza (`freshness.py --modelli`) → se FRESCO usa il *Testo del modello* come scaffold e adatta a foro+changelog; se manca/scaduto → web/One Legale on-demand.

## Fonte e aggiornamento
I 206 modelli sono testi propri, scritti in Markdown. La freschezza è **derivata** dalle
voci del `changelog-riforme` (nessuna rete a sé): quando una riforma si muove, la **Sentinella** segnala quali
modelli rivedere (`references/modelli-pass.md`, tell-only). La giurisprudenza si popola **on-demand** in redazione.

