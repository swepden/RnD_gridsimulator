# backend/services/weather_api.py
import requests
import datetime
from . import data_store # Import the cache module

# NASA POWER API base URL
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
DEFAULT_CACHE_TTL_WEATHER = 60 * 60 # 1 hour for weather data, as it's less volatile than spot electricity data

# Copernicus CDS API details would go here if used directly
# COPERNICUS_API_URL = "..."
# COPERNICUS_API_KEY = "YOUR_COPERNICUS_API_KEY_HERE"

def get_solar_irradiation(lat: float, lon: float, use_cache: bool = True) -> float:
    """
    Fetches solar irradiation (e.g., W/m^2) for a given latitude and longitude.
    Uses NASA POWER API as an example, with caching.
    """
    cache_key = f"weather_solar_{lat}_{lon}"
    if use_cache:
        cached_data = data_store.get_cache(cache_key)
        if cached_data is not None: # Check for not None, as 0.0 is a valid irradiation
            return cached_data

    print(f"Weather API: No cache for solar at ({lat},{lon}). Fetching new data.")

    # Parameters for NASA POWER API
    # For real-time, you'd fetch for the latest available hour.
    # For climatology (typical conditions), params change.
    # This example will fetch data for the previous day as a simple proxy for "recent" data.
    # A robust implementation would handle timezones and data availability lags.
    # For this prototype, we'll keep it simple and mostly rely on dummy data path.

    # params = {
    #     "parameters": "ALLSKY_SFC_SW_DWN",
    #     "community": "RE",
    #     "longitude": lon,
    #     "latitude": lat,
    #     "format": "JSON",
    #     "start": (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime('%Y%m%d'), # Example: data from 2 days ago to yesterday
    #     "end": (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    # }

    # SIMULATING API CALL OR USING DUMMY DATA
    # Replace this section with actual requests.get(NASA_POWER_BASE_URL, params=params) when ready
    irradiation_value = 600.0  # Default dummy value in W/m^2
    print(f"Weather API: Using DUMMY solar irradiation data: {irradiation_value} W/m^2 for ({lat},{lon}).")
    # try:
    #     # print(f"Attempting NASA POWER API call for solar: {NASA_POWER_BASE_URL} with params {params}")
    #     # response = requests.get(NASA_POWER_BASE_URL, params=params, timeout=10)
    #     # response.raise_for_status()
    #     # api_data = response.json()
    #     # # The actual path to data depends on NASA POWER JSON structure, which can be nested.
    #     # # Example: api_data['properties']['parameter']['ALLSKY_SFC_SW_DWN']['YYYYMMDDHH'] or a mean value.
    #     # # Taking the first value if it's a dictionary of times.
    #     # if isinstance(api_data['properties']['parameter']['ALLSKY_SFC_SW_DWN'], dict):
    #     #    irradiation_value = next(iter(api_data['properties']['parameter']['ALLSKY_SFC_SW_DWN'].values()), 250.0)
    #     # else: # if it's a single value (e.g. for climatology)
    #     #    irradiation_value = api_data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
    #     print(f"NASA POWER API (solar) success for ({lat},{lon}). Raw: {api_data}")
    # except requests.exceptions.RequestException as e:
    #     print(f"NASA POWER API (solar) error for ({lat},{lon}): {e}. Using fallback dummy value.")
    #     irradiation_value = 250.0  # Fallback dummy value
    # except (KeyError, TypeError) as e:
    #     print(f"NASA POWER API (solar) response parsing error for ({lat},{lon}): {e}. Using fallback dummy value.")
    #     irradiation_value = 200.0

    if use_cache:
        data_store.set_cache(cache_key, irradiation_value, ttl_seconds=DEFAULT_CACHE_TTL_WEATHER)

    return irradiation_value


def get_wind_speed(lat: float, lon: float, height_m: int = 100, use_cache: bool = True) -> float:
    """
    Fetches wind speed (e.g., m/s) for a given latitude, longitude, and height.
    Uses NASA POWER API as an example, with caching.
    """
    # NASA POWER provides WS2M, WS10M, WS50M. For 100m, one might need to interpolate or use WS50M as proxy.
    # For simplicity, if height is 100m, we'll request WS50M.
    nasa_height_param = height_m if height_m in [2, 10, 50] else 50
    cache_key = f"weather_wind_{lat}_{lon}_{nasa_height_param}m"

    if use_cache:
        cached_data = data_store.get_cache(cache_key)
        if cached_data is not None: # Check for not None, as 0.0 is a valid wind speed
            return cached_data

    print(f"Weather API: No cache for wind at ({lat},{lon}), {nasa_height_param}m. Fetching new data.")

    # params = {
    #     "parameters": f"WS{nasa_height_param}M",
    #     "community": "RE",
    #     "longitude": lon,
    #     "latitude": lat,
    #     "format": "JSON",
    #     "start": (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime('%Y%m%d'),
    #     "end": (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    # }

    # SIMULATING API CALL OR USING DUMMY DATA
    wind_speed_value = 12.0  # Default dummy value in m/s
    print(f"Weather API: Using DUMMY wind speed data: {wind_speed_value} m/s for ({lat},{lon}) at {nasa_height_param}m.")
    # try:
    #     # print(f"Attempting NASA POWER API call for wind: {NASA_POWER_BASE_URL} with params {params}")
    #     # response = requests.get(NASA_POWER_BASE_URL, params=params, timeout=10)
    #     # response.raise_for_status()
    #     # api_data = response.json()
    #     # if isinstance(api_data['properties']['parameter'][f"WS{nasa_height_param}M"], dict):
    #     #    wind_speed_value = next(iter(api_data['properties']['parameter'][f"WS{nasa_height_param}M"].values()), 5.0)
    #     # else:
    #     #    wind_speed_value = api_data['properties']['parameter'][f"WS{nasa_height_param}M"]
    #     print(f"NASA POWER API (wind) success for ({lat},{lon}). Raw: {api_data}")
    # except requests.exceptions.RequestException as e:
    #     print(f"NASA POWER API (wind) error for ({lat},{lon}): {e}. Using fallback dummy value.")
    #     wind_speed_value = 5.0  # Fallback dummy value
    # except (KeyError, TypeError) as e:
    #     print(f"NASA POWER API (wind) response parsing error for ({lat},{lon}): {e}. Using fallback dummy value.")
    #     wind_speed_value = 4.0

    if use_cache:
        data_store.set_cache(cache_key, wind_speed_value, ttl_seconds=DEFAULT_CACHE_TTL_WEATHER)

    return wind_speed_value


def get_copernicus_capacity_factors(region: str, plant_type: str, use_cache: bool = True) -> float:
    """
    Placeholder for fetching regional capacity factors from Copernicus Climate Data Store (CDS).
    Includes dummy data and caching.
    """
    cache_key = f"copernicus_cf_{region}_{plant_type}"
    if use_cache:
        cached_data = data_store.get_cache(cache_key)
        if cached_data is not None:
            return cached_data

    print(f"Weather API (Copernicus): No cache for CF for {plant_type} in {region}. Fetching new data (dummy).")

    # Dummy implementation for Copernicus data
    cf_value = 0.0
    if plant_type.lower() == "solar":
        cf_value = 0.18  # Example average capacity factor for solar
    elif plant_type.lower() == "wind":
        cf_value = 0.35  # Example average capacity factor for onshore wind

    print(f"Weather API (Copernicus): Using DUMMY CF value: {cf_value} for {plant_type} in {region}.")

    if use_cache:
        data_store.set_cache(cache_key, cf_value, ttl_seconds=DEFAULT_CACHE_TTL_WEATHER * 24) # Longer TTL for CFs

    return cf_value

if __name__ == '__main__':
    print("Testing weather_api.py with caching...")
    test_lat, test_lon = 52.5, 13.4 # Berlin

    print("\n--- Solar Irradiation ---")
    s1 = get_solar_irradiation(test_lat, test_lon)
    print(f"Solar (1st call): {s1} W/m^2")
    s2 = get_solar_irradiation(test_lat, test_lon)
    print(f"Solar (2nd call, should be cached): {s2} W/m^2")
    data_store.clear_cache(f"weather_solar_{test_lat}_{test_lon}")
    s3 = get_solar_irradiation(test_lat, test_lon)
    print(f"Solar (3rd call, after clear, should fetch again): {s3} W/m^2")

    print("\n--- Wind Speed ---")
    w1 = get_wind_speed(test_lat, test_lon, height_m=50)
    print(f"Wind @50m (1st call): {w1} m/s")
    w2 = get_wind_speed(test_lat, test_lon, height_m=50)
    print(f"Wind @50m (2nd call, should be cached): {w2} m/s")

    print("\n--- Copernicus Capacity Factors (Dummy) ---")
    cf_solar1 = get_copernicus_capacity_factors("DE", "solar")
    print(f"Copernicus Solar CF for DE (1st call): {cf_solar1}")
    cf_solar2 = get_copernicus_capacity_factors("DE", "solar")
    print(f"Copernicus Solar CF for DE (2nd call, should be cached): {cf_solar2}")

    print("\nWeather API test finished.")
