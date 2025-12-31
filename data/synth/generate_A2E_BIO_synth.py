#!/usr/bin/env python3
"""
Generate synthetic BIO-tagged address data (Group A2E) and write to CoNLL.

Examples
--------
# From project root (recommended):
python -m data.synth.generate_BIO_synth --n 1000 --out data/synth_data/synth_group_A2E.conll --preview 3 --stats

# From inside data/synth/:
python generate_BIO_synth.py -n 200 --out ../synth_group_A2E.conll --preview 3 --stats
"""
import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# ---- Make imports robust no matter where you run from ----
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent           # e.g., .../data
ROOT = PARENT.parent           # project root (if any)

for p in (HERE, PARENT, ROOT):
    if p and p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Try local imports first (running inside data/synth/), then package-style (-m data.synth...)
try:
    from group_A2E_BIO_synth import GroupA2EGenerator, to_conll
except Exception:
    try:
        from synth.group_A2E_BIO_synth import GroupA2EGenerator, to_conll
    except Exception:
        from data.synth.group_A2E_BIO_synth import GroupA2EGenerator, to_conll

try:
    from config.groupA2E_config import SynthesisConfigA2E
    from config.general_config import KeywordVariants  # also holds gazetteers if you want to modify
except Exception:
    try:
        from synth.config.groupA2E_config import SynthesisConfigA2E
        from synth.config.general_config import KeywordVariants
    except Exception:
        from data.synth.config.groupA2E_config import SynthesisConfigA2E
        from data.synth.config.general_config import KeywordVariants

def gen_samples(n: int, seed: int) -> "List[Tuple[str, list[str], list[str]]]":
    gen = GroupA2EGenerator(variants=KeywordVariants(), cfg=SynthesisConfigA2E(), seed=seed)
    return [gen.generate_one() for _ in range(n)]

def print_preview(samples, k: int = 3):
    print("\n=== PREVIEW ===")
    for i, (raw, toks, tags) in enumerate(samples[:k], 1):
        print(f"\n#{i}  {raw}")
        for t, y in zip(toks, tags):
            print(f"{t}\t{y}")

def _first_idx(tags, *wanted):
    return next((i for i, y in enumerate(tags) if y in wanted), None)

def _has_token_with_tag(tokens, tags, token_set, tag_prefix):
    for t, y in zip(tokens, tags):
        if t.lower() in token_set and y.startswith(tag_prefix):
            return True
    return False

def compute_stats(samples):
    """
    Sanity checks for A2E:
      - Avenue/Street presence (cadde/sokak)
      - Building/Flat presence (bina/daire)
      - Floor (KAT) presence + pattern variants
      - Bare neighborhood usage (+ uppercase rate when bare)
      - Postcode before admin
      - Admin slash usage
      - Order: district->province vs province->district
      - Duplicated admin pair at start (+ neighborhood-prepended rate)
      - Segment shuffle among [neighborhood, avenue, street]
    """
    from collections import Counter, defaultdict

    c = Counter()
    floor_patterns = Counter()
    avenue_names = Counter()

    neighborhood_kw_set = { "mah.", "mh.", "mahallesi", "mah", "mh" }

    for raw, toks, tags in samples:
        # --- Presence: cadde/sokak ---
        has_cad = any(y.startswith(("B-CADDE","I-CADDE")) for y in tags)
        has_sk  = any(y.startswith(("B-SOKAK","I-SOKAK")) for y in tags)
        if has_cad and has_sk: c["cad+sk"] += 1
        elif has_cad:          c["cad_only"] += 1
        elif has_sk:           c["sk_only"] += 1
        else:                  c["no_cad_no_sk"] += 1

        # Avenue name tally (first CADDE token if present)
        try:
            first_cad_idx = tags.index("B-CADDE")
            avenue_names[toks[first_cad_idx]] += 1
        except ValueError:
            pass

        # --- Presence: bina/daire ---
        has_bina = any(y.startswith(("B-BINA_NO","I-BINA_NO")) for y in tags)
        has_dair = any(y.startswith(("B-DAIRE_NO","I-DAIRE_NO")) for y in tags)
        if has_bina and has_dair: c["bina+daire"] += 1
        elif has_bina:            c["bina_only"] += 1
        elif has_dair:            c["daire_only"] += 1
        else:                     c["no_bina_no_daire"] += 1

        # If both exist, check if flat (DAIRE) appears before building (BINA)
        b_bina = _first_idx(tags, "B-BINA_NO")
        b_dair = _first_idx(tags, "B-DAIRE_NO")
        if b_bina is not None and b_dair is not None:
            if b_dair < b_bina:
                c["flat_before_building"] += 1
            else:
                c["building_before_flat"] += 1

        # --- Floor (KAT) ---
        b_kat = _first_idx(tags, "B-KAT")
        if b_kat is not None:
            c["has_floor"] += 1
            # classify pattern using local context around B-KAT
            # patterns:
            #   A: "3 . kat"         -> num '.' 'kat'
            #   B: "<kw> : 3"        -> kw ':' num   (kw in kat/kat./k/k.)
            #   C: "<kw> 3"          -> kw num
            tok = toks[b_kat]
            nxt = toks[b_kat+1] if b_kat+1 < len(toks) else None
            nxt2= toks[b_kat+2] if b_kat+2 < len(toks) else None
            kw_like = tok.lower() in {"kat","kat.","k","k."}
            is_num  = tok.isdigit()
            if is_num and nxt == "." and (nxt2 and nxt2.lower().startswith("kat")):
                floor_patterns["num_dot_kat"] += 1
            elif kw_like and nxt == ":" and (nxt2 and nxt2.isdigit()):
                floor_patterns["kw_colon_num"] += 1
            elif kw_like and (nxt and nxt.isdigit()):
                floor_patterns["kw_num"] += 1
            else:
                floor_patterns["other"] += 1
        else:
            c["no_floor"] += 1

        # --- Bare neighborhood ---
        has_nei_kw_token = _has_token_with_tag(
            toks, tags, neighborhood_kw_set, "I-MAHALLE"
        )
        if not has_nei_kw_token:
            c["neighborhood_bare"] += 1
            # Check uppercase on bare neighborhood tokens (letters-only tokens)
            # Collect all MAHALLE tokens until we hit first non-MAHALLE after initial MAHALLE run
            nei_idxs = [i for i,y in enumerate(tags) if y.startswith(("B-MAHALLE","I-MAHALLE"))]
            letter_tokens = [t for i,t in enumerate(toks) if i in nei_idxs and any(ch.isalpha() for ch in t)]
            if letter_tokens and all(t == t.upper() for t in letter_tokens):
                c["neighborhood_bare_upper"] += 1
        else:
            c["neighborhood_with_kw"] += 1

        # --- Postcode ---
        b_pc = _first_idx(tags, "B-POSTA_KODU")
        if b_pc is not None:
            c["has_postcode"] += 1

        # --- Admin stats ---
        # slash
        if any(t == "/" and y == "O" for t, y in zip(toks, tags)):
            c["admin_slash"] += 1

        # ordering
        b_il   = _first_idx(tags, "B-IL")
        b_ilce = _first_idx(tags, "B-ILCE")
        if b_il is not None and b_ilce is not None:
            if b_ilce < b_il: c["district_first"] += 1
            else:             c["province_first"] += 1

        # duplicate admin at beginning (counts of B-IL + B-ILCE >= 4)
        total_admin_b = sum(1 for y in tags if y in {"B-IL","B-ILCE"})
        if total_admin_b >= 4:
            c["admin_duplicated_at_start"] += 1
            # was neighborhood prepended too?
            first_admin_idx = min(i for i,y in enumerate(tags) if y in {"B-IL","B-ILCE"})
            if any(i < first_admin_idx and tags[i].startswith(("B-MAHALLE","I-MAHALLE")) for i in range(len(tags))):
                c["admin_dup_with_neighborhood"] += 1

        # --- Segment shuffle among [neighborhood, avenue, street] ---
        # default order (no shuffle): neighborhood first, then avenue (if any), then street (if any).
        # we'll detect shuffle if:
        #   - first CADDE or first SOKAK appears before first MAHALLE, or
        #   - both CADDE and SOKAK exist and first SOKAK appears before first CADDE
        first_nei = _first_idx(tags, "B-MAHALLE")
        first_cad = _first_idx(tags, "B-CADDE")
        first_sok = _first_idx(tags, "B-SOKAK")
        shuffled = False
        if (first_cad is not None and first_nei is not None and first_cad < first_nei) or \
           (first_sok is not None and first_nei is not None and first_sok < first_nei):
            shuffled = True
        if first_cad is not None and first_sok is not None and first_sok < first_cad:
            shuffled = True
        if shuffled:
            c["segments_shuffled"] += 1
        else:
            c["segments_not_shuffled"] += 1

        # --- Postcode before admin check specifically ---
        if b_pc is not None and (b_il is not None or b_ilce is not None):
            first_admin = min([idx for idx in [b_il, b_ilce] if idx is not None])
            if b_pc < first_admin:
                c["postcode_before_admin"] += 1
            else:
                c["postcode_after_admin"] += 1

    total = len(samples)
    pct = lambda x: f"{(100.0*x/total):5.1f}%" if total else "n/a"

    print("\n=== STATS (sanity checks) ===")
    print(f"Total samples: {total}")
    print("\n-- Avenue/Street presence --")
    print(f"cad+sk        : {c['cad+sk']:5d}  ({pct(c['cad+sk'])})")
    print(f"cad_only      : {c['cad_only']:5d}  ({pct(c['cad_only'])})")
    print(f"sk_only       : {c['sk_only']:5d}  ({pct(c['sk_only'])})")
    print(f"none          : {c['no_cad_no_sk']:5d}  ({pct(c['no_cad_no_sk'])})")

    print("\n-- Building/Flat presence --")
    print(f"bina+daire    : {c['bina+daire']:5d}  ({pct(c['bina+daire'])})")
    print(f"bina_only     : {c['bina_only']:5d}  ({pct(c['bina_only'])})")
    print(f"daire_only    : {c['daire_only']:5d}  ({pct(c['daire_only'])})")
    print(f"none          : {c['no_bina_no_daire']:5d}  ({pct(c['no_bina_no_daire'])})")

    print("\n-- Flat/Building order when both exist --")
    print(f"flat→building : {c['flat_before_building']:5d}  ({pct(c['flat_before_building'])})")
    print(f"building→flat : {c['building_before_flat']:5d}  ({pct(c['building_before_flat'])})")

    print("\n-- Floor (KAT) --")
    print(f"has_floor     : {c['has_floor']:5d}  ({pct(c['has_floor'])})")
    print(f"no_floor      : {c['no_floor']:5d}  ({pct(c['no_floor'])})")
    if c["has_floor"]:
        total_floor = c["has_floor"]
        def fpct(x): return f"{(100.0*x/total_floor):5.1f}%"
        print(f"  num.dot.kat : {floor_patterns['num_dot_kat']:5d}  ({fpct(floor_patterns['num_dot_kat'])})")
        print(f"  kw:colon:num: {floor_patterns['kw_colon_num']:5d}  ({fpct(floor_patterns['kw_colon_num'])})")
        print(f"  kw num      : {floor_patterns['kw_num']:5d}  ({fpct(floor_patterns['kw_num'])})")
        print(f"  other       : {floor_patterns['other']:5d}  ({fpct(floor_patterns['other'])})")

    print("\n-- Neighborhood form --")
    print(f"bare          : {c['neighborhood_bare']:5d}  ({pct(c['neighborhood_bare'])})")
    print(f"  bare UPPER  : {c['neighborhood_bare_upper']:5d}  ({pct(c['neighborhood_bare_upper'])})")
    print(f"with keyword  : {c['neighborhood_with_kw']:5d}  ({pct(c['neighborhood_with_kw'])})")

    print("\n-- Admin formatting --")
    print(f"admin '/'     : {c['admin_slash']:5d}  ({pct(c['admin_slash'])})")
    print(f"ilçe→il       : {c['district_first']:5d}  ({pct(c['district_first'])})")
    print(f"il→ilçe       : {c['province_first']:5d}  ({pct(c['province_first'])})")

    print("\n-- Duplicate admin at start --")
    print(f"dup admin     : {c['admin_duplicated_at_start']:5d}  ({pct(c['admin_duplicated_at_start'])})")
    print(f"  +neighborhood: {c['admin_dup_with_neighborhood']:5d}  ({pct(c['admin_dup_with_neighborhood'])})")

    print("\n-- Segment shuffle (neighborhood/avenue/street) --")
    print(f"shuffled      : {c['segments_shuffled']:5d}  ({pct(c['segments_shuffled'])})")
    print(f"not shuffled  : {c['segments_not_shuffled']:5d}  ({pct(c['segments_not_shuffled'])})")

    print("\n-- Postcode --")
    print(f"has postcode  : {c['has_postcode']:5d}  ({pct(c['has_postcode'])})")
    print(f"  before admin: {c['postcode_before_admin']:5d}  ({pct(c['postcode_before_admin'])})")
    print(f"  after admin : {c['postcode_after_admin']:5d}  ({pct(c['postcode_after_admin'])})")

    # Optional: top avenues
    if avenue_names:
        top = avenue_names.most_common(10)
        print("\nTop avenue names:")
        for name, cnt in top:
            print(f"  {name:<22} {cnt:5d}")

def main():
    p = argparse.ArgumentParser(description="Generate synthetic Group A2E BIO CoNLL")
    p.add_argument("-n", "--n", type=int, default=1000, help="number of samples")
    p.add_argument("--seed", type=int, default=42, help="random seed")
    # default output: ../synth_group_A2E.conll relative to this script
    p.add_argument("--out", type=str, default=str((HERE.parent / "synth_group_A2E.conll").resolve()),
                   help="output .conll path")
    p.add_argument("--group", type=str, default="A2E", help="group label to write in headers")
    p.add_argument("--preview", type=int, default=0, help="print first K samples to stdout")
    p.add_argument("--stats", action="store_true", help="print simple distribution stats")
    args = p.parse_args()

    samples = gen_samples(args.n, args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    to_conll(samples, str(out_path), group_label=args.group)
    print(f"Wrote {len(samples)} samples to {out_path}")

    if args.preview > 0:
        print_preview(samples, args.preview)
    if args.stats:
        compute_stats(samples)

if __name__ == "__main__":
    main()
