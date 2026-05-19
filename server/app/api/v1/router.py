from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.booking import router as booking_router
from app.api.v1.endpoints.destination import router as destination_router
from app.api.v1.endpoints.flights import router as flights_router
from app.api.v1.endpoints.hotels import router as hotels_router
from app.api.v1.endpoints.rapidapi import router as rapidapi_router
from app.api.v1.endpoints.travel import router as travel_router
from app.api.v1.endpoints.trips import router as trips_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(booking_router)
api_router.include_router(flights_router)
api_router.include_router(hotels_router)
api_router.include_router(travel_router)
api_router.include_router(destination_router)
api_router.include_router(rapidapi_router)
api_router.include_router(trips_router)
