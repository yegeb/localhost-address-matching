from dataclasses import dataclass
from typing import List

# (You can keep SITE/BLOK/APARTMAN/BULVAR/DAIRE templates here or in general_config)
SITE_TEMPLATES: List[str] = [
    "{name} evleri", "{name} sitesi", "{name} site",
    "{name} rezidans", "{name} residence", "{name} tower",
    "{name} plaza", "{name} konutları",
]
BLOK_TEMPLATES: List[str] = ["{label} blok", "{label} bloğu", "blok: {label}"]
APARTMAN_TEMPLATES: List[str] = ["{name} apartmanı", "{name} apt", "{name} apart", "{name} apartman"]
BULVAR_TEMPLATES: List[str] = ["{name} bulvarı", "{name} bulv", "{name} bulvar"]
DAIRE_NO_TEMPLATES: List[str] = ["daire {no}", "daire: {no}", "d: {no}", "no: {no}", "no {no}"]

@dataclass
class SynthesisConfigF2J:
    """
    F→J synthesis config with:
      • Original site/bina/daire/bulvar rules.
      • Global admin diversity for non-TARIF (PD/NDP/ONLY-ONE/none + optional PD duplication).
      • TARIF branch:
          - Optional PD or NDP (front/end placement).
          - Optional duplication of that admin block.
          - **NEW:** Optional duplication of the *entire TARIF address*.
          - TARIF lines contain nothing else (no site/bina/daire/bulvar).
    """

    # ---------------- Address "body" (non-TARIF) ----------------
    p_has_site: float = 0.75
    p_bina_blok_given_site: float = 0.85
    p_bina_apartman_given_no_site: float = 0.95
    p_has_daire_no_given_bina: float = 0.90
    p_has_bulvar_given_no_site: float = 0.15

    # ---------------- Admin (non-TARIF) ----------------
    apply_admin_rules_only_if_body_present: bool = False
    p_admin_pd: float = 0.20
    p_admin_ndp: float = 0.75
    p_admin_only_one: float = 0.05
    p_uppercase_for_ndp: float = 0.50
    p_ndp_use_slashes_when_not_upper: float = 0.50
    p_admin_pd_duplicate: float = 0.70
    p_pd_dup_to_front_prob: float = 0.60

    # ---------------- TARIF branch ----------------
    p_tarif: float = 0.50
    p_tarif_has_pd: float = 0.80
    p_tarif_ndp_given_pd: float = 0.90
    p_tarif_pd_front_prob: float = 0.50
    p_tarif_ndp_use_slashes: float = 0.70

    # TARIF admin duplication
    p_tarif_admin_duplicate: float = 0.55
    p_tarif_dup_to_front_prob: float = 0.50

    # NEW: duplicate the *entire* TARIF address (tokens + tags) once
    p_tarif_duplicate_whole: float = 0.02

    # Optional noise
    allow_blok_and_apartman_together: bool = True
    p_random_uppercase: float = 0.05
    p_random_extra_spaces: float = 0.00
    p_random_colon_variants: float = 0.05

    # --- Noise / boring negatives (F2J only for now) ---
    p_noise_boring_negatives: float = 0.20  # 5% of F2J samples

    # Which separators to inject and the minimum count per noisy sample
    noise_separators: tuple = ("-", "/")
    min_noise_separators: int = 4

    # What to append at the very end of the sentence
    noise_country_tokens: tuple = ("tr", "TR", "Türkiye", "TÜRKİYE")


__all__ = [
    "SynthesisConfigF2J",
    "SITE_TEMPLATES", "BLOK_TEMPLATES", "APARTMAN_TEMPLATES",
    "BULVAR_TEMPLATES", "DAIRE_NO_TEMPLATES",
]
