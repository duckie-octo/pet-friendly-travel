# destination.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.geoapify_client import GeoapifyError, get_geoapify_client
from app.services.destination_service import DestinationService

router = APIRouter(tags=["destinations"])

def get_destination_service() -> DestinationService:
    return DestinationService(get_geoapify_client())

@router.get("/destinations")
async def get_destinations(
    city: str,
    country: str,
    limit: int = Query(20, ge=1, le=500),
    pets_allowed: bool = True,
    categories: str = "commercial.supermarket",
    service: DestinationService = Depends(get_destination_service),
):
    try:
        return service.get_destinations(
            city, country, limit, pets_allowed, categories
        )
    except GeoapifyError as err:
        raise HTTPException(status_code=err.status_code, detail=err.detail) from err