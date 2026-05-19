import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_trips_db
from app.core.deps import get_current_user
from app.core.geoapify_client import GeoapifyError
from app.core.rapidapi_client import RapidApiError
from app.models.trips_schema import Flight, Trip, TripFlight, TripHotel, TripPetPlace
from app.models.userprofile import User
from app.schemas.trip import TripCreateRequest, TripSearchResponse
from app.schemas.trip_db import (
    FlightSummary,
    HotelSummary,
    PetPlaceSummary,
    TripDetailResponse,
    TripSummary,
)
from app.services.trip_persist_service import create_trip_from_selection
from app.services.trip_search_service import TripSearchService, get_trip_search_service

router = APIRouter(prefix="/trips", tags=["trips"])


def _trip_to_detail(trip: Trip) -> TripDetailResponse:
    flights: list[FlightSummary] = []
    for link in trip.trip_flights:
        f = link.flight
        flights.append(
            FlightSummary(
                id=f.id,
                airline_code=f.airline.iata_code,
                airline_name=f.airline.name,
                flight_number=f.flight_number,
                origin_iata=f.origin_iata,
                destination_iata=f.destination_iata,
                departs_at=f.departs_at,
                arrives_at=f.arrives_at,
                price=float(f.price) if f.price is not None else None,
                currency=f.currency,
            )
        )

    hotels: list[dict[str, Any]] = []
    for link in trip.trip_hotels:
        h = link.hotel
        hotels.append(
            {
                "id": str(h.id),
                "name": h.name,
                "city": h.city,
                "country_code": h.country_code,
                "check_in": link.check_in.isoformat(),
                "check_out": link.check_out.isoformat(),
                "guests": link.guests,
                "price_per_night": float(h.price_per_night) if h.price_per_night else None,
            }
        )

    pet_places: list[PetPlaceSummary] = []
    for link in trip.trip_pet_places:
        p = link.pet_place
        pet_places.append(
            PetPlaceSummary(
                id=p.id,
                name=p.name,
                address=p.address,
                city=p.city,
                pet_category=p.pet_category,
            )
        )

    return TripDetailResponse(
        id=trip.id,
        user_id=trip.user_id,
        title=trip.title,
        status=trip.status,
        start_date=trip.start_date,
        end_date=trip.end_date,
        notes=trip.notes,
        created_at=trip.created_at,
        flights=flights,
        hotels=hotels,
        pet_places=pet_places,
    )


def _load_trip(db: Session, trip_id: uuid.UUID, user_id: uuid.UUID) -> Trip:
    trip = (
        db.query(Trip)
        .options(
            joinedload(Trip.trip_flights).joinedload(TripFlight.flight).joinedload(Flight.airline),
            joinedload(Trip.trip_hotels).joinedload(TripHotel.hotel),
            joinedload(Trip.trip_pet_places).joinedload(TripPetPlace.pet_place),
        )
        .filter(Trip.id == trip_id, Trip.user_id == user_id)
        .first()
    )
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/search", response_model=TripSearchResponse, summary="Search live trip options")
async def search_trips(
    origin: str = Query(..., description="Origin airport IATA code, e.g. JFK"),
    destination: str = Query(..., description="Destination airport IATA code, e.g. LAX"),
    dest_city: str = Query(..., description="Destination city for hotels/places"),
    dest_country: str = Query(..., description="Destination country"),
    depart_date: str = Query(..., description="YYYY-MM-DD"),
    return_date: str | None = Query(None, description="YYYY-MM-DD"),
    adults: int = Query(1, ge=1, le=9),
    pets_allowed: bool = Query(True),
    service: TripSearchService = Depends(get_trip_search_service),
):
    try:
        return service.search(
            origin_airport=origin,
            destination_airport=destination,
            dest_city=dest_city,
            dest_country=dest_country,
            depart_date=depart_date,
            return_date=return_date,
            adults=adults,
            pets_allowed=pets_allowed,
        )
    except RapidApiError as err:
        raise HTTPException(status_code=err.status_code, detail=err.detail) from err
    except GeoapifyError as err:
        raise HTTPException(status_code=err.status_code, detail=err.detail) from err


@router.get("/", response_model=list[TripSummary], summary="List trips for current user")
def list_trips(
    db: Session = Depends(get_trips_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.created_at.desc())
        .all()
    )
    return [
        TripSummary(
            id=t.id,
            user_id=t.user_id,
            title=t.title,
            status=t.status,
            start_date=t.start_date,
            end_date=t.end_date,
            notes=t.notes,
            created_at=t.created_at,
        )
        for t in rows
    ]


@router.get("/{trip_id}", response_model=TripDetailResponse, summary="Get trip details")
def get_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_trips_db),
    current_user: User = Depends(get_current_user),
):
    trip = _load_trip(db, trip_id, current_user.id)
    return _trip_to_detail(trip)


@router.post(
    "/",
    response_model=TripDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save chosen trip to trips database (ERD schema)",
)
def save_trip(
    payload: TripCreateRequest,
    db: Session = Depends(get_trips_db),
    current_user: User = Depends(get_current_user),
):
    trip = create_trip_from_selection(db, user_id=current_user.id, payload=payload)
    return _trip_to_detail(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a trip")
def delete_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_trips_db),
    current_user: User = Depends(get_current_user),
):
    trip = _load_trip(db, trip_id, current_user.id)
    db.delete(trip)
    db.commit()
    return None
