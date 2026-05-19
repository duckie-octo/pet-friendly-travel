from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FlightSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    airline_code: str
    airline_name: str
    flight_number: str
    origin_iata: str
    destination_iata: str
    departs_at: datetime
    arrives_at: datetime
    price: float | None = None
    currency: str | None = None


class HotelSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_hotel_id: str
    name: str
    city: str
    country_code: str
    address: str | None = None
    price_per_night: float | None = None
    currency: str | None = None


class PetPlaceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address: str | None = None
    city: str | None = None
    pet_category: str | None = None


class TripSummary(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    status: str
    start_date: date
    end_date: date
    notes: str | None = None
    created_at: datetime


class TripDetailResponse(TripSummary):
    flights: list[FlightSummary] = Field(default_factory=list)
    hotels: list[dict[str, Any]] = Field(default_factory=list)
    pet_places: list[PetPlaceSummary] = Field(default_factory=list)
