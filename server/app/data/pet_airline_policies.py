"""IATA allowlist and in-cabin pet policies for pet-friendly flight search."""

PET_FRIENDLY_AIRLINES: frozenset[str] = frozenset(
    {
        "AA",  # American Airlines
        "DL",  # Delta Air Lines
        "UA",  # United Airlines
        "WN",  # Southwest Airlines
        "B6",  # JetBlue
        "AC",  # Air Canada
        "LH",  # Lufthansa
        "KL",  # KLM
        "AF",  # Air France
        "AS",  # Alaska Airlines
    }
)

PET_POLICY: dict[str, dict] = {
    "AA": {
        "airline": "American Airlines",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 9,
        "fee": "$125–$200",
        "currency": "USD",
    },
    "DL": {
        "airline": "Delta Air Lines",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 8,
        "fee": "$150–$200",
        "currency": "USD",
    },
    "UA": {
        "airline": "United Airlines",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 9,
        "fee": "$150/each way",
        "currency": "USD",
    },
    "WN": {
        "airline": "Southwest Airlines",
        "in_cabin": True,
        "cargo": False,
        "max_kg": 9,
        "fee": "$95/each way",
        "currency": "USD",
    },
    "B6": {
        "airline": "JetBlue",
        "in_cabin": True,
        "cargo": False,
        "max_kg": 9,
        "fee": "$125/each way",
        "currency": "USD",
    },
    "AC": {
        "airline": "Air Canada",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 10,
        "fee": "$50–$118/each way",
        "currency": "CAD",
    },
    "LH": {
        "airline": "Lufthansa",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 8,
        "fee": "€55–€200/each way",
        "currency": "EUR",
    },
    "KL": {
        "airline": "KLM",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 8,
        "fee": "€75 (Europe), €400 (intercontinental)",
        "currency": "EUR",
    },
    "AF": {
        "airline": "Air France",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 8,
        "fee": "€70–€400/each way",
        "currency": "EUR",
    },
    "AS": {
        "airline": "Alaska Airlines",
        "in_cabin": True,
        "cargo": True,
        "max_kg": 9,
        "fee": "$100–$150/each way",
        "currency": "USD",
    },
}


def allowed_airline_codes(
    *,
    max_pet_kg: float | None = None,
    cargo_only: bool = False,
) -> list[str]:
    codes = set(PET_FRIENDLY_AIRLINES)
    if max_pet_kg is not None:
        codes = {code for code in codes if PET_POLICY[code]["max_kg"] >= max_pet_kg}
    if cargo_only:
        codes = {code for code in codes if PET_POLICY[code]["cargo"]}
    return sorted(codes)
