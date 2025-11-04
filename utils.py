import requests
from functools import lru_cache

DEFAULT_HEADERS = {"User-Agent": "OpenAPI-Lab/1.0"}

def safe_get_json(url, params=None, timeout=15):
    r = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json()

@lru_cache(maxsize=128)
def geocode_city(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    data = safe_get_json(url, {"name": city, "count": 1})
    results = data.get("results") or []
    if not results:
        return None
    item = results[0]
    return {
        "name": item["name"],
        "lat": item["latitude"],
        "lon": item["longitude"],
        "country": item.get("country", "")
    }

def fetch_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 3, "timezone": "auto"
    }
    return safe_get_json(url, params)

def fetch_artworks(query: str, page: int = 1, limit: int = 12):
    url = "https://api.artic.edu/api/v1/artworks/search"
    params = {
        "q": query, "page": page, "limit": limit,
        "fields": "id,title,artist_display,date_display,image_id"
    }
    return safe_get_json(url, params)

def build_art_image_url(image_id: str, size=400):
    if not image_id:
        return None
    return f"https://www.artic.edu/iiif/2/{image_id}/full/{size},/0/default.jpg"

def fetch_stooq_csv(symbol: str = "^ks200"):
    url = "https://stooq.com/q/d/l/"
    params = {"s": symbol, "i": "d"}
    r = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=15)
    r.raise_for_status()
    return r.text
