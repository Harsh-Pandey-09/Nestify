"""
Rule-based compatibility scoring used when the LLM is unavailable
(timeout, API error, malformed response, missing API key, etc).
Deterministic and cheap so it always succeeds.
"""


def compute_fallback_score(listing_dict: dict, tenant_dict: dict) -> tuple[float, str]:
    rent = float(listing_dict.get("rent", 0))
    budget_min = float(tenant_dict.get("budget_min", 0))
    budget_max = float(tenant_dict.get("budget_max", 0))

    listing_location = str(listing_dict.get("location", "")).strip().lower()
    preferred_location = str(tenant_dict.get("preferred_location", "")).strip().lower()

    # --- Budget scoring (0-50) ---
    if budget_min <= rent <= budget_max:
        budget_score = 50.0
    else:
        # distance outside the range, as a fraction of the budget width (or of rent if range is 0)
        if rent < budget_min:
            diff = budget_min - rent
        else:
            diff = rent - budget_max
        span = max(budget_max - budget_min, budget_max * 0.2, 1.0)
        ratio = diff / span
        budget_score = max(0.0, 50.0 - (ratio * 50.0))

    # --- Location scoring (0-50) ---
    if not listing_location or not preferred_location:
        location_score = 25.0  # unknown -> neutral
    elif listing_location == preferred_location:
        location_score = 50.0
    elif listing_location in preferred_location or preferred_location in listing_location:
        location_score = 35.0  # partial / substring match (e.g. same city, different area)
    else:
        # check for shared words (e.g. "Koramangala, Bangalore" vs "Bangalore")
        listing_words = set(listing_location.replace(",", " ").split())
        preferred_words = set(preferred_location.replace(",", " ").split())
        if listing_words & preferred_words:
            location_score = 30.0
        else:
            location_score = 5.0

    score = round(budget_score + location_score, 2)

    budget_desc = "within" if budget_min <= rent <= budget_max else "outside"
    location_desc = "matches" if location_score >= 45 else ("partially matches" if location_score >= 25 else "does not match")

    explanation = (
        f"Rule-based score: rent ({rent}) is {budget_desc} the tenant's budget range "
        f"({budget_min}-{budget_max}), and listing location '{listing_dict.get('location')}' "
        f"{location_desc} preferred location '{tenant_dict.get('preferred_location')}'."
    )
    return score, explanation
