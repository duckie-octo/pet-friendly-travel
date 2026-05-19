import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TripsBase


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Airline(TripsBase):
    __tablename__ = "airlines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    iata_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    pet_policy = relationship("AirlinePetPolicy", back_populates="airline", uselist=False)
    flights = relationship("Flight", back_populates="airline")


class AirlinePetPolicy(TripsBase):
    __tablename__ = "airline_pet_policies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    airline_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("airlines.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    allow_pet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fee_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    policy_source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    policy_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    airline = relationship("Airline", back_populates="pet_policy")


class Flight(TripsBase):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    booking_flight_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    booking_search_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    airline_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("airlines.id"), nullable=False
    )
    flight_number: Mapped[str] = mapped_column(String(32), nullable=False)
    origin_iata: Mapped[str] = mapped_column(String(8), nullable=False)
    destination_iata: Mapped[str] = mapped_column(String(8), nullable=False)
    departs_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrives_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stops: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cabin_class: Mapped[str | None] = mapped_column(String(32), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    cache_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    airline = relationship("Airline", back_populates="flights")
    trip_links = relationship("TripFlight", back_populates="flight")


class Hotel(TripsBase):
    __tablename__ = "hotels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    booking_hotel_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    country_code: Mapped[str] = mapped_column(String(8), nullable=False)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    star_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_score: Mapped[float | None] = mapped_column(nullable=True)
    price_per_night: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    cache_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dog_policy = relationship("HotelDogPolicy", back_populates="hotel", uselist=False)
    trip_links = relationship("TripHotel", back_populates="hotel")


class HotelDogPolicy(TripsBase):
    __tablename__ = "hotel_dog_policies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("hotels.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    dogs_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    size_allowed: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    admin_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    hotel = relationship("Hotel", back_populates="dog_policy")


class PetPlace(TripsBase):
    __tablename__ = "pet_places"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    google_place_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    pet_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pet_subcategory: Mapped[str | None] = mapped_column(String(128), nullable=True)
    google_rating: Mapped[float | None] = mapped_column(nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    cache_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    details = relationship("PetPlaceDetail", back_populates="pet_place", uselist=False)
    trip_links = relationship("TripPetPlace", back_populates="pet_place")


class PetPlaceDetail(TripsBase):
    __tablename__ = "pet_place_details"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pet_place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pet_places.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    accepts_dogs: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    size_restrictions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    breed_restrictions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fee_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amenities: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    admin_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    pet_place = relationship("PetPlace", back_populates="details")


class Trip(TripsBase):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    trip_flights = relationship("TripFlight", back_populates="trip", cascade="all, delete-orphan")
    trip_hotels = relationship("TripHotel", back_populates="trip", cascade="all, delete-orphan")
    trip_pet_places = relationship(
        "TripPetPlace", back_populates="trip", cascade="all, delete-orphan"
    )


class TripFlight(TripsBase):
    __tablename__ = "trip_flights"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    flight_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("flights.id"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    trip = relationship("Trip", back_populates="trip_flights")
    flight = relationship("Flight", back_populates="trip_links")


class TripHotel(TripsBase):
    __tablename__ = "trip_hotels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    hotel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("hotels.id"), nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    trip = relationship("Trip", back_populates="trip_hotels")
    hotel = relationship("Hotel", back_populates="trip_links")


class TripPetPlace(TripsBase):
    __tablename__ = "trip_pet_places"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    pet_place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pet_places.id"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    trip = relationship("Trip", back_populates="trip_pet_places")
    pet_place = relationship("PetPlace", back_populates="trip_links")
