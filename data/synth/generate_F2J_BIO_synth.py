#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate synthetic BIO-tagged address data (Group F2J) and write to CoNLL.

Examples
--------
# From project root (recommended):
python -m data.synth.generate_F2J_BIO_synth --n 1000 --out data/synth_data/synth_group_F2J.conll --preview 3 --stats

# From inside data/synth/:
python generate_F2J_BIO_synth.py -n 200 --out ../synth_group_F2J.conll --preview 3 --stats
"""
import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# ------------------------------------------------------------------------------------------
# Import generator + config with a robust path strategy (works from module or script runs)
# ------------------------------------------------------------------------------------------
def _bootstrap_imports():
    """
    Make project root importable (expects both 'data' and 'src' dirs under root).
    Then import the generator & config robustly.
    """
    here = Path(__file__).resolve()
    root = next((p for p in [here, *here.parents] if (p / "data").exists() and (p / "src").exists()), None)
    if root and str(root) not in sys.path:
        sys.path.insert(0, str(root))

_bootstrap_imports()

# Try package-style import first, then local fallback, then synth/ fallback
try:
    from data.synth.group_F2J_BIO_synth import (
        generate_group_F2J_dataset,
        to_conll,
    )
    from data.synth.config.general_config import (
        BINA_BLOK_KEYWORDS, BINA_APARTMAN_KEYWORDS,
    )
except Exception:
    try:
        from group_F2J_BIO_synth import (
            generate_group_F2J_dataset,
            to_conll,
        )
        from config.general_config import (
            BINA_BLOK_KEYWORDS, BINA_APARTMAN_KEYWORDS,
        )
    except Exception:
        from synth.group_F2J_BIO_synth import (
            generate_group_F2J_dataset,
            to_conll,
        )
        from synth.config.general_config import (
            BINA_BLOK_KEYWORDS, BINA_APARTMAN_KEYWORDS,
        )

Sample = Tuple[str, List[str], List[str]]  # (raw, tokens, tags)


# ------------------------------------------------------------------------------------------
# Pretty preview
# ------------------------------------------------------------------------------------------
def print_preview(samples: List[Sample], k: int = 3):
    k = min(k, len(samples))
    print("\n=== Preview ({} samples) ===".format(k))
    for i in range(k):
        raw, toks, tags = samples[i]
        print(f"\n[{i+1}] RAW: {raw}")
        print("TOKENS:", " ".join(toks))
        print("TAGS  :", " ".join(tags))


# ------------------------------------------------------------------------------------------
# Simple stats to check rule adherence
# ------------------------------------------------------------------------------------------
def _has_tag(tags: List[str], prefix: str) -> bool:
    # e.g. prefix="B-SITE_ADI" or "B-BULVAR"
    return any(t == prefix or t.startswith(prefix.replace("B-", "I-")) for t in tags)

def _any_in(seq, pool) -> bool:
    sp = set(x.lower() for x in pool)
    return any((s.lower() in sp) for s in seq)

def compute_stats(samples: List[Sample]):
    """
    Reports empirical frequencies vs. spec:
      - SITE rate ≈ 30%
      - Given SITE: BLOK rate ≈ 35% (within SITE subset)
      - Given NO SITE: APARTMAN rate ≈ 20%
      - Given any BINA: DAIRE_NO rate ≈ 15%
      - Given NO SITE: BULVAR rate ≈ 10%
    Also prints overall label distribution.
    """
    from collections import Counter

    n = len(samples)
    if n == 0:
        print("\n[stats] No samples.")
        return

    # Counters
    cnt = Counter()
    tag_counter = Counter()

    for raw, toks, tags in samples:
        tag_counter.update(tags)

        has_site = any(t.startswith("B-SITE_ADI") for t in tags)
        has_bulvar = any(t.startswith("B-BULVAR") for t in tags)

        # BINA detection by keywords + tag span presence
        has_bina_span = any(t.startswith("B-BINA_ADI") for t in tags)
        has_blok_kw = False
        has_apart_kw = False
        if has_bina_span:
            # rely on presence of specific tokens in the BINA phrase
            # (We don't reconstruct spans; keyword presence across all tokens is fine empirically)
            has_blok_kw = _any_in(toks, BINA_BLOK_KEYWORDS)
            has_apart_kw = _any_in(toks, BINA_APARTMAN_KEYWORDS)

        has_daire = any(t.startswith("B-DAIRE_NO") for t in tags)

        # Aggregate
        if has_site:
            cnt["site_total"] += 1
            if has_blok_kw:
                cnt["site_with_blok"] += 1
        else:
            cnt["nosite_total"] += 1
            if has_apart_kw:
                cnt["nosite_with_apartman"] += 1
            if has_bulvar:
                cnt["nosite_with_bulvar"] += 1

        if has_bina_span:
            cnt["bina_total"] += 1
            if has_daire:
                cnt["bina_with_daire"] += 1

    # Pretty print
    def pct(num, den):
        return (100.0 * num / den) if den else 0.0

    print("\n=== Sanity Stats (empirical) ===")
    print(f"Total samples: {n}")
    print(f"SITE present: {cnt['site_total']}  ({pct(cnt['site_total'], n):5.1f}%)")
    if cnt["site_total"]:
        print(f"  └─ BLOK given SITE: {cnt['site_with_blok']}  ({pct(cnt['site_with_blok'], cnt['site_total']):5.1f}%)")
    print(f"NO-SITE: {cnt['nosite_total']}  ({pct(cnt['nosite_total'], n):5.1f}%)")
    if cnt["nosite_total"]:
        print(f"  ├─ APARTMAN given NO-SITE: {cnt['nosite_with_apartman']}  ({pct(cnt['nosite_with_apartman'], cnt['nosite_total']):5.1f}%)")
        print(f"  └─ BULVAR given NO-SITE:   {cnt['nosite_with_bulvar']}   ({pct(cnt['nosite_with_bulvar'], cnt['nosite_total']):5.1f}%)")

    if cnt["bina_total"]:
        print(f"Any BINA: {cnt['bina_total']}  ({pct(cnt['bina_total'], n):5.1f}%)")
        print(f"  └─ DAIRE given BINA: {cnt['bina_with_daire']}  ({pct(cnt['bina_with_daire'], cnt['bina_total']):5.1f}%)")

    # Label distribution (top 15)
    print("\nTop tags:")
    for tag, c in tag_counter.most_common(15):
        print(f"  {tag:12s} : {c}")


# ------------------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------------------
def build_argparser():
    ap = argparse.ArgumentParser(
        description="Generate Group F2J synthetic BIO-tagged address data and save as CoNLL."
    )
    ap.add_argument("-n",  "--n",     type=int,   default=1000, help="Number of samples to generate.")
    ap.add_argument("--out",          type=str,   default="data/synth_data/synth_group_F2J.conll", help="Output CoNLL file.")
    ap.add_argument("--group",        type=str,   default="F2J", help="Group label to write into headers.")
    ap.add_argument("--seed",         type=int,   default=42,    help="Random seed.")
    ap.add_argument("--preview",      type=int,   default=0,     help="Print K sample previews to stdout.")
    ap.add_argument("--stats",        action="store_true",       help="Compute and print sanity stats.")
    return ap

def gen_samples(n: int, seed: int = 42) -> List[Sample]:
    # group_F2J provides this generator helper
    return generate_group_F2J_dataset(n=n, seed=seed)

def main():
    args = build_argparser().parse_args()

    # Generate
    samples = gen_samples(args.n, args.seed)

    # Write CoNLL
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    to_conll(samples, str(out_path), group_label=args.group)
    print(f"Wrote {len(samples)} samples to {out_path}")

    # Optional preview + stats
    if args.preview > 0:
        print_preview(samples, args.preview)
    if args.stats:
        compute_stats(samples)

if __name__ == "__main__":
    main()
