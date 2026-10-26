#!/usr/bin/env python3
"""Run the standard reel checks on every reel of one source, from its
work/<slug>/reels.json (so no per-slug check_reel.py copy is needed).
Usage:  /Users/venkyb/envs/bie-work/bin/python3 tools/check_slug.py <slug> [NN ...]
Checks (same as check_reel.py): 1080x1920, under 60s, English spelling
(dictionary + tools/sanskrit_terms.py + EXTRA_NAMES below), caption-boundary
cut check, plus the finished file's trailing quiet. Exit 1 on any FAIL."""
import importlib.util, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("ep05check", os.path.join(ROOT, "work", "venkatachala-ep05", "check_reel.py"))
cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
# proper nouns / words used in later sources (extend as needed)
EXTRA_NAMES = {"vrishabhasura", "vrishabha", "vrishabhachala", "sheshachala", "sheshadeva", "shesha", "vayudeva", "vayu", "sudarshana",
               "navaratri", "sheshi", "anjana", "anjanachala", "anjanadevi", "matanga", "hanuman", "srinivasa", "venkatesha", "aradhana",
               "ambarisha", "kapila", "tirtha", "madhava", "venkatachala", "narasimha", "kesari", "satyatmateertha", "uttaradi",
               "chakra", "shloka", "puja", "pilgrimage", "arrogant", "mustard", "coil", "coiled", "flung", "settle"}
cr.ALLOWLIST = cr.ALLOWLIST | EXTRA_NAMES | set(json.load(open(os.path.join(ROOT, "work", sys.argv[1], "extra_words.json")))) if os.path.exists(os.path.join(ROOT, "work", sys.argv[1], "extra_words.json")) else cr.ALLOWLIST | EXTRA_NAMES
def tail_quiet(path, dur):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "silencedetect=noise=-30dB:d=0.1", "-f", "null", "-"], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if len(se) < len(ss): se.append(dur)
    return next((dur - s for s, e in zip(ss, se) if e >= dur - 0.05), 0.0)
def main():
    slug = sys.argv[1]; want = {int(n) for n in sys.argv[2:]}
    spec_j = json.load(open(os.path.join(ROOT, "work", slug, "reels.json"), encoding="utf-8"))
    dictionary = cr.load_dict(); bad_any = False
    for r in spec_j["reels"]:
        if want and r["num"] not in want: continue
        nn = f"{r['num']:02d}"; path = os.path.join(ROOT, "reels", slug, f"{slug}_{nn}_{r['topic']}.mp4")
        if not os.path.exists(path): print(f"[FAIL] {nn}: file missing"); bad_any = True; continue
        w, h, dur = cr.ffprobe_dims(path); fails = []
        if (w, h) != (1080, 1920): fails.append(f"dims {w}x{h}")
        if dur >= 60: fails.append(f"duration {dur:.1f}s")
        subs = [s[0] for s in r["subs"]] + [r["title_lead"] + " " + r["title_main"]] + [r["caption"]["title"]]
        bad, wrong = cr.spell_check(subs, dictionary)
        for a, b in wrong: fails.append(f"wrong transliteration {a!r} -> {b!r}")
        tq = tail_quiet(path, dur)
        if tq < 0.35: fails.append(f"tail quiet only {tq:.2f}s")
        sm, em, s_ok, e_ok = cr.boundary_cut_check(path, dur, r["start"], r["end"], os.path.join(ROOT, "sources", slug, "source.en.vtt"))
        print(f"{'FAIL' if fails else 'OK  '} {nn} {dur:5.1f}s tail {tq:.2f}s  spell-review={sorted(set(bad))}  {'; '.join(fails)}")
        bad_any |= bool(fails)
    sys.exit(1 if bad_any else 0)
main()
