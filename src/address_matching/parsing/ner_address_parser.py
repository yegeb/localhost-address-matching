#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict_address_ner_stream.py
-----------------------------
Version-proof & memory-safe NER inference for *very large* CSVs.
- Works with old/new `transformers` (handles absence of `truncation` kw).
- Streams the CSV in chunks (no need to load entire file to RAM).
- Batches texts for faster inference and writes results incrementally.

Outputs a CSV with original columns +:
- pred_tags      (space-separated BIO over whitespace tokens)
- entities_json  (list of dicts: type,text,start,end,score)
- entities_flat  ("TYPE=text | TYPE=text | ...")

Example:
python ner_address_parser.py \
  --model-dir /path/to/BERTurk_stage1_out \
  --csv /path/to/input.csv \
  --text-col 0 \
  --out /path/to/predictions.csv \
  --chunk-size 5000 \
  --batch-size 32 \
  --device -1

Tip: Use --device 0 if you have a GPU.
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import re
import sys
from typing import List, Dict, Any, Tuple

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, TokenClassificationPipeline

# ---------- loading ----------

def load_pipeline(model_dir: str, device: int | None = None) -> TokenClassificationPipeline:
    tok = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    if device is None:
        device = 0 if torch.cuda.is_available() else -1
    return TokenClassificationPipeline(model=model, tokenizer=tok, aggregation_strategy="simple", device=device)

# ---------- token alignment helpers ----------

_WS_TOKEN_RE = re.compile(r"\S+")

def whitespace_tokens_with_offsets(text: str):
    tokens: List[str] = []
    offsets: List[Tuple[int, int]] = []
    for m in _WS_TOKEN_RE.finditer(text):
        tokens.append(m.group(0))
        offsets.append((m.start(), m.end()))
    return tokens, offsets

def spans_to_bio(text: str, spans: List[Dict[str, Any]]):
    tokens, offsets = whitespace_tokens_with_offsets(text)
    tags = ["O"] * len(tokens)
    spans_sorted = sorted(spans, key=lambda x: x.get("start", 0))
    for sp in spans_sorted:
        label = sp.get("entity_group") or sp.get("entity") or "ENT"
        s = int(sp["start"]); e = int(sp["end"]); first = True
        for i, (ts, te) in enumerate(offsets):
            if te <= s: 
                continue
            if ts >= e:
                break
            if ts < e and te > s:
                tags[i] = f"{'B' if first else 'I'}-{label}"
                first = False
    return tokens, tags

def aggregate_entities(text: str, spans: List[Dict[str, Any]]):
    ents = []
    for sp in sorted(spans, key=lambda x: x.get("start", 0)):
        label = sp.get("entity_group") or sp.get("entity") or "ENT"
        start = int(sp["start"]); end = int(sp["end"])
        ent_text = text[start:end]; score = float(sp.get("score", 0.0))
        ents.append({"type": label, "text": ent_text, "start": start, "end": end, "score": score})
    return ents

def join_entities_flat(entities: List[Dict[str, Any]]) -> str:
    from collections import defaultdict
    bucket = defaultdict(list)
    for e in entities:
        bucket[e["type"]].append(e["text"])
    parts = []
    for t, vals in bucket.items():
        for v in vals:
            parts.append(f"{t}={v}")
    return " | ".join(parts)

# ---------- inference ----------

def call_pipe_version_safe(pipe: TokenClassificationPipeline, inputs, max_length: int | None):
    """
    Some transformers versions reject `truncation`/`max_length` at call time for token-classification.
    We try with them once; on TypeError, we retry without.
    """
    if max_length is not None:
        try:
            return pipe(inputs, truncation=True, max_length=max_length)
        except TypeError:
            return pipe(inputs)
    else:
        return pipe(inputs)

def process_batch(pipe: TokenClassificationPipeline, batch_texts: List[str], max_length: int | None) -> List[Dict[str, Any]]:
    spans_list = call_pipe_version_safe(pipe, batch_texts, max_length)
    out = []
    for text, spans in zip(batch_texts, spans_list):
        ents = aggregate_entities(text, spans)
        tokens, tags = spans_to_bio(text, spans)
        out.append({
            "text": text,
            "tokens": tokens,
            "pred_tags": " ".join(tags),
            "entities_json": json.dumps(ents, ensure_ascii=False),
            "entities_flat": join_entities_flat(ents),
        })
    return out

# ---------- CSV streaming ----------

def iter_csv_chunks(path: str, chunksize: int, header_none_try: bool, text_col):
    """
    A generator that yields (df_chunk, text_series) with strings only.
    If header_none_try is True, read first with header=None; otherwise infer header.
    """
    if header_none_try:
        reader = pd.read_csv(path, header=None, dtype=str, keep_default_na=False, chunksize=chunksize)
        for df in reader:
            if isinstance(text_col, int):
                yield df, df.iloc[:, text_col].astype(str)
            else:
                # If user gave a name but we used header=None, switch to header=infer for the next run
                raise ValueError("You provided a column name but file is read as header=None. Re-run with --header infer and --text-col as the name.")
    else:
        reader = pd.read_csv(path, header="infer", dtype=str, keep_default_na=False, chunksize=chunksize)
        for df in reader:
            if isinstance(text_col, int):
                yield df, df.iloc[:, text_col].astype(str)
            else:
                if text_col not in df.columns:
                    raise ValueError(f"Column '{text_col}' not found. Available: {list(df.columns)}")
                yield df, df[text_col].astype(str)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--text-col", default="0", help="Index (int) or name (str) of the address column")
    ap.add_argument("--out", default="predictions.csv")
    ap.add_argument("--chunk-size", type=int, default=5000, help="Rows per chunk to stream")
    ap.add_argument("--batch-size", type=int, default=32, help="Texts per forward pass")
    ap.add_argument("--device", type=int, default=None, help="-1 CPU, 0 GPU0, ...")
    ap.add_argument("--max-length", type=int, default=None, help="Tokenizer max_length; omit to let defaults apply")
    ap.add_argument("--header", choices=["infer","none"], default="none", help="CSV header mode")
    args = ap.parse_args()

    # Coerce text_col to int if numeric
    try:
        text_col = int(args.text_col)
    except ValueError:
        text_col = args.text_col  # name

    sys.stderr.write(f"[info] Loading model from: {args.model_dir}\n")
    pipe = load_pipeline(args.model_dir, device=args.device)

    # Prepare writer
    write_header = True
    mode = "w"
    total_rows = 0
    header_none_try = (args.header == "none")

    with open(args.out, mode, newline="", encoding="utf-8") as fout:
        writer = None

        for df_chunk, text_series in iter_csv_chunks(args.csv, args.chunk_size, header_none_try, text_col):
            rows = df_chunk.to_dict(orient="records")
            texts = text_series.tolist()
            total_rows += len(texts)

            # Process in sub-batches for speed
            results_rows: List[Dict[str, Any]] = []
            for i in range(0, len(texts), args.batch_size):
                batch_texts = texts[i:i+args.batch_size]
                batch_out = process_batch(pipe, batch_texts, args.max_length)
                # Merge with original row dicts
                for orig, pred in zip(rows[i:i+args.batch_size], batch_out):
                    merged = orig.copy()
                    merged["pred_tags"] = pred["pred_tags"]
                    merged["entities_json"] = pred["entities_json"]
                    merged["entities_flat"] = pred["entities_flat"]
                    results_rows.append(merged)

            # Initialize CSV DictWriter once with combined fieldnames
            if writer is None:
                fieldnames = list(results_rows[0].keys()) if results_rows else list(df_chunk.columns) + ["pred_tags","entities_json","entities_flat"]
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()

            # Stream write
            for row in results_rows:
                writer.writerow(row)

            sys.stderr.write(f"[info] Wrote {total_rows} rows so far...\n")

    sys.stderr.write(f"[done] Finished. Total rows: {total_rows}. Output: {args.out}\n")


if __name__ == "__main__":
    main()
