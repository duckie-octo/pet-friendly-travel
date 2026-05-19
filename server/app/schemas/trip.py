from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class TripFlightOption(BaseModel):
    offer_token: str | None = None
    airline_code: str
    airline_name: str
    flight_number: str
    departure_date: str
    departure_time: str
    arrive_date: str
    arrive_time: str
    rate: float
    origin: str
    destination: str
    origin_name: str | None = None
    destination_name: str | None = None
    pet_policy: dict[str, Any] | None = None


class TripHotelOption(BaseModel):
    hotel_id: int
    hotel_name: str
    city: str
    country: str
    address: str | None = None
    rate: float | None = None
    currency: str | None = None
    photo_url: str | None = None
    pet_friendly: bool = True
    url: str | None = None


class TripPlaceOption(BaseModel):
    place_id: str | None = None
    name: str
    address: str | None = None
    lat: float | None = None
    lon: float | None = None
    categories: list[str] = Field(default_factory=list)


class TripSearchResponse(BaseModel):
    destination: dict[str, Any]
    flights: list[TripFlightOption]
    hotels: list[TripHotelOption]
    places: list[TripPlaceOption]
    hints: list[str] = Field(default_factory=list)


class TripPlaceSelection(BaseModel):
    place_id: str | None = None
    name: str
    address: str | None = None
    lat: float | None = None
    lon: float | None = None
    categories: list[str] = Field(default_factory=list)
    notes: str | None = None


class TripCreateRequest(BaseModel):
    start_date: date
    end_date: date
    title: str | None = None
    notes: str | None = None
    guests: int = Field(default=1, ge=1, le=20)
    selected_flight: TripFlightOption
    selected_hotel: TripHotelOption
    selected_places: list[TripPlaceSelection] = Field(default_factory=list)
    traveling_with_pets: bool = False
    pet_count: int | None = None
