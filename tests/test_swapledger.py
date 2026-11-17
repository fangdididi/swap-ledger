import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import swapledger as sl  # noqa: E402

EX = os.path.join(HERE, "..", "examples", "oat-remake")
SCRIPT = os.path.join(HERE, "..", "scripts", "swapledger.py")


def row(**kw):
    base = {k: "" for k in sl.LEDGER_FIELDS}
    base.update(kw)
    return base


class T(unittest.TestCase):
    def setUp(self):
        self.swap = sl.load_swap(os.path.join(EX, "swap.json"))

    def test_norm_folds_lookalikes(self):
        self.assertEqual(sl.norm("Br1ght-L0AF"), sl.norm("brightloaf"))
        self.assertEqual(sl.norm("Ｂｒｉｇｈｔｌｏａｆ"), sl.norm("Brightloaf"))

    def test_fit_over(self):
        r = row(id="X", channel="text", action="SWAP", start="0", end="1", replacement="one two three four five six seven")
        probs, _ = sl.check_fit(self.swap, [r])
        self.assertTrue(probs and "X" in probs[0])

    def test_fit_ignores_untimed_channels(self):
        r = row(id="X", channel="logo", action="SWAP", start="0", end="0.1", replacement="a very long logo note here")
        self.assertEqual(sl.check_fit(self.swap, [r])[0], [])

    def test_fit_chinese_units(self):
        s = dict(self.swap, language="zh", rates={})
        r = row(id="Z", channel="voice", action="SWAP", start="0", end="2", replacement="每根燕麦棒含九克蛋白质")
        probs, rep = sl.check_fit(s, [r])
        self.assertIn("11 units", rep[0])
        self.assertTrue(probs)

    def test_claim_number_needs_fact(self):
        r = row(id="C", action="SWAP", replacement="Loved by 40,000 runners")
        self.assertTrue(any("40,000" in p for p in sl.check_claims(self.swap, [r])))

    def test_claim_backed_number_passes(self):
        r = row(id="C", action="SWAP", replacement="Ships to 12 countries", fact="F2")
        self.assertEqual(sl.check_claims(self.swap, [r]), [])

    def test_superlative_flagged(self):
        r = row(id="C", action="SWAP", replacement="The best bar in your bag")
        self.assertTrue(sl.check_claims(self.swap, [r]))

    def test_unknown_fact_id(self):
        r = row(id="C", action="SWAP", replacement="Simple oats", fact="F9")
        self.assertTrue(any("F9" in p for p in sl.check_claims(self.swap, [r])))

    def test_sweep_finds_split_name_and_colour(self):
        hits = sl.sweep(self.swap, [os.path.join(EX, "description.txt"), os.path.join(EX, "composition.css")])
        self.assertTrue(any("split" in h for h in hits))
        self.assertTrue(any("#e5592f" in h for h in hits))

    def test_sweep_clean_file(self):
        self.assertEqual(sl.sweep(self.swap, [os.path.join(EX, "render-captions.srt"), os.path.join(EX, "frame-text.txt")]), [])

    def test_ledger_open_items(self):
        s = dict(self.swap, channels_checked={})
        rows = [row(id="A", channel="voice", action="ASK", what="VO"), row(id="B", channel="sound", action="NEUTRAL", rights="unknown")]
        probs = sl.ledger_open(s, rows)
        self.assertTrue(any("ASK" in p for p in probs))
        self.assertTrue(any("unknown" in p for p in probs))
        self.assertTrue(any("not walked" in p for p in probs))

    def test_gate_cli_verdicts(self):
        files = [os.path.join(EX, f) for f in ("swap.json", "ledger.csv", "render-captions.srt", "frame-text.txt")]
        out = subprocess.run([sys.executable, SCRIPT, "gate"] + files, capture_output=True, text=True)
        self.assertIn("VERDICT CLEAN", out.stdout)
        out = subprocess.run([sys.executable, SCRIPT, "gate"] + files + [os.path.join(EX, "description.txt")], capture_output=True, text=True)
        self.assertIn("VERDICT RESIDUE", out.stdout)
        self.assertEqual(out.returncode, 1)
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run([sys.executable, SCRIPT, "gate"] + files[:2], capture_output=True, text=True)
            self.assertIn("VERDICT OPEN", out.stdout)


if __name__ == "__main__":
    unittest.main()
