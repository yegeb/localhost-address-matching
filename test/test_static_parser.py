#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_static_parser.py — manual cases with smart resolution & rich failure logs
(Updated to use data.ptt_data.map.Turkey)
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set

# ---------- 1) EDIT THESE CASES ------------------------------------------------
TEST_CASES: List[Tuple[str, str, str, str]] = [
    ("Caferağa Mah., Kadıköy / İstanbul No:12 D:5", "İstanbul", "Kadıköy", "Caferağa"),
    ("Etiler mahallesi Beşiktaş İstanbul sk. 14", "İstanbul", "Beşiktaş", "Etiler"),
    ("Kızılay Çankaya / Ankara cd:5 sk:9", "Ankara", "Çankaya", "Kızılay"),
    ("Acıbadem Mah Kadıköy İstanbul 3blok", "İstanbul", "Kadıköy", "Acıbadem"),
    ("Levent mah. Besiktas / Istanbul", "İstanbul", "Beşiktaş", "Levent"),
    ("Etlik mh keçiören ankara no:10", "Ankara", "Keçiören", "Etlik"),
    # add more...
]

# ---------- 2) BOOTSTRAP IMPORT PATHS -----------------------------------------
def find_project_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "src").exists() and (p / "data").exists():
            return p
    return start.parents[3]

PROJECT_ROOT = find_project_root(Path(__file__).resolve())
sys.path.insert(0, str(PROJECT_ROOT))

# ---------- 3) IMPORT YOUR PARSER & TREE --------------------------------------
import src.address_matching.parsing.static_parser as parsing
from data.ptt_data.map import Turkey

# Load XLSX deterministically (Turkey caches to pkl internally)
XLSX = PROJECT_ROOT / "data" / "ptt_data" / "turkiye_posta_kodlari.xlsx"
TR = Turkey.load(str(XLSX))

N = parsing.n.normalize_static_parser
INDICATOR_SUFFIXES = (" mah", " mahalle", " mahallesi")

# ---------- 4) UTILS -----------------------------------------------------------
def trunc(s: str, n: int) -> str:
    return (s[: n - 1] + "…") if len(s) > n else s

def tokens_wo_indicators(parser, text: str) -> List[str]:
    norm_text = parsing.n.normalize_static_parser(text)
    tks = norm_text.split()
    return [t for t in tks if t not in parser.INDICATOR_TOKENS]

def window_in_tokens(tokens: List[str], phrase: str) -> bool:
    parts = phrase.split()
    L = len(parts)
    for i in range(0, len(tokens) - L + 1):
        if tokens[i:i+L] == parts:
            return True
    return False

def suggest(keys: List[str], target: str, limit: int = 5) -> List[str]:
    target_tokens = target.split()
    def score(k: str):
        kt = k.split()
        common = len(set(kt) & set(target_tokens))
        contains = int(target in k or k in target)
        starts = int(k.startswith(target))
        return (contains, starts, common, -len(k))
    return [k for k in sorted(keys, key=score, reverse=True)[:limit]]

def resolve_nbhd_key(province_key: str, district_key: str, n_key: str) -> Tuple[str, List[str]]:
    """
    Try exact, then with common indicator suffixes under (province,district).
    Returns (resolved_key, notes).
    """
    notes: List[str] = []
    nlist = set(TR.neighbourhoods_of(province=province_key, district=district_key))
    if n_key in nlist:
        return n_key, notes
    for suff in INDICATOR_SUFFIXES:
        cand = n_key + suff
        if cand in nlist:
            notes.append(f"resolved neighbourhood '{n_key}' -> '{cand}' (tree key)")
            return cand, notes
    return n_key, notes

def explain_failure(parser, sentence, exp_p, exp_d, exp_n, got_p, got_d, got_n, tokens_no_ind) -> str:
    lines = []
    norm_sentence = parsing.n.normalize_static_parser(sentence)
    lines.append("---- DEBUG --------------------------------------------------")
    lines.append(f"Input (raw):   {sentence}")
    lines.append(f"Input (norm):  {norm_sentence}")
    lines.append(f"Tokens (-ind): {tokens_no_ind}")
    lines.append("")
    # Sizes from Turkey tree
    provs = list(TR.provinces())
    districts_count = sum(len(list(TR.districts_of(p))) for p in provs)
    nbhds_count = len(TR.neighbourhoods_of())  # all
    lines.append(f"Tree sizes: provinces={len(provs)} districts={districts_count} neighborhoods={nbhds_count}")
    lines.append("")
    # Province
    lines.append("[Province]")
    lines.append(f"  expected: {exp_p} | got: {got_p}")
    lines.append(f"  exists in tree: {exp_p in provs}")
    lines.append(f"  appears in tokens: {window_in_tokens(tokens_no_ind, exp_p)}")
    lines.append(f"  best cand (unrestricted): {parser._best_match(tokens_no_ind, parser._prov_index, None)}")
    lines.append("")
    # District
    lines.append("[District]")
    dists_in_p = set(TR.districts_of(exp_p)) if exp_p in provs else set()
    lines.append(f"  expected: {exp_d} | got: {got_d}")
    lines.append(f"  exists in tree under province: {exp_d in dists_in_p}")
    lines.append(f"  appears in tokens: {window_in_tokens(tokens_no_ind, exp_d)}")
    lines.append(f"  allowed_districts size: {len(dists_in_p) if dists_in_p else 'None'}")
    lines.append(f"  best cand (unrestricted): {parser._best_match(tokens_no_ind, parser._dist_index, None)}")
    lines.append(f"  best cand (restricted):   {parser._best_match(tokens_no_ind, parser._dist_index, dists_in_p) if dists_in_p else None}")
    lines.append("")
    # Neighbourhood
    lines.append("[Neighbourhood]")
    nkeys = list(TR.neighbourhoods_of(province=exp_p, district=exp_d)) if (exp_p in provs and exp_d in dists_in_p) else []
    lines.append(f"  expected: {exp_n} | got: {got_n}")
    lines.append(f"  exists in tree (under exp_p/exp_d): {exp_n in nkeys}")
    lines.append(f"  appears in tokens: {window_in_tokens(tokens_no_ind, exp_n)}")
    lines.append(f"  allowed_neighbourhoods size: {len(nkeys) if nkeys else 'None'}")
    lines.append(f"  best cand (unrestricted): {parser._best_match(tokens_no_ind, parser._nbhd_index, None)}")
    allow_n: Set[str] = set(nkeys) if nkeys else set()
    lines.append(f"  best cand (restricted):   {parser._best_match(tokens_no_ind, parser._nbhd_index, allow_n) if allow_n else None}")
    if nkeys:
        lines.append(f"  suggestions under '{exp_d}': {suggest(nkeys, exp_n)}")
    lines.append("------------------------------------------------------------")
    return "\n".join(lines)

# ---------- 5) TEST RUNNER -----------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Run manual test cases for StaticAddressParser (with smart resolution).")
    ap.add_argument("--max", type=int, default=9999, help="Max number of cases to run.")
    args = ap.parse_args()

    parser = parsing.StaticAddressParser()

    provs = list(TR.provinces())
    districts_count = sum(len(list(TR.districts_of(p))) for p in provs)
    nbhds_count = len(TR.neighbourhoods_of())

    print("\n# StaticAddressParser Manual Tests")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Tree sizes: provinces={len(provs)} districts={districts_count} neighborhoods={nbhds_count}")
    print(f"Cases provided: {len(TEST_CASES)}\n")

    header = f"{'RES':6} | {'INPUT (truncated)':55} | {'EXPECTED p/d/n':40} | {'GOT p/d/n'}"
    print(header)
    print("-" * len(header))

    total = 0
    ran = 0
    passed = 0
    failures: List[str] = []

    for sentence, p_raw, d_raw, n_raw in TEST_CASES[: args.max]:
        total += 1

        exp_p, exp_d, exp_n = N(p_raw), N(d_raw), N(n_raw)

        # province/district must exist; otherwise it's definitely a FAIL
        missing_pd = []
        if exp_p not in provs:
            missing_pd.append(f"province '{exp_p}'")
        dists_in_p = set(TR.districts_of(exp_p)) if exp_p in provs else set()
        if exp_d not in dists_in_p:
            missing_pd.append(f"district '{exp_d}' under '{exp_p}'")

        # Try to resolve neighbourhood to a tree key (attach suffixes if needed)
        resolved_n, notes = resolve_nbhd_key(exp_p, exp_d, exp_n)
        exp_tuple_used  = f"{exp_p}/{exp_d}/{resolved_n}"

        tokens_no_ind = tokens_wo_indicators(parser, sentence)
        out = parser.parse(sentence)
        got_p, got_d, got_n = out.province, out.district, out.neighbourhood

        ok = not missing_pd and (got_p == exp_p) and (got_d == exp_d) and (got_n == resolved_n)

        if ok:
            ran += 1
            passed += 1
            res = "PASS"
        else:
            ran += 1
            res = "FAIL"
            msg = [f"Expected (used): {exp_tuple_used}"]
            if notes:
                msg.append("Resolution notes: " + "; ".join(notes))
            if missing_pd:
                msg.append("Missing in tree: " + ", ".join(missing_pd))
            msg.append(explain_failure(parser, sentence, exp_p, exp_d, resolved_n, got_p, got_d, got_n, tokens_no_ind))
            failures.append("\n".join(msg))

        print(f"{res:6} | {trunc(sentence,55):55} | {trunc(exp_tuple_used,40):40} | {got_p}/{got_d}/{got_n}")

    print("\nSummary:")
    print(f"  Provided: {total}")
    print(f"  Ran:      {ran}")
    print(f"  Passed:   {passed}/{ran}" if ran else "  No runnable cases")

    if failures:
        print("\nFailures (verbose):")
        for f in failures:
            print(f)
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
