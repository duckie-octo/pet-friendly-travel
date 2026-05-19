from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.core.geoapify_client import GeoapifyClient, GeoapifyError, get_geoapify_client
from app.core.rapidapi_client import RapidApiClient, RapidApiError, get_rapidapi_client
from app.data.pet_airline_policies import PET_POLICY, allowed_airline_codes
from app.schemas.trip import (
    TripFlightOption,
    TripHotelOption,
    TripPlaceOption,
    TripSearchResponse,
)


def _iso_to_date_time(iso_value: str) -> tuple[str, str]:
    normalized = iso_value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        date_part = iso_value[:10]
        time_part = iso_value[11:16] if len(iso_value) > 11 else "00:00"
        return date_part, time_part
    return dt.date().isoformat(), dt.strftime("%H:%M")


def _price_total(price_breakdown: dict[str, Any] | None) -> float:
    if not price_breakdown:
        return 0.0
    total = price_breakdown.get("total") or {}
    units = float(total.get("units") or 0)
    nanos = float(total.get("nanos") or 0)
    return units + nanos / 1_000_000_000


def _carrier_code(leg: dict[str, Any]) -> str:
    carriers_data = leg.get("carriersData") or []
    if carriers_data:
        return str(carriers_data[0].get("code") or carriers_data[0].get("marketingCarrier") or "XX")
    carriers = leg.get("carriers") or []
    if carriers:
        return str(carriers[0])
    info = leg.get("flightInfo") or {}
    carrier_info = info.get("carrierInfo") or {}
    return str(carrier_info.get("marketingCarrier") or carrier_info.get("operatingCarrier") or "XX")


class TripSearchService:
    def __init__(
        self,
        rapidapi: RapidApiClient,
        geoapify: GeoapifyClient,
    ) -> None:
        self.rapidapi = rapidapi
        self.geoapify = geoapify
        self.settings = get_settings()

    def resolve_destination(self, city: str, country: str | None = None) -> dict[str, Any]:
        query = f"{city}, {country}" if country else city
        locations = self.rapidapi.search_locations(query)
        if not locations:
            raise RapidApiError(404, f"No Booking.com destination for {query!r}")
        hit = locations[0]
        return {
            "label": hit.get("label") or hit.get("name"),
            "dest_id": str(hit.get("dest_id")),
            "dest_type": hit.get("dest_type") or "city",
            "city": hit.get("city_name") or hit.get("name") or city,
            "country": hit.get("country") or country or "",
            "latitude": hit.get("latitude"),
            "longitude": hit.get("longitude"),
        }

    def search(
        self,
        *,
        origin_airport: str,
        destination_airport: str,
        dest_city: str,
        dest_country: str,
        depart_date: str,
        return_date: str | None,
        adults: int,
        pets_allowed: bool,
        places_limit: int = 15,
    ) -> TripSearchResponse:
        destination = self.resolve_destination(dest_city, dest_country)
        hints: list[str] = []

        flights = self._search_flights(
            origin_airport=origin_airport,
            destination_airport=destination_airport,
            depart_date=depart_date,
            return_date=return_date,
            adults=adults,
        )
        if not flights:
            hints.append(
                f"No pet-friendly airline offers for {origin_airport}→{destination_airport} on {depart_date}."
            )

        hotels = self._search_hotels(
            dest_id=destination["dest_id"],
            dest_type=destination["dest_type"],
            checkin=depart_date,
            checkout=return_date or depart_date,
            adults=adults,
            pets_allowed=pets_allowed,
            city=destination["city"],
            country=destination["country"],
        )
        if not hotels:
            hints.append(f"No pet-friendly hotels found near {destination['label']}.")

        places = self._search_places(
            city=dest_city,
            country=dest_country,
            limit=places_limit,
        )
        if not places:
            hints.append(f"No pet-related places found in {dest_city} via Geoapify.")

        return TripSearchResponse(
            destination=destination,
            flights=flights,
            hotels=hotels,
            places=places,
            hints=hints,
        )

    def _search_flights(
        self,
        *,
        origin_airport: str,
        destination_airport: str,
        depart_date: str,
        return_date: str | None,
        adults: int,
    ) -> list[TripFlightOption]:
        from_code = f"{origin_airport.upper()}.AIRPORT"
        to_code = f"{destination_airport.upper()}.AIRPORT"
        flight_type = "ROUNDTRIP" if return_date else "ONEWAY"
        payload = self.rapidapi.search_flights(
            depart_date=depart_date,
            from_code=from_code,
            to_code=to_code,
            adults=adults,
            currency="USD",
            flight_type=flight_type,
            return_date=return_date,
        )
        offers = payload.get("flightOffers") or []
        allowed = allowed_airline_codes()
        results: list[TripFlightOption] = []

        for offer in offers[:25]:
            segments = offer.get("segments") or []
            if not segments:
                continue
            seg = segments[0]
            legs = seg.get("legs") or []
            if not legs:
                continue
            leg = legs[0]
            code = _carrier_code(leg)
            if code not in allowed:
                continue
            policy = PET_POLICY.get(code)
            dep_date, dep_time = _iso_to_date_time(
                leg.get("departureTime") or seg.get("departureTime") or depart_date
            )
            arr_date, arr_time = _iso_to_date_time(
                leg.get("arrivalTime") or seg.get("arrivalTime") or depart_date
            )
            flight_info = leg.get("flightInfo") or {}
            origin = leg.get("departureAirport") or seg.get("departureAirport") or {}
            dest = leg.get("arrivalAirport") or seg.get("arrivalAirport") or {}
            results.append(
                TripFlightOption(
                    offer_token=offer.get("token"),
                    airline_code=code,
                    airline_name=(policy or {}).get("airline") or code,
                    flight_number=str(flight_info.get("flightNumber") or ""),
                    departure_date=dep_date,
                    departure_time=dep_time,
                    arrive_date=arr_date,
                    arrive_time=arr_time,
                    rate=round(_price_total(offer.get("priceBreakdown")), 2),
                    origin=str(origin.get("code") or origin_airport.upper()),
                    destination=str(dest.get("code") or destination_airport.upper()),
                    origin_name=origin.get("name"),
                    destination_name=dest.get("name"),
                    pet_policy=policy,
                )
            )
        return results

    def _search_hotels(
        self,
        *,
        dest_id: str,
        dest_type: str,
        checkin: str,
        checkout: str,
        adults: int,
        pets_allowed: bool,
        city: str,
        country: str,
    ) -> list[TripHotelOption]:
        cats = None
        if pets_allowed:
            cats = self.settings.booking_pet_categories_filter_ids

        payload = self.rapidapi.search_hotels(
            page_number=0,
            dest_type=dest_type,
            dest_id=dest_id,
            units="metric",
            children_number=0,
            locale="en-gb",
            include_adjacency=True,
            filter_by_currency="USD",
            order_by="popularity",
            checkin_date=checkin,
            checkout_date=checkout,
            room_number=1,
            adults_number=adults,
            categories_filter_ids=cats,
        )
        rows = payload.get("result") or []
        hotels: list[TripHotelOption] = []
        for row in rows[:20]:
            hotel_id = row.get("hotel_id")
            if hotel_id is None:
                continue
            hotels.append(
                TripHotelOption(
                    hotel_id=int(hotel_id),
                    hotel_name=str(row.get("hotel_name") or "Hotel"),
                    city=city,
                    country=country,
                    address=row.get("address"),
                    rate=float(row.get("min_total_price") or 0) or None,
                    currency=row.get("currencycode") or "USD",
                    photo_url=row.get("main_photo_url"),
                    pet_friendly=pets_allowed,
                    url=row.get("url"),
                )
            )
        return hotels

    def _search_places(self, *, city: str, country: str, limit: int) -> list[TripPlaceOption]:
        try:
            payload = self.geoapify.get_destinations(
                city=city,
                country=country,
                limit=limit,
                pets_allowed=True,
                categories="pet,pet.dog_park,commercial.pet,pet.veterinary",
            )
        except GeoapifyError:
            return []

        places: list[TripPlaceOption] = []
        for feature in payload.get("features") or []:
            props = feature.get("properties") or {}
            name = props.get("name") or props.get("address_line1")
            if not name:
                continue
            places.append(
                TripPlaceOption(
                    place_id=str(props.get("place_id") or ""),
                    name=str(name),
                    address=props.get("formatted") or props.get("address_line2"),
                    lat=props.get("lat"),
                    lon=props.get("lon"),
                    categories=list(props.get("categories") or []),
                )
            )
        return places


def get_trip_search_service() -> TripSearchService:
    return TripSearchService(get_rapidapi_client(), get_geoapify_client())
