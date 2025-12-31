from dataclasses import dataclass

@dataclass
class SynthesisConfigA2E:
    # ======= Global formatting =======
    # In 5% of samples, uppercase every word token.
    p_all_uppercase: float = 0.05

    # ======= Structure probabilities =======
    # Neighborhood repetition
    p_repeat_neighborhood: float = 0.15

    # Avenue/Street presence
    p_both_avenue_street: float = 0.45
    p_only_avenue: float = 0.20
    p_only_street: float = 0.20

    # Building/Flat presence
    p_both_building_flat: float = 0.30
    p_only_building: float = 0.35
    p_only_flat: float = 0.15

    # Colon usage after keyword tokens like "no", "daire", "kat"
    p_colon_after_numbers: float = 0.55

    # Admin formatting
    p_slash_between_admin: float = 0.45     # include "/" between district & province
    p_district_first: float = 0.65          # district before province (else province before district)

    # Duplicate admin at start (keep same slash/order as end)
    p_prepend_admin_again: float = 0.20

    # When the above triggers, 40% prepend NEIGHBORHOOD first: "Neighborhood / District / Province ..."
    p_prepend_with_neighborhood: float = 0.40

    # Shuffle order among [neighborhood-block(s), avenue?, street?]
    p_shuffle_segments: float = 0.20

    # If both flat & building exist, put FLAT before BUILDING
    p_swap_flat_before_building_when_both: float = 0.15

    # Sometimes NEIGHBORHOOD appears without the keyword ("mah./mh./mahallesi")
    p_neighborhood_bare: float = 0.25

    # If bare neighborhood is used, 65% uppercase
    p_bare_neighborhood_uppercase: float = 0.65

    # Include floor info (KAT) like "3. kat", "kat: 3", "k: 3", "kat 3"
    p_include_floor: float = 0.25

    # Include POSTA_KODU just before the (ending) admin pair
    p_postcode_before_admin: float = 0.10

    # --- Cosmetics ---
    p_uppercase_admin: float = 0.15
    p_uppercase_neighborhood: float = 0.05

    # --- Noise / boring negatives (A2E only for now) ---
    p_noise_boring_negatives: float = 0.05  # 5% of A2E samples

    # Which separators to inject and the minimum count per noisy sample
    noise_separators: tuple = ("-", "/")
    min_noise_separators: int = 3

    # What to append at the very end of the sentence
    noise_country_tokens: tuple = ("tr", "TR", "Türkiye", "TÜRKİYE")


__all__ = ["SynthesisConfigA2E"]
