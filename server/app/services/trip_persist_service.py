from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.data.pet_airline_policies import PET_POLICY
from app.models.trips_schema import (
    Airline,
    AirlinePetPolicy,
    Flight,
    Hotel,
    HotelDogPolicy,
    PetPlace,
    PetPlaceDetail,
    Trip,
    TripFlight,
    TripHotel,
    TripPetPlace,
)
from app.schemas.trip import TripCreateRequest, TripFlightOption, TripHotelOption, TripPlaceOption


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.fromisoformat(f"{date_str[:10]}T{time_str}:00").replace(tzinfo=timezone.utc)


def _country_code(country: str) -> str:
    mapping = {
        "USA": "US",
        "United States": "US",
        "UK": "GB",
        "United Kingdom": "GB",
        "France": "FR",
        "Japan": "JP",
    }
    if len(country) == 2:
        return country.upper()
    return mapping.get(country, country[:2].upper() if country else "US")


def _get_or_create_airline(db: Session, iata: str, name: str) -> Airline:
    row = db.execute(select(Airline).where(Airline.iata_code == iata.upper())).scalar_one_or_none()
    if row:
        return row
    airline = Airline(iata_code=iata.upper(), name=name or iata)
    db.add(airline)
    db.flush()
    policy = PET_POLICY.get(iata.upper())
    if policy:
        db.add(
            AirlinePetPolicy(
                airline_id=airline.id,
                allow_pet=bool(policy.get("in_cabin")),
                fee_currency=policy.get("currency"),
            )
        )
    return airline


def _get_or_create_flight(db: Session, option: TripFlightOption, airline: Airline) -> Flight:
    booking_id = option.offer_token or f"{option.airline_code}-{option.flight_number}-{option.departure_date}"
    existing = db.execute(
        select(Flight).where(Flight.booking_flight_id == booking_id)
    ).scalar_one_or_none()
    if existing:
        return existing

    departs = _parse_datetime(option.departure_date, option.departure_time)
    arrives = _parse_datetime(option.arrive_date, option.arrive_time)
    duration = int((arrives - departs).total_seconds() // 60) if arrives > departs else None

    flight = Flight(
        booking_flight_id=booking_id,
        airline_id=airline.id,
        flight_number=option.flight_number,
        origin_iata=option.origin.upper(),
        destination_iata=option.destination.upper(),
        departs_at=departs,
        arrives_at=arrives,
        duration_minutes=duration,
        stops=0,
        price=Decimal(str(option.rate)) if option.rate is not None else None,
        cabin_class="ECONOMY",
        currency="USD",
        cache_expires_at=_utcnow() + timedelta(hours=24),
    )
    db.add(flight)
    db.flush()
    return flight


def _get_or_create_hotel(db: Session, option: TripHotelOption) -> Hotel:
    booking_id = str(option.hotel_id)
    existing = db.execute(
        select(Hotel).where(Hotel.booking_hotel_id == booking_id)
    ).scalar_one_or_none()
    if existing:
        return existing

    nights = max(1, 1)
    nightly = None
    if option.rate is not None:
        nightly = Decimal(str(option.rate))

    hotel = Hotel(
        booking_hotel_id=booking_id,
        name=option.hotel_name,
        address=option.address,
        city=option.city,
        country_code=_country_code(option.country),
        price_per_night=nightly,
        currency=option.currency or "USD",
        cache_expires_at=_utcnow() + timedelta(hours=24),
    )
    db.add(hotel)
    db.flush()
    if option.pet_friendly:
        db.add(HotelDogPolicy(hotel_id=hotel.id, dogs_allowed=True))
    return hotel


def _get_or_create_pet_place(db: Session, option: TripPlaceOption, city: str, country: str) -> PetPlace:
    external_id = option.place_id or f"{option.name}:{option.lat}:{option.lon}"
    existing = db.execute(
        select(PetPlace).where(PetPlace.google_place_id == external_id)
    ).scalar_one_or_none()
    if existing:
        return existing

    categories = option.categories or []
    pet_cat = categories[0] if categories else "pet"

    place = PetPlace(
        google_place_id=external_id,
        name=option.name,
        address=option.address,
        city=city,
        country_code=_country_code(country),
        latitude=option.lat,
        longitude=option.lon,
        pet_category=pet_cat,
        cache_expires_at=_utcnow() + timedelta(days=7),
    )
    db.add(place)
    db.flush()
    db.add(PetPlaceDetail(pet_place_id=place.id, accepts_dogs=True))
    return place


def create_trip_from_selection(
    db: Session,
    *,
    user_id: uuid.UUID,
    payload: TripCreateRequest,
) -> Trip:
    flight_opt = payload.selected_flight
    hotel_opt = payload.selected_hotel

    airline = _get_or_create_airline(db, flight_opt.airline_code, flight_opt.airline_name)
    flight = _get_or_create_flight(db, flight_opt, airline)
    hotel = _get_or_create_hotel(db, hotel_opt)

    title = payload.title or f"{flight_opt.origin} → {flight_opt.destination}"
    trip = Trip(
        user_id=user_id,
        title=title,
        status="planned",
        start_date=payload.start_date,
        end_date=payload.end_date,
        notes=payload.notes,
    )
    db.add(trip)
    db.flush()

    db.add(TripFlight(trip_id=trip.id, flight_id=flight.id, sort_order=0))
    db.add(
        TripHotel(
            trip_id=trip.id,
            hotel_id=hotel.id,
            check_in=payload.start_date,
            check_out=payload.end_date,
            guests=payload.guests,
        )
    )

    for idx, place_sel in enumerate(payload.selected_places):
        place_opt = TripPlaceOption(
            place_id=place_sel.place_id,
            name=place_sel.name,
            address=place_sel.address,
            lat=place_sel.lat,
            lon=place_sel.lon,
            categories=place_sel.categories or [],
        )
        pet_place = _get_or_create_pet_place(
            db, place_opt, city=hotel_opt.city, country=hotel_opt.country
        )
        db.add(
            TripPetPlace(
                trip_id=trip.id,
                pet_place_id=pet_place.id,
                sort_order=idx,
                notes=place_sel.notes,
            )
        )

    db.commit()
    return (
        db.query(Trip)
        .options(
            joinedload(Trip.trip_flights).joinedload(TripFlight.flight).joinedload(Flight.airline),
            joinedload(Trip.trip_hotels).joinedload(TripHotel.hotel),
            joinedload(Trip.trip_pet_places).joinedload(TripPetPlace.pet_place),
        )
        .filter(Trip.id == trip.id)
        .one()
    )
