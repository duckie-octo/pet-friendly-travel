import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    amadeus_client_id: str | None = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret: str | None = os.getenv("AMADEUS_CLIENT_SECRET")
    amadeus_hostname: str = os.getenv("AMADEUS_HOSTNAME", "test")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fallback.db")
    # Optional split: user accounts vs trip/booking data (Render: userprofile + Pet_friendly_travel)
    userprofile_database_url: str = os.getenv(
        "USERPROFILE_DATABASE_URL",
        os.getenv("DATABASE_URL", "sqlite:///./fallback.db"),
    )
    trips_database_url: str = os.getenv(
        "TRIPS_DATABASE_URL",
        os.getenv("DATABASE_URL", "sqlite:///./fallback.db"),
    )
    rapidapi_key: str | None = os.getenv("RAPIDAPI_KEY")
    geoapify_api_key: str | None = os.getenv("GEOAPIFY_API_KEY")
    # Booking.com RapidAPI uses `categories_filter_ids`, not a pets_allowed flag. Set this to the pets filter
    # string from RapidAPI docs for v1/hotels/search, e.g. BOOKING_PET_CATEGORIES_FILTER_IDS="hotelfacility::..."
    booking_pet_categories_filter_ids: str | None = os.getenv("BOOKING_PET_CATEGORIES_FILTER_IDS")
    # Path segment for hotel detail/description on RapidAPI (response includes property_highlight_strip, facilities_block).
    booking_hotel_detail_path: str = os.getenv("BOOKING_HOTEL_DETAIL_PATH", "v1/hotels/description")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "3600")
    )

def get_settings() -> Settings:
    return Settings()
