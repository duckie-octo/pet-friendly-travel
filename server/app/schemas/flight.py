from pydantic import BaseModel


class PetPolicy(BaseModel):
    airline: str
    in_cabin: bool
    cargo: bool
    max_kg: float
    fee: str
    currency: str


class FlightResult(BaseModel):
    reservation_no: int
    booking_id: int
    airline_code: str
    airline_name: str
    flight_number: str
    departure_date: str
    departure_time: str
    arrive_date: str
    arrive_time: str
    rate: float | None
    origin: str
    destination: str
    traveling_with_pets: bool
    pet_count: int | None
    pet_policy: PetPolicy


class PetFriendlyAirlinesResponse(BaseModel):
    count: int
    airlines: list[PetPolicy]


class PetFriendlyFlightsResponse(BaseModel):
    count: int
    flights: list[FlightResult]
    hints: list[str] = []
