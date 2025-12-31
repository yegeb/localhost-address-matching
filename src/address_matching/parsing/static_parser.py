import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List, Set, Any

import sys
from pathlib import Path

# static_parser.py lives at .../src/address_matching/parsing/static_parser.py
# Put project root (that has both 'src' and 'data') on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# Import runtime tree + normalizer
from data.ptt_data.map import Turkey
from src.address_matching import AddressNormalizer

# Load the XLSX via an absolute path (works regardless of CWD); Turkey caches via pkl
XLSX = PROJECT_ROOT / "data" / "ptt_data" / "turkiye_posta_kodlari.xlsx"
TR = Turkey.load(str(XLSX))

# Normalizer instance
n = AddressNormalizer()

# ---------------------------- Data Structures ---------------------------- #

@dataclass
class Address:
    def __init__(self, province, district, neighbourhood, label):
        self.province = province
        self.district = district
        self.neighbourhood = neighbourhood
        self.label = label

# ---------------------------- Static Parser ----------------------------- #

class StaticAddressParser:
    """
    Deterministic (non-ML) parser that finds province → district → neighbourhood
    using ONLY the names provided by the Turkey tree (data/ptt_data/map.py).
    All names are assumed to be pre-normalized with AddressNormalizer.normalize_static_parser.

    Matching happens on *plain* names from the Turkey tree.
    """

    # Kept for compatibility; NOT used to filter tokens.
    INDICATOR_TOKENS: Set[str] = {"mah", "cad", "sk"}

    def __init__(self):
        # token indices (first_token -> [(token_list, full_name)])
        self._prov_index: Dict[str, List[Tuple[List[str], str]]] = {}
        self._dist_index: Dict[str, List[Tuple[List[str], str]]] = {}
        self._nbhd_index: Dict[str, List[Tuple[List[str], str]]] = {}
        self._build_indices()

    # ------------------------- Public API ------------------------- #

    def parse(self, address_text: str) -> Address:
        # Normalize and tokenize (keep ALL tokens)
        norm = n.normalize_static_parser(address_text)
        tokens = norm.split()

        # Province
        match_prov = self._best_match(tokens, self._prov_index, allowed_names=None)
        prov_norm = match_prov[0] if match_prov else None

        # District (restricted by province if known)
        allowed_districts: Optional[Set[str]] = None
        if prov_norm:
            allowed_districts = set(self._districts_of(prov_norm))

        match_dist = self._best_match(tokens, self._dist_index, allowed_names=allowed_districts)
        dist_norm = match_dist[0] if match_dist else None

        # Infer province from district if needed (may be ambiguous; we pick the first)
        if not prov_norm and dist_norm:
            prov_norm = self._some_province_of_district(dist_norm)

        # Neighbourhood allowed set
        allowed_nbhds: Optional[Set[str]] = None
        if dist_norm:
            if prov_norm:
                # Known (province, district) → restrict to that pair
                allowed_nbhds = set(TR.neighbourhoods_of(province=prov_norm, district=dist_norm))
            else:
                # Province unknown → union across all provinces that contain this district
                allowed_nbhds = set(TR.neighbourhoods_of(district=dist_norm))

        match_nbhd = self._best_match(tokens, self._nbhd_index, allowed_names=allowed_nbhds)
        nbhd_norm = match_nbhd[0] if match_nbhd else None

        return Address(
            province=prov_norm,
            district=dist_norm,
            neighbourhood=nbhd_norm,
            label=address_text
        )

    # ----------------------- Internal: Build ----------------------- #

    def _build_indices(self) -> None:
        # Province names (plain, already normalized by Turkey)
        prov_names: Set[str] = set(TR.provinces())

        # District names (plain) — union over all provinces
        dist_names: Set[str] = set()
        for p in prov_names:
            dist_names.update(TR.districts_of(p))

        # Neighbourhood names (plain) — all in Turkey
        nbhd_names: Set[str] = set(TR.neighbourhoods_of())

        # Build token indices (assumes keys already normalized)
        self._prov_index = self._build_token_index(prov_names)
        self._dist_index = self._build_token_index(dist_names)
        self._nbhd_index = self._build_token_index(nbhd_names)

    # ----------------------- Internal: Search ---------------------- #

    def _best_match(
        self,
        tokens: List[str],
        index: Dict[str, List[Tuple[List[str], str]]],
        allowed_names: Optional[Set[str]] = None
    ) -> Optional[Tuple[str, int, int]]:
        """
        Returns (name, start_idx, end_idx) for the single best match.
        Ranking: longest match (by token length), then earliest position.
        """
        best = None
        best_payload = None
        T = len(tokens)

        for i in range(T):
            first = tokens[i]
            for cand_tokens, name in index.get(first, []):
                if allowed_names is not None and name not in allowed_names:
                    continue
                L = len(cand_tokens)
                if i + L > T:
                    continue
                if tokens[i:i+L] == cand_tokens:
                    rank_key = (L, -i)
                    if best is None or rank_key > best:
                        best = rank_key
                        best_payload = (name, i, i + L)
        return best_payload

    def _build_token_index(self, names: Set[str]) -> Dict[str, List[Tuple[List[str], str]]]:
        """
        Build (first-token) → [(token_list, full_name)] index for faster scanning.
        Assumes input names are already normalized with the same rules as the parser.
        """
        idx: Dict[str, List[Tuple[List[str], str]]] = {}
        for name in names:
            toks = name.split()
            if not toks:
                continue
            idx.setdefault(toks[0], []).append((toks, name))
        for lst in idx.values():
            lst.sort(key=lambda x: len(x[0]), reverse=True)
        return idx

    # ----------------------- Internal: Lookups --------------------- #

    @staticmethod
    def _districts_of(province: str) -> List[str]:
        """District list for a province (plain names)."""
        return list(TR.districts_of(province)) if province else []

    @staticmethod
    def _some_province_of_district(district: str) -> Optional[str]:
        """
        Return one province that contains the given district.
        If multiple provinces share the district name, returns the first encountered.
        """
        for p in TR.provinces():
            if district in TR.districts_of(p):
                return p
        return None
