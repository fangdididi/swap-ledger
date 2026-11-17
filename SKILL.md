---
name: swap-ledger
description: Rebrand a reference or template video into your own brand without leftovers. Walk the source through ten identity channels (on-screen text, logo, product, UI, voice, captions, palette, sound, people, metadata), decide SWAP / DROP / NEUTRAL / ASK for every appearance, check that each new line fits its screen time and that every number or superlative is backed by your own facts sheet, then sweep the rendered evidence for old-brand residue (names, look-alike spellings, split words, near-identical colours). Use when remaking, recreating, localizing or white-labelling a video, motion template or ad for a different brand, client or product.
---

# swap-ledger

## What this is

When a video is rebuilt for a new brand — a template bought from a marketplace, a competitor ad used as a reference, last year's launch film reused for a new product, one master cut white-labelled for ten clients — the work usually fails in the same three places:

1. **Leftovers.** The headline is changed, but the old name survives in the end-card URL, a burned-in caption, a UI screenshot, the file name, the sonic logo or one background colour.
2. **Borrowed claims.** "Voted #1 bakery 2025" turns into "Voted #1 snack bar 2025": a line kept from the source with one word changed, which is now a claim nobody can support.
3. **Lines that no longer fit.** The new copy is longer than the old copy, but the hold time is the same, so viewers can't finish reading it or the voiceover runs into the next shot.

swap-ledger turns the rebrand into a ledger you can check. Every appearance of the old identity gets a row, a decision and, when needed, a replacement. Then the finished render is checked against the ledger rather than against someone's memory.

It is tool-agnostic. It works with motion-graphics code (HTML/CSS, Remotion, HyperFrames-style compositions), timeline editors, After Effects projects or a plain shot list.

## When to use it

- Recreating a reference video or a motion template for your brand, product or client.
- Reusing your own older film for a renamed product, new logo or new market.
- White-labelling one master video for several resellers or clients.
- Localizing a video where product names, prices or claims change per market.
- Reviewing someone else's rebrand before it ships.

Not for: deciding whether you may use a reference at all (that is a rights question for the owner or a lawyer), or for judging the creative quality of the cut.

## The ten channels

Walk the source once per channel. Doing this one channel at a time catches what a single "watch it through" pass misses.

| Channel | Look for |
|---|---|
| `text` | headlines, lower thirds, badges, stickers, price tags, legal lines |
| `logo` | marks, watermarks, favicons in screen captures, embossing on objects |
| `product` | packaging, the hero object, product shots, mascots |
| `ui` | app or website screenshots, mock dashboards, browser tabs, notifications |
| `voice` | voiceover, dialogue, on-camera speech that names the brand or makes a claim |
| `captions` | burned-in and sidecar subtitles (they often lag behind a VO change) |
| `palette` | brand colours in backgrounds, shapes, gradients, light leaks |
| `sound` | jingles, sonic logos, licensed music, recognizable sound effects |
| `people` | spokespeople, hosts, recognizable faces and hands that belong to the old brand |
| `meta` | title, description, hashtags, thumbnail, end-card URL, file names, chapter names |

## Steps

### 1. Fill the swap card

Run `python3 scripts/swapledger.py new rebrand/` to get `swap.json` and `ledger.csv`, then fill `swap.json`:

- `from_brand`: every name, short name, handle, domain, product name, person, colour (hex) and sound that identifies the source.
- `to_brand`: the same for the new brand. Only use material the owner gives you or that is in their workspace; never invent a logo, a slogan or a handle.
- `facts`: each statement the new brand can stand behind, with an `id` and a `source` (a label, page, contract, spec sheet). This is the only place numbers and superlatives may come from.
- `language` and optionally `rates`: reading speed (units per second) for on-screen text and speaking speed for voice. Defaults are 2.5 words/s read and 2.6 words/s spoken for English, 5 and 4 characters/s for Chinese. Lower them for children, older viewers or dense backgrounds.

### 2. Walk the source and write the ledger

For every appearance, add a row: `id, shot, start, end, channel, what, action, replacement, fact, rights, note`.

Actions:

- **SWAP**: replace it. Write the replacement concretely ("Oatfield mark with the same bounce", not "new logo").
- **DROP**: remove it, and close the gap (re-time, extend the neighbour, or use a neutral plate).
- **NEUTRAL**: keep it, because it carries no identity (a generic hand, a sky, a stock keyboard sound).
- **ASK**: only the owner can decide. The gate stays open until this is answered.

`rights` applies to borrowed material such as footage, music, fonts and stock: `owned`, `licensed`, `generated`, `replace` or `unknown`. Anything `unknown` or `replace` that is not dropped keeps the gate open. Leave it empty for things you make yourself (text, shapes).

After each channel is walked, set it to `done` (or `n/a`) in `channels_checked`.

### 3. Check fit and claims before you render

```
python3 scripts/swapledger.py fit rebrand/swap.json rebrand/ledger.csv
python3 scripts/swapledger.py claims rebrand/swap.json rebrand/ledger.csv
```

- `fit` times every swapped text, caption, UI and voice line: `OK`, `TIGHT` (within 20%) or `OVER`. Fix OVER by cutting words first. Extend the hold only if the cut can absorb it, and then re-time the music.
- `claims` flags any number not found in a cited fact, any superlative ("best", "#1", "the first", "fastest", "最", "第一", "领先"…) that the cited fact doesn't say, and any fact id that doesn't exist. Don't adjust a borrowed claim to make it pass. Drop it or get a real fact.

### 4. Render, collect evidence, sweep

Collect text evidence from the actual render, not from the project:

- the subtitle file and a transcript of the final audio,
- an OCR or hand-typed dump of sampled frames (every cut plus about one frame per second for text-heavy parts),
- composition source files (CSS, JSON, project XML) for colours and leftover strings,
- the publishing metadata (title, description, tags, file name).

```
python3 scripts/swapledger.py sweep rebrand/swap.json captions.srt frames.txt comp.css description.txt
```

The sweep folds case, full-width characters, accents and look-alike characters (0/o, 1/l/i, 3/e, 5/s, @/a) and removes separators. That way `N0rth-Wind`, `northwind` and a name broken across two lines are all caught. It also flags any hex colour within ΔE 8 of an old brand colour that isn't also close to a new one. Things the sweep can't hear or see (a sonic logo, a face, a product silhouette) have to be closed in the ledger by a human watch-through.

### 5. Gate

```
python3 scripts/swapledger.py gate rebrand/swap.json rebrand/ledger.csv captions.srt frames.txt comp.css description.txt
```

- **CLEAN**: every channel is walked, nothing is ASK, every line fits, every claim is backed, and the sweep found nothing.
- **RESIDUE**: old identity or an unbacked claim is still in the deliverable. Fix it and re-render.
- **OPEN**: decisions, timing or evidence are missing. A gate with no render evidence can never be CLEAN.

Hand over the verdict, the ledger and the list of items that were checked only by eye.

## Example

A bakery ad (Brightloaf) is remade for an oat-bar brand (Oatfield). See `examples/oat-remake/`:

- `A5` "Voted #1 bakery 2025" → **DROP**. Oatfield has no matching fact, so the badge is not rewritten.
- `A4` VO "Baked fresh by Pia every dawn" → "Nine grams of protein in every Field Bar", citing fact `F1` (from the nutrition label).
- `A7` the licensed jingle and oven-ding sonic logo → Oatfield's own sting, because a licence for the old brand doesn't transfer.
- `fit` shows three TIGHT lines but none OVER. `claims` reports everything backed.
- `sweep` still finds two leftovers: a badge colour `#e5592f` that is ΔE 0.7 from Brightloaf's red, and a description that thanks "the Bright / loaf team" across a line break. Verdict: **RESIDUE**.

## Tips

- Walk `meta` and `captions` last and slowly. Most leftovers are found there.
- A swapped logo should keep the source's *motion role* (entrance, size, hold), not its shape. Check the clear space around the new mark.
- Longer replacement copy often means a smaller font. Re-check legibility on a phone-size preview, not only the timing.
- Keep the original sound only if its licence covers the new use. Otherwise the `sound` row is SWAP with `rights` set.
- Don't let a generated shot re-create a real person from the old brand. Swap the role, not the face.
- For white-label batches, keep one ledger per client. The sweep for client B should include client A's names as `from_brand` too.
