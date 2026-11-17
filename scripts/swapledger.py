#!/usr/bin/env python3
"""swapledger.py - brand swap ledger, fit/claim checks and residue sweep for remade videos.

Commands:
  new DIR                       write a starter swap.json + ledger.csv into DIR
  fit SWAP LEDGER               does each replacement line fit the time it is on screen / spoken?
  claims SWAP LEDGER            are numbers, superlatives and awards in replacements backed by the facts sheet?
  sweep SWAP FILE [FILE ...]    scan transcripts, frame-text dumps, captions, source and metadata for old-brand residue
  gate SWAP LEDGER [FILE ...]   run everything and print CLEAN / RESIDUE / OPEN

Exit code: 0 when the check passes, 1 when it finds problems, 2 on bad input.
Standard library only.
"""
import csv, json, math, os, re, sys, unicodedata

CHANNELS = ["text", "logo", "product", "ui", "voice", "captions", "palette", "sound", "people", "meta"]
ACTIONS = {"SWAP", "DROP", "NEUTRAL", "ASK"}
RIGHTS = {"owned", "licensed", "generated", "replace", "unknown", ""}
TIMED_CHANNELS = {"text": "read", "captions": "read", "ui": "read", "voice": "speak"}
DEFAULT_RATES = {"en": {"read": 2.5, "speak": 2.6}, "zh": {"read": 5.0, "speak": 4.0}}
LEET = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "|": "l"})
SUPERLATIVES = [
    r"\bbest\b", r"#1\b", r"\bno\.? ?1\b", r"\bnumber one\b", r"\bfastest\b", r"\bcheapest\b",
    r"\bleading\b", r"\bworld'?s\b", r"\bthe first\b", r"\bthe only\b", r"\baward", r"\bguarantee", r"\bunlimited\b",
    r"\bclinically\b", r"\bproven\b", r"\btrusted by\b",
    "第一", "最", "领先", "唯一", "首个", "首款", "获奖", "保证", "无限",
]
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")

TEMPLATE_SWAP = {
    "language": "en",
    "rates": DEFAULT_RATES["en"],
    "from_brand": {
        "names": ["Northwind", "Northwind Cloud"],
        "handles": ["@northwindhq"],
        "domains": ["northwind.example"],
        "products": ["Gale"],
        "people": ["Jordan the Northwind host"],
        "colors": ["#1f6feb", "#f2cc60"],
        "sounds": ["three-note Northwind chime"],
    },
    "to_brand": {
        "names": ["Tidepool"],
        "handles": ["@tidepoolapp"],
        "domains": ["tidepool.example"],
        "products": ["Drift"],
        "colors": ["#0f766e", "#fafaf9"],
    },
    "facts": [
        {"id": "F1", "text": "Drift syncs notes across 3 devices on the free plan", "source": "pricing page, 2026-11"},
    ],
    "allow_tokens": [],
    "channels_checked": {c: "pending" for c in CHANNELS},
    "color_threshold": 8.0,
}
LEDGER_FIELDS = ["id", "shot", "start", "end", "channel", "what", "action", "replacement", "fact", "rights", "note"]
TEMPLATE_ROWS = [
    {"id": "A1", "shot": "1", "start": "0.0", "end": "2.0", "channel": "logo", "what": "Northwind mark top-left",
     "action": "SWAP", "replacement": "Tidepool mark, same corner, same entrance", "fact": "", "rights": "owned", "note": ""},
    {"id": "A2", "shot": "2", "start": "2.0", "end": "4.5", "channel": "text", "what": "Headline 'Northwind keeps you in sync'",
     "action": "SWAP", "replacement": "Your notes, on every device", "fact": "", "rights": "", "note": ""},
]


def die(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(2)


def load_swap(path):
    try:
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
    except (OSError, ValueError) as e:
        die(f"cannot read {path}: {e}")
    if "from_brand" not in s:
        die("swap card has no from_brand")
    return s


def load_ledger(path):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        die(f"cannot read {path}: {e}")
    for r in rows:
        for k in LEDGER_FIELDS:
            r[k] = (r.get(k) or "").strip()
    return rows


def norm(text):
    """Fold case, width, accents, look-alike digits and separators so 'N0rth-Wind' == 'northwind'."""
    t = unicodedata.normalize("NFKC", text).lower().translate(LEET)
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    t = t.replace("i", "l")  # i, l, 1 and | look alike on screen; fold them together
    return re.sub(r"[\W_]+", "", t)


def units(text, lang):
    if lang == "zh":
        han = len(re.findall(r"[\u4e00-\u9fff]", text))
        latin = len(re.findall(r"[A-Za-z0-9]+", text))
        return han + latin
    return len(re.findall(r"[A-Za-z0-9\u00c0-\u024f']+", text))


def rates_for(swap):
    lang = swap.get("language", "en")
    base = dict(DEFAULT_RATES.get(lang, DEFAULT_RATES["en"]))
    base.update(swap.get("rates") or {})
    return lang, base


def check_fit(swap, rows):
    lang, rates = rates_for(swap)
    problems, report = [], []
    for r in rows:
        mode = TIMED_CHANNELS.get(r["channel"])
        if r["action"] != "SWAP" or not mode or not r["replacement"]:
            continue
        try:
            dur = float(r["end"]) - float(r["start"])
        except ValueError:
            problems.append(f"{r['id']}: start/end missing, cannot time '{r['replacement']}'")
            continue
        if dur <= 0:
            problems.append(f"{r['id']}: end is not after start")
            continue
        n = units(r["replacement"], lang)
        need = n / rates[mode] + (0.3 if mode == "read" else 0.0)
        ratio = need / dur
        status = "OK" if ratio <= 1.0 else ("TIGHT" if ratio <= 1.2 else "OVER")
        report.append(f"{r['id']} {r['channel']:<8} {n:>3} units need {need:4.1f}s have {dur:4.1f}s  {status}")
        if status == "OVER":
            problems.append(f"{r['id']}: '{r['replacement']}' needs {need:.1f}s but is on for {dur:.1f}s - cut words or extend the hold")
    return problems, report


def fact_numbers(swap, ids):
    nums, texts = set(), []
    for f in swap.get("facts", []):
        if f.get("id") in ids:
            texts.append(f.get("text", ""))
            nums.update(NUM_RE.findall(f.get("text", "")))
    return nums, " ".join(texts).lower()


def check_claims(swap, rows):
    problems = []
    known = {f.get("id") for f in swap.get("facts", [])}
    for r in rows:
        if r["action"] != "SWAP" or not r["replacement"]:
            continue
        text = r["replacement"]
        ids = {x.strip() for x in re.split(r"[;, ]+", r["fact"]) if x.strip()}
        bad_ids = ids - known
        if bad_ids:
            problems.append(f"{r['id']}: cites unknown fact id(s) {sorted(bad_ids)}")
        nums, facttext = fact_numbers(swap, ids)
        for n in NUM_RE.findall(text):
            if n not in nums:
                problems.append(f"{r['id']}: number '{n}' in '{text}' is not in any cited fact")
        low = text.lower()
        for pat in SUPERLATIVES:
            m = re.search(pat, low)
            if m and m.group(0).strip("#") not in facttext:
                problems.append(f"{r['id']}: claim word '{m.group(0)}' in '{text}' has no cited fact that says it")
                break
    return problems


def from_tokens(swap):
    fb = swap["from_brand"]
    toks = []
    for key in ("names", "handles", "domains", "products", "people"):
        for v in fb.get(key, []) or []:
            if key == "people":
                v = v.split(" the ")[0]
            n = norm(v)
            if len(n) >= 3:
                toks.append((v, n))
    allow = {norm(a) for a in swap.get("allow_tokens", []) or []}
    to_norm = [norm(v) for k in ("names", "handles", "domains", "products") for v in (swap.get("to_brand", {}).get(k) or [])]
    return [(v, n) for v, n in toks if n not in allow and not any(n in t for t in to_norm)]


def hex_to_lab(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    x = (lin[0] * 0.4124 + lin[1] * 0.3576 + lin[2] * 0.1805) / 0.95047
    y = lin[0] * 0.2126 + lin[1] * 0.7152 + lin[2] * 0.0722
    z = (lin[0] * 0.0193 + lin[1] * 0.1192 + lin[2] * 0.9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(a, b):
    return math.dist(hex_to_lab(a), hex_to_lab(b))


HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def sweep(swap, files):
    toks = from_tokens(swap)
    old_cols = swap["from_brand"].get("colors", []) or []
    new_cols = swap.get("to_brand", {}).get("colors", []) or []
    thr = float(swap.get("color_threshold", 8.0))
    hits = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError as e:
            die(f"cannot read {path}: {e}")
        prev = ""
        for i, line in enumerate(lines, 1):
            nl, joined = norm(line), norm(prev + " " + line)
            for raw, n in toks:
                if n in nl:
                    hits.append(f"{path}:{i}: '{raw}' -> {line.strip()[:90]}")
                elif n in joined and n not in norm(prev):
                    hits.append(f"{path}:{i}: '{raw}' split across lines {i-1}-{i}")
            for hx in HEX_RE.findall(line):
                for oc in old_cols:
                    d = delta_e(hx, oc)
                    if d <= thr and not any(delta_e(hx, nc) <= thr for nc in new_cols):
                        hits.append(f"{path}:{i}: colour {hx} is within dE {d:.1f} of old brand {oc}")
                        break
            prev = line
    return hits


def ledger_open(swap, rows):
    probs = []
    seen_ids = set()
    for r in rows:
        if r["id"] in seen_ids:
            probs.append(f"duplicate row id {r['id']}")
        seen_ids.add(r["id"])
        if r["channel"] not in CHANNELS:
            probs.append(f"{r['id']}: unknown channel '{r['channel']}' (use one of {', '.join(CHANNELS)})")
        if r["action"] not in ACTIONS:
            probs.append(f"{r['id']}: action '{r['action']}' must be SWAP, DROP, NEUTRAL or ASK")
        elif r["action"] == "ASK":
            probs.append(f"{r['id']}: still ASK - '{r['what']}' needs the owner's answer")
        elif r["action"] == "SWAP" and not r["replacement"]:
            probs.append(f"{r['id']}: SWAP with no replacement")
        if r["rights"] not in RIGHTS:
            probs.append(f"{r['id']}: rights '{r['rights']}' not one of owned/licensed/generated/replace/unknown")
        elif r["rights"] in ("unknown", "replace") and r["action"] != "DROP":
            probs.append(f"{r['id']}: borrowed material with rights '{r['rights']}' is still in the cut")
    checked = swap.get("channels_checked", {})
    for c in CHANNELS:
        state = checked.get(c, "pending")
        if state not in ("done", "n/a"):
            probs.append(f"channel '{c}' not walked yet (channels_checked says '{state}')")
    return probs


def cmd_new(d):
    os.makedirs(d, exist_ok=True)
    sp, lp = os.path.join(d, "swap.json"), os.path.join(d, "ledger.csv")
    for p in (sp, lp):
        if os.path.exists(p):
            die(f"{p} exists; not overwriting")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE_SWAP, f, indent=2, ensure_ascii=False)
    with open(lp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(TEMPLATE_ROWS)
    print(f"wrote {sp} and {lp} - replace the example brand with yours")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) >= 2 else 2
    cmd, args = argv[1], argv[2:]
    if cmd == "new" and len(args) == 1:
        return cmd_new(args[0])
    if cmd == "fit" and len(args) == 2:
        probs, rep = check_fit(load_swap(args[0]), load_ledger(args[1]))
        print("\n".join(rep) or "no timed swaps")
        for p in probs:
            print("OVER  " + p)
        return 1 if probs else 0
    if cmd == "claims" and len(args) == 2:
        probs = check_claims(load_swap(args[0]), load_ledger(args[1]))
        for p in probs:
            print("CLAIM " + p)
        print("claims: " + ("all backed" if not probs else f"{len(probs)} unbacked"))
        return 1 if probs else 0
    if cmd == "sweep" and len(args) >= 2:
        hits = sweep(load_swap(args[0]), args[1:])
        for h in hits:
            print("RESIDUE " + h)
        print("sweep: " + ("clean" if not hits else f"{len(hits)} residue hit(s)"))
        return 1 if hits else 0
    if cmd == "gate" and len(args) >= 2:
        swap, rows = load_swap(args[0]), load_ledger(args[1])
        opened = ledger_open(swap, rows)
        fitp, _ = check_fit(swap, rows)
        claimp = check_claims(swap, rows)
        hits = sweep(swap, args[2:]) if args[2:] else []
        for tag, items in (("OPEN", opened), ("OVER", fitp), ("CLAIM", claimp), ("RESIDUE", hits)):
            for x in items:
                print(f"{tag:<8}{x}")
        if not args[2:]:
            print("note: no render evidence given - sweep skipped, gate cannot be CLEAN")
        if hits or claimp:
            verdict = "RESIDUE"
        elif opened or fitp or not args[2:]:
            verdict = "OPEN"
        else:
            verdict = "CLEAN"
        print("VERDICT " + verdict)
        return 0 if verdict == "CLEAN" else 1
    die("bad arguments; run with --help")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
