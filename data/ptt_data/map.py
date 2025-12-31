# -*- coding: utf-8 -*-
"""
map.py
------
Builds a normalized, cached nested hashmap from PTT's Excel:
    province -> district -> neighbourhood -> {}

Also exposes fast lookup indices:
    - district_index[(province, district)] -> set(neighbourhoods)
    - district_union[district] -> { province: set(neighbourhoods), ... }

Extras:
    - Subset view helpers (İzmir, Aydın, Manisa, Muğla, Denizli by default)
    - TurkeySubset: read-only view over any province subset with the same API
"""

from __future__ import annotations

import os
import pickle
import hashlib
from collections import defaultdict
from typing import Any, Dict, Iterable, Optional, Tuple, Union, List

import pandas as pd

# Ensure project root is on sys.path so 'src' is importable
import sys
from pathlib import Path
HERE = Path(__file__).resolve()
ROOT = next((p for p in HERE.parents if (p / "src").exists() and (p / "data").exists()), None)
if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.address_matching import AddressNormalizer


# ----------------------------- Default subset provinces ----------------------------- #
# Human (canonical) names; normalized internally wherever needed.
FIVE_PROVINCES: Tuple[str, ...] = ("İzmir", "Aydın", "Manisa", "Muğla", "Denizli")


# ----------------------------- internal tree helpers ----------------------------- #
def _tree():
    return defaultdict(_tree)

def _to_dict(d):
    """Convert nested defaultdicts to plain dicts (recursively)."""
    if isinstance(d, defaultdict):
        return {k: _to_dict(v) for k, v in d.items()}
    return d

def _from_plain_dict(d: Dict[str, Any]) -> defaultdict:
    """
    Convert a plain nested dict (province->district->neighbourhood->{})
    back into our nested defaultdict(_tree) structure.
    """
    root = _tree()
    for k, v in d.items():
        if isinstance(v, dict):
            root[k] = _from_plain_dict(v)
        else:
            # Leaves should be dicts; just assign directly
            root[k] = v
    return root


# ========================================================================================= #
#                                         Turkey                                            #
# ========================================================================================= #

class Turkey:
    """
    Builds a normalized, cached nested hashmap:
        province -> district -> neighbourhood -> {}

    Also exposes:
        - district_index[(province, district)] -> set(neighbourhoods)
        - district_union[district] -> { province: set(neighbourhoods), ... }  (for district-only queries)
    """

    # column indices in XLSX
    province_col: int = 0
    district_col: int = 1
    neigh_col: int = 3

    # version hint for cache invalidation if logic changes
    _NORM_HINT = "turkey_tree:v2-normalized-keys-strip-standalone-mah"

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self._normalizer = AddressNormalizer()
        self._data = _tree()  # province -> district -> neighbourhood -> {}
        # Fast lookup indices
        self.district_index: Dict[Tuple[str, str], set] = {}
        self.district_union: Dict[str, Dict[str, set]] = {}
        if df is not None:
            self._build(df)

    # ------------------------- Public constructors -------------------------

    @classmethod
    def load(cls,
             xlsx_path: Union[str, os.PathLike],
             *,
             use_cache: bool = True,
             cache_path: Optional[Union[str, os.PathLike]] = None) -> "Turkey":
        """
        Load from XLSX with a pickle checkpoint for speed.
        Always skips the first row (header).
        """
        xlsx_path = str(xlsx_path)
        cache_path = str(cache_path) if cache_path is not None else (xlsx_path + ".tree.pkl")

        if use_cache and cls._cache_valid(xlsx_path, cache_path):
            return cls._load_cache(cache_path)

        # Read and drop header row
        df = pd.read_excel(xlsx_path, header=None)
        if len(df) > 0:
            df = df.iloc[1:].reset_index(drop=True)

        inst = cls(df)
        if use_cache:
            inst._write_cache(xlsx_path, cache_path)
        return inst

    # ------------------------------ Build ---------------------------------

    def _build(self, df: pd.DataFrame) -> None:
        N = self._normalize_static
        strip = self._strip_standalone_mah

        # Build nested tree and indices
        for _, row in df.iterrows():
            prov_raw = str(row[self.province_col]).strip()
            dist_raw = str(row[self.district_col]).strip()
            neigh_raw = str(row[self.neigh_col]).strip()
            if not prov_raw or not dist_raw or not neigh_raw:
                continue

            p = N(prov_raw)
            d = N(dist_raw)
            n = strip(N(neigh_raw))
            if not n:
                continue

            # province → district → neighbourhood → {}
            _ = self._data[p][d][n]  # create path

            # district index keyed by (province, district)
            key = (p, d)
            self.district_index.setdefault(key, set()).add(n)

            # district union index keyed by plain district
            self.district_union.setdefault(d, {}).setdefault(p, set()).add(n)

    # ------------------------------ Cache ---------------------------------

    @staticmethod
    def _xlsx_signature(xlsx_path: str) -> Dict[str, Any]:
        stat = os.stat(xlsx_path)
        sha = hashlib.sha256()
        with open(xlsx_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                sha.update(chunk)
        return {"path": os.path.abspath(xlsx_path), "size": stat.st_size, "sha256": sha.hexdigest()}

    @classmethod
    def _cache_valid(cls, xlsx_path: str, cache_path: str) -> bool:
        if not (os.path.exists(xlsx_path) and os.path.exists(cache_path)):
            return False
        try:
            with open(cache_path, "rb") as f:
                blob = pickle.load(f)
            return blob.get("signature") == cls._xlsx_signature(xlsx_path) and blob.get("norm_hint") == cls._NORM_HINT
        except Exception:
            return False

    @classmethod
    def _load_cache(cls, cache_path: str) -> "Turkey":
        with open(cache_path, "rb") as f:
            blob = pickle.load(f)
        inst = cls(df=None)
        # Reconstruct the nested defaultdict structure from the stored plain dict
        inst._data = _from_plain_dict(blob["data"]["tree"])
        inst.district_index = blob["data"]["district_index"]
        inst.district_union = blob["data"]["district_union"]
        return inst

    def _write_cache(self, xlsx_path: str, cache_path: str) -> None:
        blob = {
            "signature": self._xlsx_signature(xlsx_path),
            "norm_hint": self._NORM_HINT,
            "data": {
                "tree": self.to_dict(),  # store as plain dict
                "district_index": self.district_index,
                "district_union": self.district_union,
            },
        }
        tmp = cache_path + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(blob, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, cache_path)

    # ----------------------------- Normalizers -----------------------------

    def _normalize_static(self, s: str) -> str:
        # Same folding as your static parser for key alignment
        return self._normalizer.normalize_static_parser(s)

    @staticmethod
    def _strip_standalone_mah(s: str) -> str:
        # Remove standalone 'mah' token only (keeps 'mahalle', 'mahallesi', etc.)
        toks = [t for t in s.split() if t != "mah"]
        return " ".join(toks)

    # ---------------------------- Public queries ---------------------------

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, dict]]]:
        """Return a plain dict (no defaultdicts) for export or printing."""
        return _to_dict(self._data)

    # Provinces
    def provinces(self) -> Iterable[str]:
        return self._data.keys()

    def get_province(self, province: str) -> Dict[str, Dict[str, dict]]:
        """District→Neighbourhoods dict for a province (empty if not found)."""
        return self.to_dict().get(self._normalize_static(province), {})

    # Districts
    def districts_of(self, province: str) -> Iterable[str]:
        return self._data.get(self._normalize_static(province), {}).keys()

    # Neighbourhoods (flexible)
    def neighbourhoods_of(self,
                          province: Optional[str] = None,
                          district: Optional[str] = None) -> List[str]:
        """
        - province & district: neighbourhoods of that pair
        - province only: all neighbourhoods across districts in province
        - district only: union of neighbourhoods across all provinces for that district
        - none: all neighbourhoods countrywide
        """
        if province and district:
            p = self._normalize_static(province)
            d = self._normalize_static(district)
            return sorted(self.district_index.get((p, d), set()))
        elif province and not district:
            p = self._normalize_static(province)
            out = []
            for dct in self._data.get(p, {}).values():
                out.extend(dct.keys())
            return sorted(set(out))
        elif district and not province:
            d = self._normalize_static(district)
            prov_map = self.district_union.get(d, {})
            out = set()
            for nset in prov_map.values():
                out.update(nset)
            return sorted(out)
        else:
            # neither provided → all neighbourhoods in TR (flattened)
            out = set()
            for p, dmap in self._data.items():
                for nmap in dmap.values():
                    out.update(nmap.keys())
            return sorted(out)

    # Stats / reports
    def district_count(self, province: str) -> int:
        p = self._normalize_static(province)
        return len(self._data.get(p, {}))

    def neighbourhood_count(self, province: str) -> int:
        p = self._normalize_static(province)
        return sum(len(dct) for dct in self._data.get(p, {}).values())

    def duplicate_districts_across_provinces(self) -> Dict[str, List[str]]:
        """
        Return {district: [prov1, prov2, ...]} for districts appearing in >1 province.
        """
        return {
            d: sorted(list(prov_map.keys()))
            for d, prov_map in self.district_union.items()
            if len(prov_map) > 1
        }

    def print_tree(self, province: Optional[str] = None) -> None:
        """Pretty-print the whole tree or a single province."""
        def _print(d: Dict[str, Any], indent=0):
            for k, v in d.items():
                print("  " * indent + f"- {k}")
                if isinstance(v, dict):
                    _print(v, indent + 1)

        if province is None:
            _print(self.to_dict())
        else:
            _print(self.get_province(province))

    # Optional: programmatic add
    def add(self, province: str, district: str, neighbourhood: str) -> None:
        p = self._normalize_static(province).strip()
        d = self._normalize_static(district).strip()
        n = self._strip_standalone_mah(self._normalize_static(neighbourhood)).strip()
        if p & d & n:
            _ = self._data[p][d][n]  # defaultdict ensures creation
            self.district_index.setdefault((p, d), set()).add(n)
            self.district_union.setdefault(d, {}).setdefault(p, set()).add(n)

    # ---------------------------- Subset helpers (view) ----------------------------

    def subset_view(self, provinces: Iterable[str] = None) -> "TurkeySubset":
        """
        Build a TurkeySubset view limited to the given provinces.
        Names may be human-form; they are normalized internally.
        """
        provinces = provinces or FIVE_PROVINCES
        wanted = { self._normalize_static(p) for p in provinces }
        full = self.to_dict()  # plain dict with normalized keys
        tree = { p: dmap for p, dmap in full.items() if p in wanted }
        return TurkeySubset(tree, self._normalizer)

    @classmethod
    def load_subset_view(cls,
                         xlsx_path: Union[str, os.PathLike],
                         provinces: Iterable[str] = None,
                         *,
                         use_cache: bool = True,
                         cache_path: Optional[Union[str, os.PathLike]] = None) -> "TurkeySubset":
        """
        One-shot loader that returns a TurkeySubset view limited to the given provinces.
        """
        inst = cls.load(xlsx_path, use_cache=use_cache, cache_path=cache_path)
        return inst.subset_view(provinces or FIVE_PROVINCES)


# ========================================================================================= #
#                                       TurkeySubset                                        #
# ========================================================================================= #

class TurkeySubset:
    """
    Read-only view over a subset: province -> district -> neighbourhood -> {}
    Mirrors the Turkey query API (provinces, districts_of, neighbourhoods_of, etc.),
    but restricted to the given provinces.
    """
    def __init__(self, tree: Dict[str, Dict[str, Dict[str, dict]]], normalizer: AddressNormalizer):
        # tree must already be a plain dict with normalized keys
        self._normalizer = normalizer
        self._data = tree
        # Build fast indices for the subset
        self.district_index: Dict[Tuple[str, str], set] = {}
        self.district_union: Dict[str, Dict[str, set]] = {}
        self._build_indices()

    def _build_indices(self) -> None:
        for p, dmap in self._data.items():
            for d, nmap in dmap.items():
                if not isinstance(nmap, dict):
                    continue
                nset = set(nmap.keys())
                if not nset:
                    continue
                self.district_index.setdefault((p, d), set()).update(nset)
                self.district_union.setdefault(d, {}).setdefault(p, set()).update(nset)

    # -------- Normalizers --------
    def _normalize_static(self, s: str) -> str:
        return self._normalizer.normalize_static_parser(s)

    # -------- Exports / queries (same shape as Turkey) --------
    def to_dict(self) -> Dict[str, Dict[str, Dict[str, dict]]]:
        return self._data

    def provinces(self) -> Iterable[str]:
        return self._data.keys()

    def get_province(self, province: str) -> Dict[str, Dict[str, dict]]:
        return self._data.get(self._normalize_static(province), {})

    def districts_of(self, province: str) -> Iterable[str]:
        return self._data.get(self._normalize_static(province), {}).keys()

    def neighbourhoods_of(self,
                          province: Optional[str] = None,
                          district: Optional[str] = None) -> List[str]:
        if province and district:
            p = self._normalize_static(province)
            d = self._normalize_static(district)
            return sorted(self.district_index.get((p, d), set()))
        elif province and not district:
            p = self._normalize_static(province)
            out = []
            for dct in self._data.get(p, {}).values():
                out.extend(dct.keys())
            return sorted(set(out))
        elif district and not province:
            d = self._normalize_static(district)
            prov_map = self.district_union.get(d, {})
            out = set()
            for nset in prov_map.values():
                out.update(nset)
            return sorted(out)
        else:
            out = set()
            for p, dmap in self._data.items():
                for nmap in dmap.values():
                    out.update(nmap.keys())
            return sorted(out)

    # Stats
    def district_count(self, province: str) -> int:
        p = self._normalize_static(province)
        return len(self._data.get(p, {}))

    def neighbourhood_count(self, province: str) -> int:
        p = self._normalize_static(province)
        return sum(len(dct) for dct in self._data.get(p, {}).values())

    def duplicate_districts_across_provinces(self) -> Dict[str, List[str]]:
        return {
            d: sorted(list(prov_map.keys()))
            for d, prov_map in self.district_union.items()
            if len(prov_map) > 1
        }

    def print_tree(self, province: Optional[str] = None) -> None:
        def _print(d: Dict[str, Any], indent=0):
            for k, v in d.items():
                print("  " * indent + f"- {k}")
                if isinstance(v, dict):
                    _print(v, indent + 1)
        if province is None:
            _print(self._data)
        else:
            _print(self.get_province(province))


# ------------------------------- CLI / demo --------------------------------

if __name__ == "__main__":
    XLSX = Path(__file__).resolve().parent / "turkiye_posta_kodlari.xlsx"
    tr = Turkey.load(str(XLSX))  # cached

    print("Provinces (TR):", len(list(tr.provinces())))
    print("Istanbul districts:", len(list(tr.districts_of("İstanbul"))))
    print("Ataşehir neighbourhoods (İstanbul/Ataşehir):",
          len(tr.neighbourhoods_of(province="İstanbul", district="Ataşehir")))

    # Five-province subset VIEW with the same API
    sub = tr.subset_view()  # defaults to FIVE_PROVINCES
    print("\n[Subset view] Province count:", len(list(sub.provinces())))
    print("[Subset view] İzmir district count:", sub.district_count("İzmir"))
    print("[Subset view] Bornova neighbourhoods:",
          len(sub.neighbourhoods_of(province="İzmir", district="Bornova")))
    # District-only union search is now limited to the subset:
    print("[Subset view] 'Atatürk' union across subset provinces:",
          len(sub.neighbourhoods_of(district="Atatürk")))
