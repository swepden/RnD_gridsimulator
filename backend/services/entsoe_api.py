# backend/services/entsoe_api.py
import requests
import datetime
# import xml.etree.ElementTree as ET
from . import data_store # Import the cache module

# Replace with your actual ENTSO-E API key
API_TOKEN = "6fd02047-1026-45e4-adfc-0471d477ffc0" # IMPORTANT: Replace with a real key for actual calls
BASE_URL = "https://transparency.entsoe.eu/api"
DEFAULT_CACHE_TTL_ENTSOE = 15 * 60 # 15 minutes for ENTSO-E data

def parse_entsoe_generation_xml(xml_str: str, region_for_dummy: str = "generic") -> dict:
    """Parses ENTSO-E XML response for generation data per energy type.
    If xml_str is empty, returns dummy data."""
    if not xml_str: # Generate dummy data if no XML string is provided
        print(f"Generating dummy ENTSO-E data for region: {region_for_dummy} because no XML provided.")
        return {
            "region": region_for_dummy,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "production": {
                "solar": 1200.0, "wind": 3400.5, "nuclear": 5000.0,
                "fossil_gas": 1000.0, "fossil_coal": 800.0, "fossil_oil": 500.0, # More specific fossil types
                "hydro": 1800.0, "hydrogen": 0.0, "biomass": 300.0, "other": 100.0,
                # Ensure all keys from EMISSION_FACTORS_GCO2_KWH in simulation.py are covered if possible
            },
            "consumption": 13000.0,
            "price": 85.5, # EUR/MWh
            "co2_intensity": 200.0, # g CO2 per kWh
            "data_source": "dummy_parsed_xml"
        }

    # Actual XML parsing logic would go here.
    # For now, if xml_str is somehow not empty but we are in dummy mode, still return something structured.
    print(f"Attempting to parse actual XML for ENTSO-E (currently placeholder) for region {region_for_dummy}")
    # This part needs a real implementation based on ENTSO-E XML structure.
    # Example: root = ET.fromstring(xml_str) etc.
    # Fallback to dummy if parsing fails or not implemented.
    parsed_data = {
        "region": region_for_dummy, # This should be extracted or passed correctly
        "timestamp": datetime.datetime.utcnow().isoformat(), # Should come from data
        "production": {"parsed_fossil": 1500.0, "parsed_renewable": 2500.0}, # Example
        "consumption": 4000.0,
        "price": 70.0,
        "co2_intensity": 150.0,
        "data_source": "parsed_xml_placeholder"
    }
    return parsed_data


def fetch_current_data(region: str, use_cache: bool = True) -> dict:
    """
    Fetches current generation mix, consumption, and electricity price for a region.
    Uses ENTSO-E API or cache. Region should be an EIC code for real API calls.
    """
    cache_key = f"entsoe_data_{region}"
    if use_cache:
        cached_data = data_store.get_cache(cache_key)
        if cached_data:
            # Optionally, add a flag to indicate it's from cache
            # cached_data["data_source"] = "cache"
            return cached_data

    print(f"ENTSO-E API: No cache or cache expired for {region}. Fetching new data.")

    # Construct params for actual API call (using EIC codes for region)
    # This is a simplified representation. Real EIC codes are needed.
    # Example EIC for Germany: "10YDE-RWENET---I"
    # For testing, we might map "Europe" or "SE" to a known EIC code if available,
    # otherwise, the API call will likely fail without a valid EIC.

    # Using a placeholder EIC if region is a common name, for testing structure.
    # A mapping from common names to EIC codes would be needed for robust use.
    region_eic = region # Assume 'region' is already the EIC code.

    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=1) # Fetch data for the last hour

    # Parameters for 'Actual Generation per Production Type' (documentType A75)
    params_generation = {
        "documentType": "A75",
        "processType": "A16", # Realised
        "in_Domain": region_eic, # Area EIC code
        "periodStart": start_time.strftime('%Y%m%d%H00'), # YYYYMMDDHH00
        "periodEnd": end_time.strftime('%Y%m%d%H00'),     # YYYYMMDDHH00
        "securityToken": API_TOKEN
    }

    # This is where the actual API call would happen.
    # For now, we'll simulate it and return dummy data if API_TOKEN is placeholder.
    if API_TOKEN == "YOUR_ENTSOE_API_KEY_HERE" or not API_TOKEN:
        print("ENTSO-E API: API_TOKEN not configured. Returning dummy data instead of making a real call.")
        api_data = parse_entsoe_generation_xml("", region_for_dummy=region) # Pass region to dummy parser
        api_data["message"] = "Dummy data because ENTSO-E API key is not set."
    else:
        print(f"ENTSO-E API: Attempting REAL API call to {BASE_URL} with params: {params_generation}")
        try:
            # TODO: Implement calls for other data types: consumption (A65), prices (A44) etc.
            # and merge them into a single dictionary.
            resp_generation = requests.get(BASE_URL, params=params_generation, timeout=10)
            resp_generation.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            xml_data_generation = resp_generation.text

            # The parse_entsoe_generation_xml needs to be robust to handle real XML.
            api_data = parse_entsoe_generation_xml(xml_data_generation, region_for_dummy=region)
            api_data["message"] = "Successfully fetched REAL data from ENTSO-E (generation part only)."
            # Here you would also fetch other data like consumption, prices, and merge them.
            # For example:
            # api_data["consumption"] = fetch_total_load(region_eic, start_time, end_time)
            # api_data["price"] = fetch_day_ahead_prices(region_eic, start_time, end_time)
            # api_data["co2_intensity"] = calculate_co2_from_mix(api_data["production"], api_data["consumption"])

        except requests.exceptions.RequestException as e:
            print(f"ENTSO-E API Error for {region}: {e}")
            api_data = parse_entsoe_generation_xml("", region_for_dummy=region) # Fallback to dummy
            api_data["message"] = f"ENTSO-E API request failed: {e}. Returning dummy data."
        except Exception as e_parse: # Catch parsing errors or other issues
            print(f"ENTSO-E Data Processing Error for {region}: {e_parse}")
            api_data = parse_entsoe_generation_xml("", region_for_dummy=region) # Fallback to dummy
            api_data["message"] = f"ENTSO-E data processing failed: {e_parse}. Returning dummy data."

    if use_cache and api_data: # api_data might be None if parsing fails and returns None
        data_store.set_cache(cache_key, api_data, ttl_seconds=DEFAULT_CACHE_TTL_ENTSOE)

    return api_data

# Placeholder for Nord Pool - This would also need caching and proper API implementation
def fetch_nordpool_data(region: str, use_cache: bool = True) -> dict:
    cache_key = f"nordpool_data_{region}"
    if use_cache:
        cached_data = data_store.get_cache(cache_key)
        if cached_data:
            return cached_data

    print(f"Nord Pool API: Fetching new data for {region} (dummy placeholder).")
    # Actual Nord Pool API call simulation
    data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "region": region,
        "nordpool_price_EUR_MWh": 75.0,
        "production_sources": {"hydro_nordic": 500, "wind_nordic": 600},
        "data_source": "dummy_nordpool_api"
    }
    if use_cache:
        data_store.set_cache(cache_key, data, ttl_seconds=DEFAULT_CACHE_TTL_ENTSOE)
    return data

if __name__ == '__main__':
    print("Testing entsoe_api.py with caching...")
    # Test with a placeholder region/EIC. For real tests, use a valid EIC.
    test_region_eic = "10YDE-RWENET---I" # Example EIC for Germany (TransnetBW)

    print("\n--- First call (should fetch and cache) ---")
    data1 = fetch_current_data(test_region_eic)
    print(f"Data for {test_region_eic}: {data1.get('message', 'N/A')}, Source: {data1.get('data_source', 'N/A')}")

    print("\n--- Second call (should hit cache) ---")
    data2 = fetch_current_data(test_region_eic)
    print(f"Data for {test_region_eic}: {data2.get('message', 'N/A')}, Source: {data2.get('data_source', 'N/A')}")
    # Check if it's indeed from cache (would require modifying get_cache to signal this or checking logs)
    # For this test, we rely on the print statements from data_store.py

    print("\n--- Test Nord Pool (dummy) ---")
    nordpool_data = fetch_nordpool_data("FI") # Finland
    print(f"Nord Pool data for FI: Price {nordpool_data.get('nordpool_price_EUR_MWh')}, Source: {nordpool_data.get('data_source', 'N/A')}")
    nordpool_data_cached = fetch_nordpool_data("FI")
    print(f"Nord Pool data for FI (cached): Price {nordpool_data_cached.get('nordpool_price_EUR_MWh')}, Source: {nordpool_data_cached.get('data_source', 'N/A')}")

    print("\n--- Clearing cache for ENTSO-E test region ---")
    data_store.clear_cache(f"entsoe_data_{test_region_eic}")
    print("\n--- Third call (should fetch again after cache clear) ---")
    data3 = fetch_current_data(test_region_eic)
    print(f"Data for {test_region_eic}: {data3.get('message', 'N/A')}, Source: {data3.get('data_source', 'N/A')}")

    print("\nENTSO-E API test finished.")
