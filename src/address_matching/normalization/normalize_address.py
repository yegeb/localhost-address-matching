import re
import unicodedata
from dataclasses import dataclass, field
from typing import Pattern, List, Tuple

@dataclass
class AddressNormalizer:
    """
    Idempotently normalizes address texts.

    Pipeline (normalize):
      1) Unicode NFKC
      2) Punctuation normalization:
         - remove '.' and ','
         - split ALL other punctuation as separate tokens (space-delimited)
      3) Turkish-aware lowercase
      4) Normalize indicators:
         mahalle -> 'mah', cadde -> 'cad', sokak -> 'sk'
      5) Apply extra user rules
      6) Collapse spaces

    Example:
        normalizer = AddressNormalizer()
        out = normalizer.normalize("Atatürk Mahallesi 123. Sok No:5")
        # -> "atatürk mah 123 sk no : 5"
    """

    # Canonical abbreviations in output
    canon_nbhd:    str = "mah"
    canon_avenue:  str = "cad"
    canon_street:  str = "sk"

    # Alphanumeric class including Turkish letters (for boundary checks)
    tr_alnum: str = r"A-Za-zÇĞİÖŞÜçğıöşü0-9"

    # Alphabetic class (no digits) for number-splitting boundaries
    tr_alpha: str = r"A-Za-zÇĞİÖŞÜçğıöşü"

    # Compiled patterns (held as attributes)
    re_nbhd:   Pattern = field(init=False)
    re_avenue: Pattern = field(init=False)
    re_street: Pattern = field(init=False)

    # Number split patterns
    re_num_split_ld: Pattern = field(init=False)  # letter -> digit boundary
    re_num_split_dl: Pattern = field(init=False)  # digit -> letter boundary

    # Optional extra rules as a list of (Pattern, replacement)
    extra_rules: List[Tuple[Pattern, str]] = field(default_factory=list)

    # ----------------------- Initialization -----------------------
    def __post_init__(self):
        """Compile required regex patterns when the class is instantiated."""
        # Neighborhood (mahalle → mah)
        self.re_nbhd = re.compile(
            rf"""
            (?<![{self.tr_alnum}])                              # left boundary
            (
                mahal{{1,3}}e[\s\._\-]*s{{1,2}}[iı](?=$|[\s,;:/\-\._]) |
                mahal{{1,3}}es{{1,2}}[iı](?=$|[\s,;:/\-\._])           |
                mahal{{1,3}}e(?=$|[\s,;:/\-\._])                       |
                mah(?=\.|\b|[:/.\-_])                                  |
                mh(?=\.|\b|[:/.\-_])                                   |
                mhl(?=\.|\b|[:/.\-_])                                  |
                mahl(?=\.|\b|[:/.\-_])                                 |
                mahal(?=$|[\s,;:/\-\._])
            )
            """,
            re.IGNORECASE | re.VERBOSE
        )

        # Avenue (cadde → cad)
        self.re_avenue = re.compile(
            rf"""
            (?<![{self.tr_alnum}])                              # left boundary
            (
                cad{{1,3}}e[\s\._\-]*s{{1,2}}[iı](?=$|[\s,;:/\-\._]) |
                cad{{1,3}}es{{1,2}}[iı](?=$|[\s,;:/\-\._])           |
                cad{{1,3}}e(?=$|[\s,;:/\-\._])                       |
                cad(?=\.|\b|[:/.\-_])                                |
                cd(?=\.|\b|[:/.\-_])                                 |
                cadd(?=\.|\b|[:/.\-_])                               |
                cadde(?=$|[\s,;:/\-\._])
            )
            """,
            re.IGNORECASE | re.VERBOSE
        )

        # Street (sokak → sk)
        self.re_street = re.compile(
            rf"""
            (?<![{self.tr_alnum}])                              # left boundary
            (
                sokağı(?:n|nın|nda|na)?(?=$|[\s,;:/\-\._])    |
                soka[ğg][aeıiuüi](?=$|[\s,;:/\-\._])          |
                soka[ğg](?=$|[\s,;:/\-\._])                   |
                sok{{1,2}}ak(?=$|[\s,;:/\-\._])               |
                sokak(?:lar[ıi]?)?(?=$|[\s,;:/\-\._])         |
                sk(?=\.|\b|[:/.\-_])                          |
                sok(?=\.|\b|[:/.\-_])
            )
            """,
            re.IGNORECASE | re.VERBOSE
        )

        # Number boundaries (letters <-> digits)
        self.re_num_split_ld = re.compile(rf"([{self.tr_alpha}])(?=\d)")
        self.re_num_split_dl = re.compile(rf"(\d)(?=[{self.tr_alpha}])")


    # --------------------- Helpers ---------------------
    @staticmethod
    def tr_lower(s: str) -> str:
        """Turkish-aware lowercase conversion (handles İ/i and I/ı)."""
        return s.replace("İ", "i").replace("I", "ı").lower()

    @staticmethod
    def _space_punct_soften(text: str) -> str:
        """
        Soften spacing around common punctuation: leave a single space.
        Two-phase: isolate punctuation, then collapse multiple spaces.
        """
        s = re.sub(r"\s+", " ", text)
        s = re.sub(r"\s*([,;:/\-\._])\s*", r" \1 ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @staticmethod
    def pre_normalize(text: str) -> str:
        """
        Unicode normalization (NFKC) + whitespace/punctuation smoothing.
        Designed to be idempotent; re-running does not change the output.
        """
        s = unicodedata.normalize("NFKC", text)
        s = AddressNormalizer._space_punct_soften(s)
        return s
    
    # ---------------- Punctuation Normalization ----------------
    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """
        Normalize ALL punctuation:
          - Remove '.' and ',' completely (replace with space)
          - For any other Unicode punctuation (category starts with 'P'),
            surround with spaces so they become separate tokens.
          - Collapse multiple spaces and trim.

        Examples:
          "No:49/13"    -> "No : 49 / 13"
          "1445.sokak"  -> "1445 sokak"
          "Aydın, Didim"-> "Aydın Didim"
          "Turgutreis-bodrum" -> "Turgutreis - bodrum"
          "D.7"         -> "D 7"
        """
        out_chars = []
        for ch in text:
            cat = unicodedata.category(ch)
            if cat.startswith('P'):  # any punctuation
                if ch in {'.', ','}:
                    # drop '.' and ',' by replacing with a space
                    out_chars.append(' ')
                else:
                    # keep all other punctuation as separate tokens
                    out_chars.append(' ')
                    out_chars.append(ch)
                    out_chars.append(' ')
            else:
                out_chars.append(ch)

        s = ''.join(out_chars)
        # Normalize all whitespace to single spaces
        s = re.sub(r'\s+', ' ', s).strip()
        return s
    
    # ---------------- Number Normalization ----------------
    def normalize_numbers(self, text: str) -> str:
        """
        Insert spaces at letter/digit boundaries:
          - 'izmir2'    -> 'izmir 2'
          - '3atatürk'  -> '3 atatürk'
          - '4mustafa5' -> '4 mustafa 5'
          - 'B3Blok'    -> 'B 3 Blok'
        Idempotent: running twice makes no further changes.
        """
        s = self.re_num_split_ld.sub(r"\1 ", text)   # letter→digit
        s = self.re_num_split_dl.sub(r"\1 ", s)      # digit→letter
        return re.sub(r"\s+", " ", s).strip()

    # ----------------- Rule Appliers -----------------
    def normalize_nbhd_token(self, text: str) -> str:
        """
        Convert all variations of the neighborhood indicator to 'mah'.
        Boundary checks avoid touching words like 'Mahmudiye'.
        """
        return self.re_nbhd.sub(self.canon_nbhd, text)
    
    def normalize_avenue_token(self, text: str) -> str:
        """
        Convert all variations of the 'cadde' indicator to 'cad'.
        Boundary checks prevent false matches in words like 'Caddebostan'.
        """
        return self.re_avenue.sub(self.canon_avenue, text)

    def normalize_street_token(self, text: str) -> str:
        """
        Convert all variations of the 'sokak' indicator to 'sk'.
        Boundary checks avoid altering words like 'Sokullu' or 'Sokrates'.
        """
        return self.re_street.sub(self.canon_street, text)

    # -------------------- Main Pipeline -------------------------
    def normalize(self, text: str, lowercase: bool = True) -> str:
        """
        Full normalization pipeline:
          1) Unicode NFKC
          2) Punctuation normalization (drop . , ; split others)
          3) Turkish-aware lowercase
          4) Number normalization (split letters and digits)
          5) 'mahalle' → 'mah'
          6) 'cadde'   → 'cad'
          7) 'sokak'   → 'sk'
          8) Extra rules
          9) Collapse spaces
        """
        s = self.pre_normalize(text)
        s = self.normalize_punctuation(s)
        if lowercase:
            s = self.tr_lower(s)
        s = self.normalize_numbers(s)
        s = self.normalize_nbhd_token(s)
        s = self.normalize_avenue_token(s)
        s = self.normalize_street_token(s)

        for pattern, repl in self.extra_rules:
            s = pattern.sub(repl, s)

        s = re.sub(r"\s+", " ", s).strip()
        return s
    
    # -------------------- Static Parser Variant ------------------
    def normalize_static_parser(self, text: str) -> str:
        """
        Static parser–oriented normalization.

        Steps:
        1) pre_normalize: Unicode NFKC + soft spacing around common punctuation
        2) Punctuation normalization:
            - remove '.' and ',' (replace with space)
            - split ALL other punctuation as separate tokens (surround with spaces)
        3) Turkish-aware lowercase (handles İ/i and I/ı correctly)
        4) Number normalization (insert spaces at letter↔digit boundaries)
        5) Fold letters for ASCII-ish matching: ı→i, ö→o, ü→u
        6) Collapse multiple spaces and trim

        Designed to be idempotent across the above steps.
        """
        s = self.pre_normalize(text)
        s = self.normalize_punctuation(s)
        s = self.tr_lower(s)
        s = self.normalize_numbers(s)
        s = (s.replace("ı", "i")
            .replace("ö", "o")
            .replace("ü", "u")
            .replace("ğ", "g")
            .replace("ş", "s")
            .replace("ç", "c"))
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def normalize_punctuation_only(self, text: str) -> str:
        """
        Punctuation-only normalization pipeline.

        Steps:
        1) Unicode NFKC (no semantic changes)
        2) Punctuation normalization:
            - remove '.' and ',' completely
            - split ALL other Unicode punctuation as separate tokens (surround with spaces)
        3) Number normalization (split letters and digits)
        4) Collapse spaces

        NOTE: Does NOT normalize abbreviations (mah/cad/sk). Idempotent.
        """
        s = self.pre_normalize(text)          # NFKC
        s = self.normalize_punctuation(s)     # drop . , ; split others as tokens
        s = self.normalize_numbers(s)
        s = re.sub(r"\s+", " ", s).strip()
        return s
    
    def idempotent_check(self, text: str) -> bool:
        """
        Idempotence test: normalize(normalize(x)) == normalize(x)?
        """
        once = self.normalize(text)
        twice = self.normalize(once)
        return once == twice
    