import json
import os
import urllib.error
import urllib.parse
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MAPBOX_GEOCODE_URL = "https://api.mapbox.com/search/geocode/v6/forward"


def generateLatLng(body):
    """
    Forward-geocode an address with Mapbox Geocoding v6.

    body: dict with at least "address" and optionally "city"
    returns: {"latitude": float, "longitude": float, "postal_code": str|None}
             or None if geocoding fails / no results
    """
    if not isinstance(body, dict):
        return None

    address = (body.get("address") or "").strip()
    city = (body.get("city") or "").strip()

    if not address and not city:
        return None

    query = ", ".join(part for part in (address, city) if part)
    token = os.environ.get("MAPBOX_TOKEN")
    if not token:
        print("MAPBOX_TOKEN is not set")
        return None

    params = urllib.parse.urlencode(
        {
            "q": query,
            "access_token": token,
            "limit": 1,
            "types": "address,place",
        }
    )
    url = f"{MAPBOX_GEOCODE_URL}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err.code} {http_err.reason}")
        return None
    except urllib.error.URLError as url_err:
        print(f"Connection error occurred: {url_err.reason}")
        return None
    except TimeoutError:
        print("The request timed out.")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None

    features = data.get("features") or []
    if not features:
        print(f"No geocode results for: {query}")
        return None

    feature = features[0]
    coordinates = (feature.get("geometry") or {}).get("coordinates") or []
    if len(coordinates) < 2:
        print(f"Geocode result missing coordinates for: {query}")
        return None

    # GeoJSON order is [longitude, latitude]
    longitude, latitude = coordinates[0], coordinates[1]

    return {
        "latitude": latitude,
        "longitude": longitude,
        "postal_code": _extract_postal_code(feature),
    }


def _extract_postal_code(feature):
    """Pull postcode from Mapbox v6 feature properties when present."""
    properties = feature.get("properties") or {}

    if properties.get("postcode"):
        return str(properties["postcode"])

    context = properties.get("context") or {}
    postcode = context.get("postcode") or {}
    if isinstance(postcode, dict) and postcode.get("name"):
        return str(postcode["name"])

    return None


if __name__ == "__main__":
    sample = {"address": "1600 Amphitheatre Parkway", "city": "Mountain View"}
    print(generateLatLng(sample))
