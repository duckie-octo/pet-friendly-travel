"""
Booking API (sample DB)

- GET ``/bookings/`` — list bookings (pagination: ``skip``, ``limit``)
- POST ``/bookings/`` — create booking (optional nested hotel and flight reservations)
- GET ``/bookings/{booking_id}`` — booking details (user + reservations)
- PATCH ``/bookings/{booking_id}`` — update booking dates or agent
- DELETE ``/bookings/{booking_id}`` — delete booking and child reservations
- PATCH ``/bookings/{booking_id}/hotel-reservations/{reservation_no}`` — update hotel stay
- DELETE ``/bookings/{booking_id}/hotel-reservations/{reservation_no}`` — remove hotel stay
- POST ``/bookings/{booking_id}/flight-reservations`` — add a flight leg (supports ``Traveling_With_Pets`` / ``Pet_Count``)
- PATCH ``/bookings/{booking_id}/flight-reservations/{reservation_no}`` — update flight leg
- DELETE ``/bookings/{booking_id}/flight-reservations/{reservation_no}`` — remove flight leg
"""

from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.database import get_trips_db, get_userprofile_db
from app.core.deps import get_current_user
from app.core.security import hash_password
from app.models.booking import (
    Booking,
    FlightReservation,
    HotelReservation,
    User as LegacyUser,
)
from app.schemas.booking import (
    BookingResponse,
    BookingDetailResponse,
    BookingCreate,
    BookingUpdate,
    HotelReservationResponse,
    FlightReservationResponse,
    FlightReservationCreate,
    HotelReservationUpdate,
    FlightReservationUpdate,
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text


router = APIRouter(prefix="", tags=["booking"])


def _legacy_deprecated() -> None:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Legacy Bookings API is retired. Use GET/POST /api/v1/trips/ instead.",
    )


def _exists(db: Session, sql: str, params: dict) -> bool:
    return db.execute(text(sql), params).scalar() is not None


def _validate_hotel_code(db: Session, hotel_code: int) -> None:
    if not _exists(
        db,
        "SELECT 1 FROM Hotel_Master WHERE Hotel_Code = :hotel_code LIMIT 1",
        {"hotel_code": hotel_code},
    ):
        raise HTTPException(status_code=400, detail=f"Hotel_Code {hotel_code} does not exist in Hotel_Master.")


def _validate_airline_code(db: Session, airline_code: str) -> None:
    if not _exists(
        db,
        "SELECT 1 FROM Airline_Master WHERE Airline_Code = :airline_code LIMIT 1",
        {"airline_code": airline_code},
    ):
        raise HTTPException(status_code=400, detail=f"Airline_Code '{airline_code}' does not exist in Airline_Master.")


def _validate_airport_code(db: Session, airport_code: str, field_name: str) -> None:
    if not _exists(
        db,
        "SELECT 1 FROM Airport_Master WHERE Airport_Code = :airport_code LIMIT 1",
        {"airport_code": airport_code},
    ):
        raise HTTPException(status_code=400, detail=f"{field_name} '{airport_code}' does not exist in Airport_Master.")


def _validate_flight_master_codes(db: Session, flight: FlightReservationCreate) -> None:
    _validate_airline_code(db, flight.Airline_Code)
    _validate_airport_code(db, flight.Origin_Airport_Code, "Origin_Airport_Code")
    _validate_airport_code(db, flight.Destination_Airport_Code, "Destination_Airport_Code")


def _get_user_booking(
    booking_id: int,
    current_user,
    db: Session,
) -> Booking:
    db_booking = db.query(Booking).filter(Booking.Booking_Id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
    if db_booking.User_Id != current_user.User_ID:
        raise HTTPException(status_code=403, detail="Not allowed to access this booking")
    return db_booking


def _normalize_flight_pet_fields(reservation: FlightReservation) -> None:
    if not reservation.Traveling_With_Pets:
        reservation.Pet_Count = None
        return
    if reservation.Pet_Count is None or reservation.Pet_Count < 1:
        raise HTTPException(
            status_code=400,
            detail="Pet_Count is required and must be >= 1 when Traveling_With_Pets is true.",
        )

# ==========================================
# ENDPOINTS (CRUD)
# ==========================================

# 1. READ: Get all Bookings (with pagination)
@router.get("/bookings", response_model=List[BookingResponse], summary="List all bookings", include_in_schema=False)
@router.get("/bookings/", response_model=List[BookingResponse], summary="List all bookings")
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    """Deprecated — use GET /api/v1/trips/."""
    _legacy_deprecated()
    bookings = (
        db.query(Booking)
        .filter(Booking.User_Id == current_user.User_ID)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return bookings

# 2. READ: Get a specific Booking by ID (with full details)
@router.get("/bookings/{booking_id}", response_model=BookingDetailResponse, summary="Get booking details")
def read_booking(
    booking_id: int,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    """Deprecated — use GET /api/v1/trips/{trip_id}."""
    _legacy_deprecated()

# 3. CREATE: Add a new Booking
@router.get("/setup-seed-data/", include_in_schema=False)
def seed_data(db: Session = Depends(get_userprofile_db)):
    """Create demo user in the userprofile ``users`` table."""
    from app.models.userprofile import User as ProfileUser

    test_email = "test@example.com"
    default_password = "testpass123"
    existing_user = db.query(ProfileUser).filter(ProfileUser.email == test_email).first()
    if existing_user:
        return {
            "message": (
                f"Seed user already exists (ID: {existing_user.id}). "
                f"Login: {test_email} / {default_password}"
            )
        }

    new_user = ProfileUser(
        email=test_email,
        password_hash=hash_password(default_password),
        full_name="Test Subject",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": (
            f"Test user created (ID: {new_user.id}). "
            f"Login: {test_email} / {default_password}"
        )
    }

@router.post("/bookings/", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED, summary="Create a new booking")
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    """Deprecated — use POST /api/v1/trips/."""
    _legacy_deprecated()
    if booking.User_Id != current_user.User_ID:
        raise HTTPException(
            status_code=403,
            detail="User_Id must match the authenticated user",
        )

    booking_data = booking.model_dump(exclude={"hotel_reservations", "flight_reservations"})
    db_booking = Booking(**booking_data)

    db.add(db_booking)
    db.flush()

    for hotel in booking.hotel_reservations:
        _validate_hotel_code(db, hotel.Hotel_Code)
        db.add(
            HotelReservation(
                Booking_Id=db_booking.Booking_Id,
                **hotel.model_dump(),
            )
        )

    for flight in booking.flight_reservations:
        _validate_flight_master_codes(db, flight)
        db.add(
            FlightReservation(
                Booking_Id=db_booking.Booking_Id,
                **flight.model_dump(),
            )
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid reservation reference data provided.") from exc

    db.refresh(db_booking)
    return db_booking

# 4. UPDATE: Modify an existing Booking
@router.patch("/bookings/{booking_id}", response_model=BookingResponse, summary="Update an existing booking")
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    """Deprecated — use /api/v1/trips/."""
    _legacy_deprecated()
    db_booking = _get_user_booking(booking_id, current_user, db)

    # Extract update data, excluding fields set to None
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Apply updates to the model
    for key, value in update_data.items():
        setattr(db_booking, key, value)

    db.commit()
    db.refresh(db_booking)
    return db_booking

# 5. DELETE: Remove an existing Booking
@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a booking")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    """Deprecated — use DELETE /api/v1/trips/{trip_id}."""
    _legacy_deprecated()
    db_booking = _get_user_booking(booking_id, current_user, db)

    db.delete(db_booking)
    db.commit()
    return None # HTTP 204 requires no content


# 6. UPDATE: Modify a hotel reservation under a booking
@router.patch(
    "/bookings/{booking_id}/hotel-reservations/{reservation_no}",
    response_model=HotelReservationResponse,
    summary="Update a hotel reservation",
)
def update_hotel_reservation(
    booking_id: int,
    reservation_no: int,
    reservation_update: HotelReservationUpdate = Body(
        ...,
        examples={
            "change_stay_dates": {
                "summary": "Change check-in/check-out dates",
                "value": {
                    "Check_In_Date": "2026-06-11",
                    "Check_Out_Date": "2026-06-20"
                },
            },
            "change_rate_and_hotel": {
                "summary": "Move to a different hotel and update rate",
                "value": {
                    "Hotel_Code": 3,
                    "Rate": 349.99
                },
            },
        },
    ),
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    _legacy_deprecated()
    _get_user_booking(booking_id, current_user, db)
    db_reservation = (
        db.query(HotelReservation)
        .filter(
            HotelReservation.Reservation_No == reservation_no,
            HotelReservation.Booking_Id == booking_id,
        )
        .first()
    )
    if db_reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Hotel reservation {reservation_no} not found for booking {booking_id}",
        )

    update_data = reservation_update.model_dump(exclude_unset=True)
    if "Hotel_Code" in update_data:
        _validate_hotel_code(db, update_data["Hotel_Code"])

    for key, value in update_data.items():
        setattr(db_reservation, key, value)

    db.commit()
    db.refresh(db_reservation)
    return db_reservation


# 7. DELETE: Remove a hotel reservation under a booking
@router.delete(
    "/bookings/{booking_id}/hotel-reservations/{reservation_no}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hotel reservation",
)
def delete_hotel_reservation(
    booking_id: int,
    reservation_no: int,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    _legacy_deprecated()
    _get_user_booking(booking_id, current_user, db)
    db_reservation = (
        db.query(HotelReservation)
        .filter(
            HotelReservation.Reservation_No == reservation_no,
            HotelReservation.Booking_Id == booking_id,
        )
        .first()
    )
    if db_reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Hotel reservation {reservation_no} not found for booking {booking_id}",
        )

    db.delete(db_reservation)
    db.commit()
    return None


# 8. CREATE: Add a flight reservation to an existing booking (including pets on the segment)
@router.post(
    "/bookings/{booking_id}/flight-reservations",
    response_model=FlightReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a flight reservation to a booking",
)
def create_flight_reservation(
    booking_id: int,
    flight: FlightReservationCreate,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    _legacy_deprecated()
    _get_user_booking(booking_id, current_user, db)

    _validate_flight_master_codes(db, flight)
    db_row = FlightReservation(Booking_Id=booking_id, **flight.model_dump())
    db.add(db_row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid flight reservation data.") from exc
    db.refresh(db_row)
    return db_row


# 9. UPDATE: Modify a flight reservation under a booking
@router.patch(
    "/bookings/{booking_id}/flight-reservations/{reservation_no}",
    response_model=FlightReservationResponse,
    summary="Update a flight reservation",
)
def update_flight_reservation(
    booking_id: int,
    reservation_no: int,
    reservation_update: FlightReservationUpdate = Body(
        ...,
        examples={
            "change_departure_time": {
                "summary": "Update departure date and time",
                "value": {
                    "Departure_Date": "2026-06-10",
                    "Departure_Time": "20:15"
                },
            },
            "change_route_and_airline": {
                "summary": "Switch airline and destination airport",
                "value": {
                    "Airline_Code": "DL",
                    "Destination_Airport_Code": "LAX"
                },
            },
            "add_pets_to_segment": {
                "summary": "Mark segment as traveling with pets",
                "value": {
                    "Traveling_With_Pets": True,
                    "Pet_Count": 2
                },
            },
        },
    ),
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    _legacy_deprecated()
    _get_user_booking(booking_id, current_user, db)
    db_reservation = (
        db.query(FlightReservation)
        .filter(
            FlightReservation.Reservation_No == reservation_no,
            FlightReservation.Booking_Id == booking_id,
        )
        .first()
    )
    if db_reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Flight reservation {reservation_no} not found for booking {booking_id}",
        )

    update_data = reservation_update.model_dump(exclude_unset=True)
    if "Airline_Code" in update_data:
        _validate_airline_code(db, update_data["Airline_Code"])
    if "Origin_Airport_Code" in update_data:
        _validate_airport_code(db, update_data["Origin_Airport_Code"], "Origin_Airport_Code")
    if "Destination_Airport_Code" in update_data:
        _validate_airport_code(db, update_data["Destination_Airport_Code"], "Destination_Airport_Code")

    for key, value in update_data.items():
        setattr(db_reservation, key, value)

    try:
        _normalize_flight_pet_fields(db_reservation)
    except HTTPException:
        db.rollback()
        raise

    db.commit()
    db.refresh(db_reservation)
    return db_reservation


# 10. DELETE: Remove a flight reservation under a booking
@router.delete(
    "/bookings/{booking_id}/flight-reservations/{reservation_no}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a flight reservation",
)
def delete_flight_reservation(
    booking_id: int,
    reservation_no: int,
    db: Session = Depends(get_trips_db),
    current_user=Depends(get_current_user),
):
    _legacy_deprecated()
    _get_user_booking(booking_id, current_user, db)
    db_reservation = (
        db.query(FlightReservation)
        .filter(
            FlightReservation.Reservation_No == reservation_no,
            FlightReservation.Booking_Id == booking_id,
        )
        .first()
    )
    if db_reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Flight reservation {reservation_no} not found for booking {booking_id}",
        )

    db.delete(db_reservation)
    db.commit()
    return None
