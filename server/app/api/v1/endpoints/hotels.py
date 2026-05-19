from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.hotel import PetFriendlyHotel, PetFriendlyHotelsResponse

router = APIRouter(prefix="", tags=["hotels"])

_PET_FRIENDLY_SQL = """
SELECT
    Hotel_Code,
    Hotel_Name,
    Address,
    City,
    Zip_Code,
    Country,
    Email,
    Phone_Number,
    Pet_Friendly,
    Pet_Fee_Per_Night,
    Max_Pets
FROM Hotel_Master
WHERE Pet_Friendly = 1
"""


def _row_to_hotel(row: dict) -> PetFriendlyHotel:
    return PetFriendlyHotel(
        Hotel_Code=row["Hotel_Code"],
        Hotel_Name=row["Hotel_Name"],
        Address=row["Address"],
        City=row["City"],
        Zip_Code=row["Zip_Code"],
        Country=row["Country"],
        Email=row["Email"],
        Phone_Number=row["Phone_Number"],
        Pet_Friendly=bool(row["Pet_Friendly"]),
        Pet_Fee_Per_Night=row["Pet_Fee_Per_Night"],
        Max_Pets=row["Max_Pets"],
    )


@router.get(
    "/hotels/pet-friendly",
    response_model=PetFriendlyHotelsResponse,
    summary="List pet-friendly hotels from the sample database",
)
def list_pet_friendly_hotels(
    city: str | None = Query(
        default=None,
        description="Optional filter: exact city name (case-sensitive match to seeded data).",
    ),
    country: str | None = Query(
        default=None,
        description="Optional filter: exact country name (case-sensitive match to seeded data).",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns rows from `Hotel_Master` where `Pet_Friendly` is set.
    Re-run `init_db.sql` (or equivalent) if columns are missing on an older database file.
    """
    sql = _PET_FRIENDLY_SQL
    params: dict[str, str] = {}
    if city is not None:
        sql += " AND City = :city"
        params["city"] = city
    if country is not None:
        sql += " AND Country = :country"
        params["country"] = country
    sql += " ORDER BY Country, City, Hotel_Name"

    try:
        result = db.execute(text(sql), params)
        rows = [dict(r._mapping) for r in result]
    except OperationalError as exc:
        if "no such column" in str(exc).lower():
            raise HTTPException(
                status_code=503,
                detail="Hotel_Master is missing pet columns. Recreate the DB from app/schemas/init_db.sql.",
            ) from exc
        raise

    hotels = [_row_to_hotel(r) for r in rows]
    return PetFriendlyHotelsResponse(Count=len(hotels), Hotels=hotels)
