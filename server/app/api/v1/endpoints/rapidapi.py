from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_settings
from app.core.rapidapi_client import RapidApiError, get_rapidapi_client
from app.services.rapidapi_service import RapidApiService

router = APIRouter(prefix="", tags=["rapidapi"])

def get_rapidapi_service() -> RapidApiService:
    return RapidApiService(get_rapidapi_client())


@router.get("/attractions/search")
async def search_attractions(
    start_date: str = Query(..., description="Format: YYYY-MM-DD"),
    end_date: str = Query(..., description="Format: YYYY-MM-DD"),
    dest_id: str = Query(..., description="Destination ID, e.g. 20088325"),
    locale: str = Query("en-gb"),
    page_number: int = Query(0, ge=0),
    currency: str = Query("AED"),
    order_by: str = Query("attr_book_score"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    try:
        return service.search_attractions(
            start_date=start_date,
            end_date=end_date,
            dest_id=dest_id,
            locale=locale,
            page_number=page_number,
            currency=currency,
            order_by=order_by,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get(
    "/hotels/search",
    tags=["hotels"],
    summary="Search hotels (Booking.com / RapidAPI)",
)
async def search_hotels(
    page_number: int = Query(0, ge=0),
    dest_type: str = Query("city"),
    dest_id: str = Query(..., description="Example: -553173"),
    units: str = Query("metric"),
    children_number: int = Query(0, ge=0),
    locale: str = Query("en-gb"),
    pets_allowed: bool = Query(
        False,
        description=(
            "When true, applies BOOKING_PET_CATEGORIES_FILTER_IDS from .env unless ``dogs`` is set."
        ),
    ),
    dogs: str | None = Query(
        None,
        description=(
            "Booking.com ``categories_filter_ids`` value from RapidAPI docs (e.g. ``hotelfacility::…``). "
            "Do **not** pass the literal word ``dogs``—omit this param and use ``pets_allowed=true`` plus "
            "``BOOKING_PET_CATEGORIES_FILTER_IDS`` in ``.env``, or paste the real filter string here."
        ),
    ),
    children_ages: str | None = Query(None, description="Comma-separated ages, e.g. 5,0"),
    include_adjacency: bool = Query(True),
    filter_by_currency: str = Query("AED"),
    order_by: str = Query("popularity"),
    checkin_date: str = Query(..., description="Format: YYYY-MM-DD"),
    checkout_date: str = Query(..., description="Format: YYYY-MM-DD"),
    room_number: int = Query(1, ge=1),
    adults_number: int = Query(1, ge=1),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    settings = get_settings()
    # Passing dogs=dogs in the query string sends the invalid filter "dogs" to Booking.com; treat as unset.
    dogs_filter = None if dogs is None or dogs.strip().lower() == "dogs" else dogs.strip()

    if dogs_filter is not None:
        cats = dogs_filter
    elif pets_allowed:
        cats = settings.booking_pet_categories_filter_ids
    else:
        cats = None

    try:
        return service.search_hotels(
            page_number=page_number,
            dest_type=dest_type,
            dest_id=dest_id,
            units=units,
            children_number=children_number,
            locale=locale,
            categories_filter_ids=cats,
            children_ages=children_ages,
            include_adjacency=include_adjacency,
            filter_by_currency=filter_by_currency,
            order_by=order_by,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            room_number=room_number,
            adults_number=adults_number,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/flights/search")
async def search_flights(
    depart_date: str = Query(..., description="Format: YYYY-MM-DD"),
    from_code: str = Query(..., description="Example: ONT.AIRPORT"),
    to_code: str = Query(..., description="Example: NYC.CITY"),
    adults: int = Query(1, ge=1),
    locale: str = Query("en-gb"),
    page_number: int = Query(0, ge=0),
    currency: str = Query("AED"),
    order_by: str = Query("BEST"),
    flight_type: str = Query("ONEWAY"),
    cabin_class: str = Query("ECONOMY"),
    children_ages: str | None = Query(None, description="Comma-separated ages, e.g. 5,0"),
    return_date: str | None = Query(None, description="Format: YYYY-MM-DD"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    try:
        return service.search_flights(
            depart_date=depart_date,
            from_code=from_code,
            to_code=to_code,
            adults=adults,
            locale=locale,
            page_number=page_number,
            currency=currency,
            order_by=order_by,
            flight_type=flight_type,
            cabin_class=cabin_class,
            children_ages=children_ages,
            return_date=return_date,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
