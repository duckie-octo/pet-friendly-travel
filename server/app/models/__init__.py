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
from app.models.userprofile import User

# Legacy booking models (sample DB) — optional if init_db.sql was loaded
try:
    from app.models.booking import (  # noqa: F401
        ActivityReservation,
        Booking,
        FlightReservation,
        HotelReservation,
    )
except ImportError:
    pass
