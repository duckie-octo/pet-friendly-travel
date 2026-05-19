from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.database import engine, get_db
from app.data.pet_airline_policies import PET_POLICY, allowed_airline_codes
from app.schemas.flight import (
    FlightResult,
    PetFriendlyAirlinesResponse,
    PetFriendlyFlightsResponse,
    PetPolicy,
)

router = APIRouter(tags=["flights"])


@lru_cache(maxsize=1)
def _flight_table_name() -> str:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND lower(name)='flight_reservations'"
            )
        ).fetchall()
    if not rows:
        return "Flight_Reservations"
    return rows[0][0]


@lru_cache(maxsize=1)
def _airline_table_name() -> str:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND lower(name)='airline_master'"
            )
        ).fetchall()
    if not rows:
        return "Airline_Master"
    return rows[0][0]


@lru_cache(maxsize=1)
def _flight_select_sql() -> str:
    flight_table = _flight_table_name()
    airline_table = _airline_table_name()

    with engine.connect() as conn:
        rows = conn.execute(text(f'PRAGMA table_info("{flight_table}")')).fetchall()
    columns = {row[1] for row in rows}

    pet_columns = ""
    if "Traveling_With_Pets" in columns and "Pet_Count" in columns:
        pet_columns = """,
    fr.Traveling_With_Pets,
    fr.Pet_Count"""

    return f"""
SELECT
    fr.Reservation_No,
    fr.Booking_Id,
    fr.Airline_Code,
    am.Airline_Name,
    fr.Flight_Number,
    fr.Departure_Date,
    fr.Departure_Time,
    fr.Arrive_Date,
    fr.Arrive_Time,
    fr.Rate,
    fr.Origin_Airport_Code      AS Origin,
    fr.Destination_Airport_Code AS Destination{pet_columns}
FROM "{flight_table}" fr
JOIN "{airline_table}" am ON fr.Airline_Code = am.Airline_Code
"""


def _rows_to_results(rows: list[Any]) -> list[FlightResult]:
    results: list[FlightResult] = []
    for row in rows:
        mapping = dict(row._mapping)
        code = mapping["Airline_Code"]
        policy = PET_POLICY.get(code)
        if policy is None:
            continue
        results.append(
            FlightResult(
                reservation_no=mapping["Reservation_No"],
                booking_id=mapping["Booking_Id"],
                airline_code=code,
                airline_name=mapping["Airline_Name"],
                flight_number=mapping["Flight_Number"],
                departure_date=str(mapping["Departure_Date"]),
                departure_time=mapping["Departure_Time"],
                arrive_date=str(mapping["Arrive_Date"]),
                arrive_time=mapping["Arrive_Time"],
                rate=mapping["Rate"],
                origin=mapping["Origin"],
                destination=mapping["Destination"],
                traveling_with_pets=bool(mapping.get("Traveling_With_Pets", 0)),
                pet_count=mapping.get("Pet_Count"),
                pet_policy=PetPolicy(**policy),
            )
        )
    return results


def _execute_flight_query(db: Session, sql: str, params: dict[str, Any]) -> list[FlightResult]:
    try:
        rows = db.execute(text(sql), params).fetchall()
    except OperationalError as exc:
        if "no such table" in str(exc).lower():
            raise HTTPException(
                status_code=503,
                detail="Flight tables missing. Recreate DB from app/schemas/init_db.sql.",
            ) from exc
        raise
    return _rows_to_results(rows)


def _in_clause_params(codes: list[str]) -> tuple[str, dict[str, str]]:
    if not codes:
        return "", {}
    placeholders = ", ".join(f":code_{i}" for i in range(len(codes)))
    params = {f"code_{i}": code for i, code in enumerate(codes)}
    return placeholders, params


def _route_departure_dates(
    db: Session,
    *,
    origin: str | None,
    destination: str | None,
    codes: list[str],
) -> list[str]:
    if not origin or not destination or not codes:
        return []

    in_clause, params = _in_clause_params(codes)
    params["origin"] = origin.upper()
    params["destination"] = destination.upper()
    sql = f"""
{_flight_select_sql()}
WHERE fr.Airline_Code IN ({in_clause})
  AND fr.Origin_Airport_Code = :origin
  AND fr.Destination_Airport_Code = :destination
ORDER BY fr.Departure_Date
"""
    rows = db.execute(text(sql), params).fetchall()
    return sorted({str(dict(row._mapping)["Departure_Date"]) for row in rows})


def _search_hints(
    db: Session,
    *,
    flights: list[FlightResult],
    origin: str | None,
    destination: str | None,
    date: str | None,
    max_pet_kg: float | None,
    cargo_only: bool,
    allowed_codes: list[str],
) -> list[str]:
    if flights:
        return []

    hints: list[str] = []

    if not allowed_codes:
        hints.append(
            "No pet-friendly airlines match max_pet_kg/cargo_only. "
            "Try lowering max_pet_kg or set cargo_only=false."
        )
        if max_pet_kg is not None:
            hints.append(
                f"Example: Delta (DL) allows up to 8 kg; max_pet_kg={max_pet_kg} excludes DL."
            )
        return hints

    if origin and destination:
        all_on_route = _route_departure_dates(
            db,
            origin=origin,
            destination=destination,
            codes=allowed_airline_codes(),
        )
        available = _route_departure_dates(
            db, origin=origin, destination=destination, codes=allowed_codes
        )

        if all_on_route and not available and max_pet_kg is not None:
            hints.append(
                f"Flights exist for {origin.upper()}→{destination.upper()} on "
                f"{', '.join(all_on_route)}, but max_pet_kg={max_pet_kg} excludes those "
                "airlines (e.g. Delta allows 8 kg)."
            )
        elif date and available and date not in available:
            hints.append(
                f"No flights on {date} for {origin.upper()}→{destination.upper()} "
                f"with the current filters."
            )
            hints.append(f"Try departure_date one of: {', '.join(available)}.")
        elif date and all_on_route and date not in all_on_route:
            hints.append(
                f"No flights on {date} for {origin.upper()}→{destination.upper()} "
                f"in the local database."
            )
            hints.append(f"Try departure_date one of: {', '.join(all_on_route)}.")
        elif not all_on_route:
            hints.append(
                f"No pet-friendly flights in DB for {origin.upper()}→{destination.upper()}. "
                "Seed data includes JFK→LAX (DL, 2024-08-15) and HND→CDG (DL, 2024-06-04)."
            )

    if max_pet_kg is not None:
        excluded = [
            code
            for code in PET_POLICY
            if code in allowed_airline_codes()
            and PET_POLICY[code]["max_kg"] < max_pet_kg
        ]
        if excluded:
            hints.append(
                f"max_pet_kg={max_pet_kg} requires airline cabin limit ≥ that weight; "
                f"excluded: {', '.join(sorted(excluded))}."
            )

    if cargo_only:
        hints.append("cargo_only=true limits to airlines that allow pets as cargo.")

    hints.append(
        "Use GET /api/v1/flights/pet-friendly (no filters) to list all DB flights on "
        "pet-friendly airlines."
    )
    return hints


def _as_response(
    flights: list[FlightResult],
    hints: list[str] | None = None,
) -> PetFriendlyFlightsResponse:
    return PetFriendlyFlightsResponse(
        count=len(flights),
        flights=flights,
        hints=hints or [],
    )


@router.get(
    "/airlines/pet-friendly",
    response_model=PetFriendlyAirlinesResponse,
    summary="List all pet-friendly airlines",
)
def list_pet_friendly_airlines():
    airlines = [PetPolicy(**policy) for policy in PET_POLICY.values()]
    return PetFriendlyAirlinesResponse(count=len(airlines), airlines=airlines)


@router.get(
    "/flights/pet-friendly",
    response_model=PetFriendlyFlightsResponse,
    summary="Get all flights on pet-friendly airlines",
)
def get_pet_friendly_flights(db: Session = Depends(get_db)):
    codes = allowed_airline_codes()
    in_clause, params = _in_clause_params(codes)
    if not in_clause:
        return _as_response(
            [],
            ["Pet-friendly airline allowlist is empty."],
        )

    sql = (
        f"{_flight_select_sql()} WHERE fr.Airline_Code IN ({in_clause}) "
        "ORDER BY fr.Departure_Date, fr.Departure_Time"
    )
    flights = _execute_flight_query(db, sql, params)
    hints = []
    if not flights:
        hints.append(
            "No rows in Flight_Reservations for pet-friendly airlines (AA, DL, UA, …). "
            "Re-seed travel_booking.db from app/schemas/init_db.sql."
        )
    return _as_response(flights, hints)


@router.get(
    "/flights/pet-friendly/search",
    response_model=PetFriendlyFlightsResponse,
    summary="Search pet-friendly flights in local database",
)
def search_pet_friendly_flights(
    origin: str | None = Query(None, description="Origin airport IATA code, e.g. JFK"),
    destination: str | None = Query(None, description="Destination airport IATA code, e.g. LAX"),
    date: str | None = Query(
        None,
        description="Departure date YYYY-MM-DD (seed data uses 2024 dates, e.g. 2024-08-15 for JFK→LAX)",
    ),
    max_pet_kg: float | None = Query(
        None,
        description=(
            "Your pet's weight in kg. Only airlines whose in-cabin limit is >= this value "
            "are included (Delta allows 8 kg, so max_pet_kg=9 excludes DL)."
        ),
    ),
    cargo_only: bool = Query(False, description="Only airlines that allow pets as cargo"),
    db: Session = Depends(get_db),
):
    codes = allowed_airline_codes(max_pet_kg=max_pet_kg, cargo_only=cargo_only)
    in_clause, params = _in_clause_params(codes)
    if not in_clause:
        return _as_response(
            [],
            _search_hints(
                db,
                flights=[],
                origin=origin,
                destination=destination,
                date=date,
                max_pet_kg=max_pet_kg,
                cargo_only=cargo_only,
                allowed_codes=codes,
            ),
        )

    filters = f"WHERE fr.Airline_Code IN ({in_clause})"

    if origin:
        filters += " AND fr.Origin_Airport_Code = :origin"
        params["origin"] = origin.upper()

    if destination:
        filters += " AND fr.Destination_Airport_Code = :destination"
        params["destination"] = destination.upper()

    if date:
        filters += " AND fr.Departure_Date = :date"
        params["date"] = date

    sql = f"{_flight_select_sql()} {filters} ORDER BY fr.Departure_Date, fr.Departure_Time"
    flights = _execute_flight_query(db, sql, params)
    hints = _search_hints(
        db,
        flights=flights,
        origin=origin,
        destination=destination,
        date=date,
        max_pet_kg=max_pet_kg,
        cargo_only=cargo_only,
        allowed_codes=codes,
    )
    return _as_response(flights, hints)
