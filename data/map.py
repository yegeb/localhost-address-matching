import pandas as pd
from typing import Any, Dict, Iterable, Union, Optional
from collections import defaultdict

Col = Union[int, str]

def _tree():
    return defaultdict(_tree)

def _to_dict(d):
    if isinstance(d, defaultdict):
        return {k: _to_dict(v) for k, v in d.items()}
    return d

class Turkey:
    """
    Builds a nested hashmap:
        City (key) -> District (key) -> Neighbourhood (key) -> {}
    """

    def __init__(self,
                 df: pd.DataFrame):
        self.city_col = 0
        self.district_col = 1
        self.neigh_col = 3
        self._data = _tree()  # Construct tree
        self._build(df)  # Build the tree

    def _build(self, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            city = str(row[self.city_col]).strip()
            district = str(row[self.district_col]).strip()
            neigh = str(row[self.neigh_col]).strip()
            if not city or not district or not neigh:
                continue
            # Ensure city → district → neighbourhood exists (leaf is a dict too)
            _ = self._data[city][district][neigh]

    # ---------- Queries / utilities ----------
    def to_dict(self) -> Dict[str, Dict[str, Dict[str, dict]]]:
        """Return a plain dict (no defaultdicts) for export or printing."""
        return _to_dict(self._data)

    def get_city(self, city: str) -> Dict[str, Dict[str, dict]]:
        """District→Neighbourhoods dict for a city (empty if not found)."""
        return self.to_dict().get(city, {})

    def cities(self) -> Iterable[str]:
        return self._data.keys()

    def districts_of(self, city: str) -> Iterable[str]:
        return self._data.get(city, {}).keys()

    def neighbourhoods_of(self, city: str, district: Optional[str] = None) -> Iterable[str]:
        if district is None:
            # Get all neighbourhoods across all districts in the city
            neighbourhoods = []
            for dct in self._data.get(city, {}).values():
                neighbourhoods.extend(dct.keys())
            return neighbourhoods
        else:
            # Get only neighbourhoods of the given district
            return self._data.get(city, {}).get(district, {}).keys()

    def district_count(self, city: str) -> int:
        return len(self._data.get(city, {}))

    def neighbourhood_count(self, city: str) -> int:
        return sum(len(dct) for dct in self._data.get(city, {}).values())

    def print_tree(self, city: Optional[str] = None) -> None:
        """Pretty-print the whole tree or a single city."""

        def _print(d: Dict[str, Any], indent=0):
            for k, v in d.items():
                print("  " * indent + f"- {k}")
                if isinstance(v, dict):
                    _print(v, indent + 1)

        if city is None:
            _print(self.to_dict())
        else:
            _print(self.get_city(city))

    def duplicate_districts_across_cities(self) -> Dict[str, list]:
        """
        Return {district: [city1, city2, ...]} for districts appearing in >1 city.
        """
        mapping: Dict[str, set] = defaultdict(set)
        for city, districts in self._data.items():
            for district in districts.keys():
                mapping[district].add(city)
        return {d: sorted(list(cities)) for d, cities in mapping.items() if len(cities) > 1}

    # Optional: add rows programmatically
    def add(self, city: str, district: str, neighbourhood: str) -> None:
        city, district, neighbourhood = city.strip(), district.strip(), neighbourhood.strip()
        if city and district and neighbourhood:
            _ = self._data[city][district][neighbourhood]


file = "turkiye_posta_kodlari.xlsx"
df = pd.read_excel(file, header=None)
turkey = Turkey(df)

print(turkey.neighbourhoods_of("İSTANBUL")[0])
