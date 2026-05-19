import json
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings


class GeoapifyError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class GeoapifyClient:
    BASE = "https://api.geoapify.com"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_destinations(
        self,
        city: str,
        country: str,
        limit: int = 20,
        pets_allowed: bool = True,
        categories: str = "commercial.supermarket",
        lang: str = "en",
    ) -> dict:
        place = self._geocode_city(city, country)
        spatial_filter = self._spatial_filter(place)
        conditions = "dogs.yes" if pets_allowed else None
        return self._search_places(
            categories=categories,
            spatial_filter=spatial_filter,
            limit=limit,
            conditions=conditions,
            lang=lang,
        )

    def _geocode_city(self, city: str, country: str) -> dict:
        params = {
            "city": city,
            "type": "city",
            "limit": "1",
            "format": "json",
            "apiKey": self.api_key,
        }
        if country:
            params["text"] = f"{city}, {country}"

        payload = self._get("/v1/geocode/search", params)
        results = payload.get("results") or []
        if not results:
            raise GeoapifyError(404, f"No city found for {city!r}, {country!r}")
        return results[0]

    def _spatial_filter(self, geocode_hit: dict) -> str:
        place_id = geocode_hit.get("place_id")
        if not place_id:
            raise GeoapifyError(502, "Geocode result missing place_id")
        return f"place:{place_id}"

    def _search_places(
        self,
        categories: str,
        spatial_filter: str,
        limit: int,
        conditions: str | None,
        lang: str,
    ) -> dict:
        params = {
            "categories": categories,
            "filter": spatial_filter,
            "limit": str(limit),
            "apiKey": self.api_key,
        }
        if conditions:
            params["conditions"] = conditions
        if lang:
            params["lang"] = lang
        return self._get("/v2/places", params)

    def _get(self, path: str, params: dict[str, str]) -> dict:
        url = f"{self.BASE}{path}?{urlencode(params)}"
        request = Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GeoapifyError(exc.code, body or str(exc)) from exc
        except URLError as exc:
            raise GeoapifyError(500, "Failed to connect to Geoapify.") from exc


@lru_cache(maxsize=1)
def get_geoapify_client() -> GeoapifyClient:
    settings = get_settings()
    if not settings.geoapify_api_key:
        raise GeoapifyError(500, "GEOAPIFY_API_KEY is not configured.")
    return GeoapifyClient(api_key=settings.geoapify_api_key)
