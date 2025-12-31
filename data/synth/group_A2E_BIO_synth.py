import random
from typing import List, Tuple

# Use your real normalizer ONLY (no local fallbacks)
from src.address_matching import AddressNormalizer


def _upper_all_words(ts):
    """Uppercase all word tokens; keep separators like '/', ':', ',' as-is."""
    return [t.upper() if t not in {'/', ':', ','} else t for t in ts]

# Robust imports (package or script; config under synth/config/)
try:
    from .config.general_config import (
        provinces, districts, neighborhoods,
        FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
        FALLBACK_POSTCODES,
        KeywordVariants, COMMON_AVENUE_NAMES,
    )
    from .config.groupA2E_config import SynthesisConfigA2E
except Exception:
    try:
        from config.general_config import (
            provinces, districts, neighborhoods,
            FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
            FALLBACK_POSTCODES,
            KeywordVariants, COMMON_AVENUE_NAMES,
        )
        from config.groupA2E_config import SynthesisConfigA2E
    except Exception:
        from synth.config.general_config import (
            provinces, districts, neighborhoods,
            FALLBACK_PROVINCES, FALLBACK_DISTRICTS, FALLBACK_NEIGHBORHOODS,
            FALLBACK_POSTCODES,
            KeywordVariants, COMMON_AVENUE_NAMES,
        )
        from synth.config.groupA2E_config import SynthesisConfigA2E

# --- Prefer runtime tree from data.ptt_data.map.Turkey (new map.py) ---
TR_SUB = None
try:
    import sys
    from pathlib import Path

    # Ensure project root (must contain both "data" and "src") is importable
    HERE = Path(__file__).resolve()
    ROOT = next((p for p in [HERE, *HERE.parents] if (p / "data").exists() and (p / "src").exists()), None)
    if ROOT and str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # Import Turkey from the new map.py
    import data.ptt_data as ptt_pkg
    from data.ptt_data.map import Turkey

    # Locate the XLSX in data/ptt_data
    PKG_DIR = Path(ptt_pkg.__file__).resolve().parent
    xlsx_candidates = [
        PKG_DIR / "turkiye_posta_kodlari.xlsx",
        (ROOT / "data" / "ptt_data" / "turkiye_posta_kodlari.xlsx") if ROOT else None,
    ]
    XLSX = next((p for p in xlsx_candidates if p and p.exists()), None)
    if XLSX is None:
        raise FileNotFoundError("turkiye_posta_kodlari.xlsx not found under data/ptt_data")

    # Load with cache; Turkey class normalizes keys internally
    _tr_sub = Turkey.load(str(XLSX)).subset_view()
    # Use only if it actually has data
    TR_SUB = _tr_sub if _tr_sub and list(_tr_sub.provinces()) else None

except Exception as e:
    # For quick debugging, uncomment:
    # print(f"[A2E] Turkey tree unavailable: {e}")
    TR_SUB = None



# --------------------------------- Core helpers --------------------------------- #

def _pick_admin_units() -> Tuple[str, str, str]:
    """
    Returns (province, district, neighborhood) using the runtime Turkey tree if available,
    otherwise falls back to static lists.
    """
    if TR_SUB is not None:
        prov_list = list(TR_SUB.provinces())
        if prov_list:
            province = random.choice(prov_list)
            district_list = list(TR_SUB.districts_of(province))
            if not district_list:
                district_list = FALLBACK_DISTRICTS.get(province, []) or ["Merkez"]
            district = random.choice(district_list)

            neighborhood_list = TR_SUB.neighbourhoods_of(province=province, district=district)
            if not neighborhood_list:
                neighborhood_list = FALLBACK_NEIGHBORHOODS.get(district, []) or ["Merkez"]
            neighborhood = random.choice(neighborhood_list)
            return province, district, neighborhood

    # Fallback path (TR missing or empty)
    province = random.choice(FALLBACK_PROVINCES)
    district_list = FALLBACK_DISTRICTS.get(province, []) or ["Merkez"]
    district = random.choice(district_list)
    neighborhood_list = FALLBACK_NEIGHBORHOODS.get(district, []) or ["Merkez"]
    neighborhood = random.choice(neighborhood_list)
    return province, district, neighborhood



def _maybe_upper(s: str, p: float) -> str:
    return s.upper() if random.random() < p else s

def _split_number_token(num_str: str) -> List[str]:
    # We never emit '.' in numbers, but keep support for '/', ':'
    out, cur = [], ""
    for ch in num_str:
        if ch in "/:":
            if cur:
                out.append(cur); cur = ""
            out.append(ch)
        else:
            cur += ch
    if cur: out.append(cur)
    return out

def _random_street_number() -> List[str]:
    if random.random() < 0.35:
        s = f"{random.randint(1, 4000)}/{random.randint(1, 9)}"
    else:
        s = str(random.randint(1, 4000))
    return _split_number_token(s)

def _random_building_no() -> List[str]:
    base = [str(random.randint(1, 300))]
    if random.random() < 0.35:
        base += ["/", random.choice(list("ABCDEFGH"))]
    return base

def _random_flat_no() -> List[str]:
    return [str(random.randint(1, 120))]

def _attach_colon(keyword_tokens: List[str], p_colon: float) -> List[str]:
    return keyword_tokens + [":"] if random.random() < p_colon else keyword_tokens

def _sanitize_kw(kw: str) -> str:
    # Drop '.' and ',' from any keyword to match your normalization
    return kw.replace(".", "").replace(",", "")

def _emit_multi(tokens: List[str], tags: List[str], name: str, btag: str):
    parts = name.split()
    tokens.append(parts[0]); tags.append(btag)
    for p in parts[1:]:
        tokens.append(p); tags.append("I-" + btag[2:])


# --------------------------------- Segments --------------------------------- #

class GroupA2EGenerator:
    """
    A2E = combined/mixed patterns generator for BIO-tagged Turkish address data.
    Tags: MAHALLE, CADDE, SOKAK, BULVAR, BINA_NO, DAIRE_NO, KAT, BINA_ADI, SITE_ADI,
          POSTA_KODU, ILCE, IL, TARIF, O
    """
    def __init__(self, variants: KeywordVariants = None, cfg: SynthesisConfigA2E = None, seed: int = None):
        self.variants = variants or KeywordVariants()
        self.cfg = cfg or SynthesisConfigA2E()
        if seed is not None:
            random.seed(seed)

    # --- NEIGHBORHOOD (with optional bare form & uppercase) ---
    def _segment_neighborhood(self, neighborhood: str) -> Tuple[List[str], List[str]]:
        t: List[str] = []
        y: List[str] = []
        use_bare = (random.random() < self.cfg.p_neighborhood_bare)
        name = neighborhood
        if use_bare and random.random() < self.cfg.p_bare_neighborhood_uppercase:
            name = name.upper()

        if use_bare:
            parts = name.split()
            t.append(parts[0]); y.append("B-MAHALLE")
            for p in parts[1:]:
                t.append(p); y.append("I-MAHALLE")
        else:
            kw = _sanitize_kw(self.variants.pick("neighborhood_kw"))
            _emit_multi(t, y, name, "B-MAHALLE")
            t.append(kw); y.append("I-MAHALLE")
        return t, y

    # --- AVENUE (CADDE) ---
    def _segment_avenue(self) -> Tuple[List[str], List[str]]:
        t: List[str] = []
        y: List[str] = []
        ave_name = random.choice(COMMON_AVENUE_NAMES)
        kw = _sanitize_kw(self.variants.pick("avenue_kw"))
        _emit_multi(t, y, ave_name, "B-CADDE")
        t.append(kw); y.append("I-CADDE")
        return t, y

    # --- STREET (SOKAK) ---
    def _segment_street(self) -> Tuple[List[str], List[str]]:
        t: List[str] = []
        y: List[str] = []
        nums = _random_street_number()
        kw = _sanitize_kw(self.variants.pick("street_kw"))
        t.append(nums[0]); y.append("B-SOKAK")
        for extra in nums[1:]:
            t.append(extra); y.append("I-SOKAK")
        t.append(kw); y.append("I-SOKAK")
        return t, y

    # --- BUILDING NO ---
    def _segment_building_no(self) -> Tuple[List[str], List[str]]:
        t: List[str] = []
        y: List[str] = []
        kw_parts = _sanitize_kw(self.variants.pick("building_no_kw")).split()
        kw_parts = _attach_colon(kw_parts, self.cfg.p_colon_after_numbers)
        t.append(kw_parts[0]); y.append("B-BINA_NO")
        for k in kw_parts[1:]:
            t.append(k); y.append("I-BINA_NO")
        for v in _random_building_no():
            t.append(v); y.append("I-BINA_NO")
        return t, y

    # --- FLAT NO ---
    def _segment_flat_no(self) -> Tuple[List[str], List[str]]:
        t: List[str] = []
        y: List[str] = []
        kw_parts = _sanitize_kw(self.variants.pick("flat_no_kw")).split()
        kw_parts = _attach_colon(kw_parts, self.cfg.p_colon_after_numbers)
        t.append(kw_parts[0]); y.append("B-DAIRE_NO")
        for k in kw_parts[1:]:
            t.append(k); y.append("I-DAIRE_NO")
        for v in _random_flat_no():
            t.append(v); y.append("I-DAIRE_NO")
        return t, y

    # --- FLOOR (KAT) ---
    def _segment_floor(self) -> Tuple[List[str], List[str]]:
        """
        Variants (without any '.' tokens):
          - "3 kat"           -> ["3", "kat"]
          - "kat : 3"         -> ["kat", ":", "3"]
          - "k : 3"           -> ["k", ":", "3"]
          - "kat 3"           -> ["kat", "3"]
        """
        t: List[str] = []
        y: List[str] = []
        template = random.choice([0, 1, 2, 3])
        num = str(random.randint(1, 20))
        if template == 0:
            t.extend([num, "kat"]); y.extend(["B-KAT", "I-KAT"])
        elif template == 1:
            kw = _sanitize_kw(self.variants.pick("floor_kw"))
            t.extend([kw, ":", num]); y.extend(["B-KAT", "I-KAT", "I-KAT"])
        elif template == 2:
            kw = "k"
            t.extend([kw, ":", num]); y.extend(["B-KAT", "I-KAT", "I-KAT"])
        else:
            kw = _sanitize_kw(self.variants.pick("floor_kw"))
            t.extend([kw, num]); y.extend(["B-KAT", "I-KAT"])
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


    def generate_one(self) -> Tuple[str, List[str], List[str]]:
        province, district, neighborhood = _pick_admin_units()
        neighborhood_disp = _maybe_upper(neighborhood, self.cfg.p_uppercase_neighborhood)
        province_disp = _maybe_upper(province, self.cfg.p_uppercase_admin)
        district_disp = _maybe_upper(district, self.cfg.p_uppercase_admin)

        tokens: List[str] = []
        tags: List[str] = []

        # --- Core segments (neighborhood + optional repetition, avenue/street) ---
        body_segments: List[Tuple[List[str], List[str]]] = []

        seg_nei = self._segment_neighborhood(neighborhood_disp)
        body_segments.append(seg_nei)

        if random.random() < self.cfg.p_repeat_neighborhood:
            body_segments.append(self._segment_neighborhood(neighborhood_disp))

        r = random.random()
        include_avenue = include_street = False
        if r < self.cfg.p_both_avenue_street:
            include_avenue = include_street = True
        elif r < self.cfg.p_both_avenue_street + self.cfg.p_only_avenue:
            include_avenue = True
        else:
            include_street = True

        if include_avenue:
            body_segments.append(self._segment_avenue())
        if include_street:
            body_segments.append(self._segment_street())

        if random.random() < self.cfg.p_shuffle_segments and len(body_segments) > 1:
            random.shuffle(body_segments)

        for t, y in body_segments:
            tokens.extend(t); tags.extend(y)

        # --- Building / Flat ---
        r = random.random()
        include_building = include_flat = False
        if r < self.cfg.p_both_building_flat:
            include_building = include_flat = True
        elif r < self.cfg.p_both_building_flat + self.cfg.p_only_building:
            include_building = True
        else:
            include_flat = True

        seg_building = self._segment_building_no() if include_building else None
        seg_flat = self._segment_flat_no() if include_flat else None
        seg_floor = self._segment_floor() if (random.random() < self.cfg.p_include_floor) else None

        if seg_building and seg_flat and random.random() < self.cfg.p_swap_flat_before_building_when_both:
            for seg in (seg_flat, seg_building, seg_floor):
                if seg:
                    t, y = seg; tokens.extend(t); tags.extend(y)
        else:
            for seg in (seg_building, seg_flat, seg_floor):
                if seg:
                    t, y = seg; tokens.extend(t); tags.extend(y)

        # --- POSTA_KODU before admin (10%) ---
        if random.random() < self.cfg.p_postcode_before_admin:
            from synth.config.general_config import FALLBACK_POSTCODES  # keep origin
            code = random.choice(FALLBACK_POSTCODES)
            tokens.append(code); tags.append("B-POSTA_KODU")

        # --- Admin pair at end ---
        use_slash = (random.random() < self.cfg.p_slash_between_admin)
        district_first = (random.random() < self.cfg.p_district_first)

        def emit_admin_pair(tok_list: List[str], tag_list: List[str]):
            if district_first:
                _emit_multi(tok_list, tag_list, district_disp, "B-ILCE")
                if use_slash:
                    tok_list.append("/"); tag_list.append("O")
                _emit_multi(tok_list, tag_list, province_disp, "B-IL")
            else:
                _emit_multi(tok_list, tag_list, province_disp, "B-IL")
                if use_slash:
                    tok_list.append("/"); tag_list.append("O")
                _emit_multi(tok_list, tag_list, district_disp, "B-ILCE")

        emit_admin_pair(tokens, tags)

        # --- Optional prepend admin (and maybe neighborhood) at beginning ---
        if random.random() < self.cfg.p_prepend_admin_again:
            pre_t: List[str] = []
            pre_y: List[str] = []
            if random.random() < self.cfg.p_prepend_with_neighborhood:
                _emit_multi(pre_t, pre_y, neighborhood_disp, "B-MAHALLE")
                if use_slash:
                    pre_t.append("/"); pre_y.append("O")
            emit_admin_pair(pre_t, pre_y)
            tokens = pre_t + tokens
            tags = pre_y + tags
        # Optional: make all words uppercase for a small portion of samples
        try:
            if random.random() < self.cfg.p_all_uppercase:
                tokens = _upper_all_words(tokens)
        except AttributeError:
            # Backward-compat if config lacks p_all_uppercase
            pass


        # Inject A2E-specific noise / boring negatives (≈5%) *before* final normalization
        tokens, tags = self._inject_noise_and_boring_negatives(tokens, tags)

        # Header string normalized by your external function
        n = AddressNormalizer()
        raw = n.normalize_punctuation_only(" ".join(tokens))
        return raw, tokens, tags



# --------------------------------- Writer / API --------------------------------- #

def to_conll(samples, path: str, group_label: str = "A2E") -> None:
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for raw, toks, tags in samples:
            rid = random.randint(10000, 99999)
            header = f"{raw}, {rid}, {group_label}"
            f.write(header + "\n")
            for t, y in zip(toks, tags):
                f.write(f"{t}\t{y}\n")
            f.write("\n")


def generate_group_A2E_dataset(n: int, seed: int = 42):
    random.seed(seed)
    gen = GroupA2EGenerator(seed=seed)
    return [gen.generate_one() for _ in range(n)]
