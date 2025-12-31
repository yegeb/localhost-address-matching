# -*- coding: utf-8 -*-
"""
group_F2J_BIO_synth.py
----------------------
F→J synthetic generator with:
- site/bina/daire/bulvar segments
- admin (province/district/neighbourhood) diversity
- TARIF (landmark) branch with category-aware pools/templates
- punctuation normalization (no ',' or '.' tokens in BIO)
- NEW: duplication of TARIF admin block and (optionally) the entire TARIF address
"""

from __future__ import annotations

import random
from typing import List, Tuple, Dict, Optional

from src.address_matching import AddressNormalizer

# ---------------------------------------------------------------------------
# Robust imports from configs
# ---------------------------------------------------------------------------
try:
    from .config.general_config import (
        provinces, districts, neighborhoods,
        FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
        KeywordVariants,
        COMMON_SITE_BASE_NAMES, COMMON_BLOK_LABELS, COMMON_APARTMAN_BASE_NAMES, COMMON_BULVAR_BASE_NAMES,
        SITE_TEMPLATES, BLOK_TEMPLATES, APARTMAN_TEMPLATES, BULVAR_TEMPLATES, DAIRE_NO_TEMPLATES,
        COMMON_TARIF_NAMES_BY_CAT, TARIF_TEMPLATES_BY_CAT,
    )
    from .config.groupF2J_config import SynthesisConfigF2J
    _HAS_NEW_TARIF = True
except Exception:
    try:
        from config.general_config import (
            provinces, districts, neighborhoods,
            FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
            KeywordVariants,
            COMMON_SITE_BASE_NAMES, COMMON_BLOK_LABELS, COMMON_APARTMAN_BASE_NAMES, COMMON_BULVAR_BASE_NAMES,
            SITE_TEMPLATES, BLOK_TEMPLATES, APARTMAN_TEMPLATES, BULVAR_TEMPLATES, DAIRE_NO_TEMPLATES,
            COMMON_TARIF_NAMES_BY_CAT, TARIF_TEMPLATES_BY_CAT,
        )
        from config.groupF2J_config import SynthesisConfigF2J
        _HAS_NEW_TARIF = True
    except Exception:
        from synth.config.general_config import (
            provinces, districts, neighborhoods,
            FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
            KeywordVariants,
            COMMON_SITE_BASE_NAMES, COMMON_BLOK_LABELS, COMMON_APARTMAN_BASE_NAMES, COMMON_BULVAR_BASE_NAMES,
            SITE_TEMPLATES, BLOK_TEMPLATES, APARTMAN_TEMPLATES, BULVAR_TEMPLATES, DAIRE_NO_TEMPLATES,
            COMMON_TARIF_BASE_NAMES, TARIF_TEMPLATES,
        )
        from synth.config.groupF2J_config import SynthesisConfigF2J
        _HAS_NEW_TARIF = False

# ---------------------------------------------------------------------------
# Optional runtime Turkey map (subset: İzmir, Aydın, Manisa, Muğla, Denizli)
# ---------------------------------------------------------------------------
TR_SUB = None
try:
    import sys
    from pathlib import Path
    HERE = Path(__file__).resolve()
    ROOT = next((p for p in [HERE, *HERE.parents] if (p / "data").exists() and (p / "src").exists()), None)
    if ROOT and str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import data.ptt_data as ptt_pkg
    from data.ptt_data.map import Turkey
    PKG_DIR = Path(ptt_pkg.__file__).resolve().parent
    xlsx_candidates = [
        PKG_DIR / "turkiye_posta_kodlari.xlsx",
        (ROOT / "data" / "ptt_data" / "turkiye_posta_kodlari.xlsx") if ROOT else None,
    ]
    XLSX = next((p for p in xlsx_candidates if p and p.exists()), None)
    if XLSX is None:
        raise FileNotFoundError
    _tr_sub = Turkey.load(str(XLSX)).subset_view()
    TR_SUB = _tr_sub if _tr_sub and list(_tr_sub.provinces()) else None
except Exception:
    TR_SUB = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick_admin_units() -> Tuple[str, str, str]:
    if TR_SUB is not None:
        prov_list = list(TR_SUB.provinces())
        if prov_list:
            province = random.choice(prov_list)
            district_list = list(TR_SUB.districts_of(province)) or FALLBACK_DISTRICTS.get(province, []) or ["Merkez"]
            district = random.choice(district_list)
            neighborhood_list = TR_SUB.neighbourhoods_of(province=province, district=district) \
                                or FALLBACK_NEIGHBORHOODS.get(district, []) or ["Merkez"]
            neighborhood = random.choice(neighborhood_list)
            return province, district, neighborhood
    province = random.choice(FALLBACK_PROVINCES)
    district = random.choice(FALLBACK_DISTRICTS.get(province, []) or ["Merkez"])
    neighborhood = random.choice(FALLBACK_NEIGHBORHOODS.get(district, []) or ["Merkez"])
    return province, district, neighborhood


def _emit_multi(tokens: List[str], tags: List[str], name: str, btag: str):
    parts = name.split()
    if not parts:
        return
    tokens.append(parts[0]); tags.append(btag)
    for p in parts[1:]:
        tokens.append(p); tags.append("I-" + btag[2:])


def _split_with_punct(text: str) -> List[str]:
    out: List[str] = []
    for token in text.split():
        cur = ""
        for ch in token:
            if ch in ":/":
                if cur:
                    out.append(cur); cur = ""
                out.append(ch)
            else:
                cur += ch
        if cur:
            out.append(cur)
    return out


def _upper_tokens(ts: List[str]) -> List[str]:
    return [t.upper() if t not in {"/", ":", ","} else t for t in ts]


def _normalize_and_strip_commas(raw_tokens: List[str], raw_tags: List[str]) -> Tuple[str, List[str], List[str]]:
    n = AddressNormalizer()
    raw = n.normalize_punctuation_only(" ".join(raw_tokens))
    t2: List[str] = []
    y2: List[str] = []
    for t, y in zip(raw_tokens, raw_tags):
        if t in {",", "."}:
            continue
        t2.append(t)
        y2.append(y)
    return raw, t2, y2


# ---------------------------------------------------------------------------
# TARIF (landmark) utilities: category-aware with weights
# ---------------------------------------------------------------------------

_DEFAULT_TARIF_CAT_WEIGHTS: Dict[str, float] = {
    "market_chain": 0.35,
    "local_shop":   0.15,
    "university":   0.10,
    "hospital":     0.10,
    "osb":          0.10,
    "hotel":        0.08,
    "avm":          0.12,
    "post_office":  0.00,
}

def _weighted_choice(mapping: Dict[str, float]) -> str:
    cats = [c for c, w in mapping.items() if w > 0]
    if not cats:
        if _HAS_NEW_TARIF:
            cats = list(COMMON_TARIF_NAMES_BY_CAT.keys())
        else:
            cats = ["__legacy__"]
    weights = [mapping.get(c, 0.0) for c in cats]
    total = sum(weights)
    if total <= 0:
        return random.choice(cats)
    r = random.random() * total
    cum = 0.0
    for c, w in zip(cats, weights):
        cum += w
        if r <= cum:
            return c
    return cats[-1]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class GroupF2JGenerator:
    """F2J: site/bina/daire/bulvar + admin diversity + TARIF (category-aware)."""

    def __init__(self, cfg: Optional[SynthesisConfigF2J] = None, seed: Optional[int] = None):
        self.cfg = cfg or SynthesisConfigF2J()
        if seed is not None:
            random.seed(seed)
        self._tarif_weights: Dict[str, float] = getattr(self.cfg, "tarif_category_weights", None) or _DEFAULT_TARIF_CAT_WEIGHTS

    # ------------------- Body segments -------------------

    def _segment_site(self):
        base = random.choice(COMMON_SITE_BASE_NAMES)
        phrase = random.choice(list(SITE_TEMPLATES)).format(name=base)
        toks = _split_with_punct(phrase)
        return toks, ["B-SITE_ADI"] + ["I-SITE_ADI"] * (len(toks) - 1)

    def _segment_bina_blok(self):
        label = random.choice(COMMON_BLOK_LABELS)
        toks = _split_with_punct(random.choice(list(BLOK_TEMPLATES)).format(label=label))
        return toks, ["B-BINA_ADI"] + ["I-BINA_ADI"] * (len(toks) - 1)

    def _segment_bina_apartman(self):
        base = random.choice(COMMON_APARTMAN_BASE_NAMES)
        toks = _split_with_punct(random.choice(list(APARTMAN_TEMPLATES)).format(name=base))
        return toks, ["B-BINA_ADI"] + ["I-BINA_ADI"] * (len(toks) - 1)

    def _segment_daire(self):
        num = str(random.randint(1, 120))
        toks = _split_with_punct(random.choice(list(DAIRE_NO_TEMPLATES)).format(no=num))
        return toks, ["B-DAIRE_NO"] + ["I-DAIRE_NO"] * (len(toks) - 1)

    def _segment_bulvar(self):
        base = random.choice(COMMON_BULVAR_BASE_NAMES)
        toks = _split_with_punct(random.choice(list(BULVAR_TEMPLATES)).format(name=base))
        return toks, ["B-BULVAR"] + ["I-BULVAR"] * (len(toks) - 1)

    # ------------------- TARIF segment (category-aware) -------------------

    def _segment_tarif(self):
        if _HAS_NEW_TARIF:
            cat = _weighted_choice(self._tarif_weights)
            names = COMMON_TARIF_NAMES_BY_CAT.get(cat, ())
            temps = TARIF_TEMPLATES_BY_CAT.get(cat, ("{name}",))
            if not names:
                non_empty = [c for c, lst in COMMON_TARIF_NAMES_BY_CAT.items() if lst]
                cat = random.choice(non_empty) if non_empty else cat
                names = COMMON_TARIF_NAMES_BY_CAT.get(cat, ("PTT",))
                temps = TARIF_TEMPLATES_BY_CAT.get(cat, ("{name}",))
            base = random.choice(list(names))
            phrase = random.choice(list(temps)).format(name=base)
        else:
            base = random.choice(list(COMMON_TARIF_BASE_NAMES))
            phrase = random.choice(list(TARIF_TEMPLATES)).format(name=base)

        toks = _split_with_punct(phrase)
        return toks, ["B-TARIF"] + ["I-TARIF"] * (len(toks) - 1)

    # ------------------- Admin blocks -------------------

    def _segment_admin_pd(self, province: str, district: str):
        t: List[str] = []; y: List[str] = []
        _emit_multi(t, y, district, "B-ILCE")
        t.append(","); y.append("O")
        _emit_multi(t, y, province, "B-IL")
        return t, y

    def _segment_admin_ndp(self, neighborhood: str, district: str, province: str,
                           uppercase: bool, use_slash: bool):
        t: List[str] = []; y: List[str] = []
        _emit_multi(t, y, neighborhood, "B-MAHALLE")
        if use_slash:
            t.append("/"); y.append("O")
            _emit_multi(t, y, district, "B-ILCE")
            t.append("/"); y.append("O")
            _emit_multi(t, y, province, "B-IL")
        else:
            _emit_multi(t, y, district, "B-ILCE")
            _emit_multi(t, y, province, "B-IL")
        if uppercase:
            t = _upper_tokens(t)
        return t, y

    def _segment_admin_only_one(self, province: str, district: str):
        t: List[str] = []; y: List[str] = []
        if random.random() < 0.5:
            _emit_multi(t, y, district, "B-ILCE")
        else:
            _emit_multi(t, y, province, "B-IL")
        return t, y
    
    def _inject_noise_and_boring_negatives(self, tokens: List[str], tags: List[str]) -> tuple[List[str], List[str]]:
        """ With p_noise_boring_negatives, inject -, /, | separators >=3x and append TR/Türkiye variant at the end. """
        if random.random() >= getattr(self.cfg, "p_noise_boring_negatives", 0.0):
            return tokens, tags

        sep_choices = list(getattr(self.cfg, "noise_separators", ("-", "/", "|")))
        min_seps = int(getattr(self.cfg, "min_noise_separators", 3))
        country_choices = list(getattr(self.cfg, "noise_country_tokens", ("tr", "TR", "Türkiye", "TÜRKİYE")))

        # 1) Candidate insertion points: before any token whose tag starts with 'B-' (and not at the very first token)
        candidate_starts = [i for i, y in enumerate(tags) if i > 0 and isinstance(y, str) and y.startswith("B-")]

        # Choose up to 'min_seps' different boundaries (or all if fewer exist)
        chosen = candidate_starts
        if len(candidate_starts) > min_seps:
            chosen = random.sample(candidate_starts, min_seps)

        # 2) Build a new sequence inserting separators before the chosen indices
        new_toks: List[str] = []
        new_tags: List[str] = []
        chosen_set = set(chosen)
        seps_added = 0

        for i, (t, y) in enumerate(zip(tokens, tags)):
            if i in chosen_set:
                s = random.choice(sep_choices)
                new_toks.append(s)
                new_tags.append("O")
                seps_added += 1
            new_toks.append(t)
            new_tags.append(y)

        # 3) If we still have fewer than 'min_seps', add extras at random safe positions
        # Avoid very first/last slot to keep shape natural
        while seps_added < min_seps and len(new_toks) > 2:
            j = random.randint(1, len(new_toks) - 2)
            # Try not to stack separators directly on punctuation; if you want stricter rules, adjust this guard
            if new_toks[j] not in sep_choices:
                s = random.choice(sep_choices)
                new_toks.insert(j, s)
                new_tags.insert(j, "O")
                seps_added += 1

        # 4) Always append one of country tokens at the very end
        new_toks.append(random.choice(country_choices))
        new_tags.append("O")

        return new_toks, new_tags

    # ------------------- Main -------------------

    def generate_one(self) -> Tuple[str, List[str], List[str]]:
        province, district, neighborhood = _pick_admin_units()
        tokens: List[str] = []; tags: List[str] = []

        # ---------------- TARIF branch ----------------
        if random.random() < self.cfg.p_tarif:
            t, y = self._segment_tarif()
            tokens += t; tags += y

            if random.random() < self.cfg.p_tarif_has_pd:
                if random.random() < self.cfg.p_tarif_ndp_given_pd:
                    ad_t, ad_y = self._segment_admin_ndp(
                        neighborhood, district, province,
                        uppercase=False,
                        use_slash=(self.cfg.p_tarif_ndp_use_slashes >= 1.0 or
                                   random.random() < self.cfg.p_tarif_ndp_use_slashes)
                    )
                else:
                    ad_t, ad_y = self._segment_admin_pd(province, district)

                place_front = (random.random() < self.cfg.p_tarif_pd_front_prob)

                dup_mode: Optional[str] = None
                if random.random() < getattr(self.cfg, "p_tarif_admin_duplicate", 0.0):
                    dup_mode = "front" if random.random() < getattr(self.cfg, "p_tarif_dup_to_front_prob", 0.5) else "after"
                    dup_t, dup_y = ad_t[:], ad_y[:]
                else:
                    dup_t, dup_y = [], []

                if place_front:
                    tokens[:0] = ad_t + [","]; tags[:0] = ad_y + ["O"]
                    if dup_mode == "front":
                        tokens[:0] = dup_t + [","]; tags[:0] = dup_y + ["O"]
                    elif dup_mode == "after":
                        insert_at = len(ad_t) + 1
                        tokens[insert_at:insert_at] = dup_t + [","]
                        tags  [insert_at:insert_at] = dup_y + ["O"]
                else:
                    tokens += [","] + ad_t; tags += ["O"] + ad_y
                    if dup_mode == "front":
                        tokens[:0] = dup_t + [","]; tags[:0] = dup_y + ["O"]
                    elif dup_mode == "after":
                        tokens += [","] + dup_t; tags += ["O"] + dup_y

            # NEW: 5% duplicate the entire TARIF address (tokens and tags)
            if random.random() < getattr(self.cfg, "p_tarif_duplicate_whole", 0.0):
                tokens = tokens + tokens
                tags   = tags + tags

            raw, tokens, tags = _normalize_and_strip_commas(tokens, tags)
            return raw, tokens, tags

        # ---------------- Non-TARIF branch ----------------
        has_site = (random.random() < self.cfg.p_has_site)

        if not has_site:
            if random.random() < self.cfg.p_has_bulvar_given_no_site:
                t, y = self._segment_bulvar(); tokens += t; tags += y
            if random.random() < self.cfg.p_bina_apartman_given_no_site:
                t, y = self._segment_bina_apartman(); tokens += t; tags += y
                if random.random() < self.cfg.p_has_daire_no_given_bina:
                    t, y = self._segment_daire(); tokens += t; tags += y
        else:
            t, y = self._segment_site(); tokens += t; tags += y
            if random.random() < self.cfg.p_bina_blok_given_site:
                t, y = self._segment_bina_blok(); tokens += t; tags += y
                if random.random() < self.cfg.p_has_daire_no_given_bina:
                    t, y = self._segment_daire(); tokens += t; tags += y

        # Admin diversity (non-TARIF)
        admin_t: List[str] = []; admin_y: List[str] = []
        r = random.random()
        cut1 = self.cfg.p_admin_ndp
        cut2 = cut1 + self.cfg.p_admin_pd
        cut3 = cut2 + self.cfg.p_admin_only_one

        pd_dup_mode: Optional[str] = None
        pd_dup_t: List[str] = []; pd_dup_y: List[str] = []

        if r < cut1:
            uppercase = (random.random() < self.cfg.p_uppercase_for_ndp)
            use_slash = (not uppercase) and (random.random() < self.cfg.p_ndp_use_slashes_when_not_upper)
            admin_t, admin_y = self._segment_admin_ndp(neighborhood, district, province, uppercase, use_slash)
        elif r < cut2:
            admin_t, admin_y = self._segment_admin_pd(province, district)
            if random.random() < self.cfg.p_admin_pd_duplicate:
                pd_dup_t, pd_dup_y = admin_t[:], admin_y[:]
                pd_dup_mode = "front" if random.random() < self.cfg.p_pd_dup_to_front_prob else "after"
        elif r < cut3:
            admin_t, admin_y = self._segment_admin_only_one(province, district)
        else:
            pass  # none

        if pd_dup_mode == "front":
            tokens[:0] = pd_dup_t + [","]; tags[:0] = pd_dup_y + ["O"]

        if admin_t:
            if tokens:
                tokens.append(","); tags.append("O")
            tokens += admin_t; tags += admin_y

        if pd_dup_mode == "after":
            if admin_t:
                tokens += [","] + pd_dup_t; tags += ["O"] + pd_dup_y
            else:
                tokens += pd_dup_t; tags += pd_dup_y

        # Inject A2E-specific noise / boring negatives (≈5%) *before* final normalization
        tokens, tags = self._inject_noise_and_boring_negatives(tokens, tags)

        # Header string normalized by your external function
        n = AddressNormalizer()
        raw = n.normalize_punctuation_only(" ".join(tokens))
        return raw, tokens, tags


# ---------------------------------------------------------------------------
# CoNLL writer & convenience
# ---------------------------------------------------------------------------

def to_conll(samples: List[Tuple[str, List[str], List[str]]], path: str, group_label: str = "F2J"):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for raw, toks, tags in samples:
            rid = random.randint(10000, 99999)
            f.write(f"{raw}, {rid}, {group_label}\n")
            for t, y in zip(toks, tags):
                f.write(f"{t}\t{y}\n")
            f.write("\n")


def generate_group_F2J_dataset(n: int, seed: int = 42):
    random.seed(seed)
    gen = GroupF2JGenerator(seed=seed)
    return [gen.generate_one() for _ in range(n)]
