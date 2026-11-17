**English** · [简体中文](README.zh-CN.md)

# swap-ledger

**Rebrand a video without leftovers.** swap-ledger is an agent skill for remaking a reference video, motion template or ad for a different brand, product or client. It turns the rebrand into a ledger you can check: every appearance of the old identity gets a decision, every new line is timed and fact-checked, and the finished render is swept for anything the old brand left behind.

## Why

Rebranded videos rarely fail on the headline. They fail on the end-card URL nobody re-typed, the burned-in caption that still says the old name, the sonic logo, one background colour that is almost the old red, or a "#1 in 2025" badge that kept the claim while the brand changed. swap-ledger makes each of those an explicit row that has to be closed before the video counts as done.

## Features

- **Ten identity channels**: text, logo, product, UI, voice, captions, palette, sound, people and metadata, each walked separately.
- **Four decisions**: SWAP, DROP, NEUTRAL or ASK for every appearance. Open questions block the gate.
- **Rights column** for borrowed footage, music and stock. Unknown or to-be-replaced material that is still in the cut blocks the gate.
- **Fit check**: reading and speaking time for each new line against its hold time (OK / TIGHT / OVER), with English and Chinese rates you can tune.
- **Claim check**: numbers and superlatives in new copy must come from a cited entry in your own facts sheet.
- **Residue sweep** over captions, transcripts, frame-text dumps, composition source and publishing metadata. It catches look-alike spellings (`N0rth-W1nd`), full-width text, names split across lines, and colours within ΔE of the old palette.
- **One verdict**: CLEAN / RESIDUE / OPEN. A gate with no render evidence never reads CLEAN.
- Standard-library Python with 12 tests, so it runs anywhere.

## Install

The skill is the folder. Copy or clone it where your agent looks for skills:

| Agent | Location |
|---|---|
| Claude Code | `~/.claude/skills/swap-ledger/` or `.claude/skills/swap-ledger/` in a project |
| Codex | `~/.codex/skills/swap-ledger/` (or reference `SKILL.md` from `AGENTS.md`) |
| Cursor | `.cursor/skills/swap-ledger/`, or point a project rule at `SKILL.md` |
| Other agents | Put the folder anywhere and ask the agent to read `SKILL.md` |

```bash
git clone https://github.com/fangdididi/swap-ledger.git ~/.claude/skills/swap-ledger
```

Then ask, for example: *"Use swap-ledger to remake this template for our brand."*

## Usage

```bash
python3 scripts/swapledger.py new rebrand/                      # starter swap.json + ledger.csv
python3 scripts/swapledger.py fit    rebrand/swap.json rebrand/ledger.csv
python3 scripts/swapledger.py claims rebrand/swap.json rebrand/ledger.csv
python3 scripts/swapledger.py sweep  rebrand/swap.json captions.srt frames.txt comp.css description.txt
python3 scripts/swapledger.py gate   rebrand/swap.json rebrand/ledger.csv captions.srt frames.txt comp.css description.txt
```

Exit code 0 means the check passed and 1 means it found problems.

## Example

`examples/oat-remake/` remakes a bakery ad (Brightloaf) for an oat-bar brand (Oatfield):

```
$ python3 scripts/swapledger.py gate examples/oat-remake/swap.json examples/oat-remake/ledger.csv \
    examples/oat-remake/render-captions.srt examples/oat-remake/frame-text.txt \
    examples/oat-remake/composition.css examples/oat-remake/description.txt
RESIDUE examples/oat-remake/composition.css:3: colour #e5592f is within dE 0.7 of old brand #e4572e
RESIDUE examples/oat-remake/description.txt:3: 'Brightloaf' split across lines 2-3
VERDICT RESIDUE
```

The "Voted #1 bakery 2025" badge was dropped instead of rewritten, because Oatfield has no fact to support it. The new voiceover cites the nutrition label. The licensed jingle was swapped because its licence doesn't transfer. Two leftovers still had to be caught: a near-identical badge colour and a thank-you to the old brand that was split across two lines.

## File structure

```
swap-ledger/
├── SKILL.md                 # skill instructions (English)
├── SKILL.zh-CN.md           # skill instructions (Chinese)
├── README.md
├── README.zh-CN.md
├── LICENSE
├── scripts/
│   └── swapledger.py        # new / fit / claims / sweep / gate
├── examples/
│   └── oat-remake/          # swap card, ledger and render evidence
└── tests/
    └── test_swapledger.py   # python3 -m unittest discover -s tests
```

## License

MIT © fangdididi
