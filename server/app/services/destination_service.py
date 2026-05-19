from app.core.geoapify_client import GeoapifyClient


class DestinationService:
    def __init__(self, geoapify_client: GeoapifyClient) -> None:
        self.geoapify = geoapify_client

    def get_destinations(
        self,
        city: str,
        country: str,
        limit: int = 20,
        pets_allowed: bool = True,
        categories: str = "commercial.supermarket",
    ) -> dict:
        return self.geoapify.get_destinations(
            city, country, limit, pets_allowed, categories
        )
