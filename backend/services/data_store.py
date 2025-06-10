# backend/services/data_store.py
import time
import threading

# Simple in-memory cache with a lock for thread safety
_CACHE = {}
_CACHE_LOCK = threading.Lock()
DEFAULT_TTL_SECONDS = 5 * 60  # 5 minutes

def set_cache(key: str, value: any, ttl_seconds: int = DEFAULT_TTL_SECONDS):
    """
    Stores a value in the cache with a specific Time-To-Live (TTL).
    """
    with _CACHE_LOCK:
        expires_at = time.time() + ttl_seconds
        _CACHE[key] = {"value": value, "expires_at": expires_at}
        print(f"Cache: SET key='{key}', TTL={ttl_seconds}s")

def get_cache(key: str) -> any:
    """
    Retrieves a value from the cache if it exists and has not expired.
    Returns None if the key is not found or the item has expired.
    """
    with _CACHE_LOCK:
        item = _CACHE.get(key)
        if item:
            if time.time() < item["expires_at"]:
                print(f"Cache: HIT key='{key}'")
                return item["value"]
            else:
                print(f"Cache: EXPIRED key='{key}'")
                # Item has expired, remove it from cache
                del _CACHE[key]
        else:
            print(f"Cache: MISS key='{key}'")
        return None

def clear_cache(key: str = None):
    """
    Clears a specific key or the entire cache if no key is provided.
    """
    with _CACHE_LOCK:
        if key:
            if key in _CACHE:
                del _CACHE[key]
                print(f"Cache: CLEARED key='{key}'")
            else:
                print(f"Cache: Key '{key}' not found for clearing.")
        else:
            _CACHE.clear()
            print("Cache: CLEARED all keys.")

# Example of how other services might use this cache:
# (This part is illustrative and would be integrated into entsoe_api.py, weather_api.py etc.)

# from . import entsoe_api as real_entsoe_api # To avoid circular import if used directly

# def get_cached_entsoe_data(region: str):
#     cache_key = f"entsoe_data_{region}"
#     data = get_cache(cache_key)
#     if data is None:
#         # data = real_entsoe_api.fetch_current_data(region) # Actual API call
#         # Forcing dummy data for illustration if real_entsoe_api is not structured for this yet
#         data = {"source": "dummy_entsoe_for_cache_example", "region": region, "timestamp": time.time()}
#         if data:
#             set_cache(cache_key, data)
#     return data

if __name__ == '__main__':
    print("Testing data_store.py cache functionality...")

    # Test set and get
    set_cache("test_key1", {"data": "some value"}, ttl_seconds=2)
    print(f"Get test_key1 immediately: {get_cache('test_key1')}")

    time.sleep(1)
    print(f"Get test_key1 after 1s: {get_cache('test_key1')}")

    time.sleep(1.5) # Total > 2s, should be expired
    print(f"Get test_key1 after >2.5s (should be expired): {get_cache('test_key1')}")
    print(f"Cache content after expiry: {_CACHE}") # Should be empty or key removed

    # Test TTL
    set_cache("test_key2", "another value", ttl_seconds=1)
    time.sleep(1.1)
    if get_cache("test_key2") is None:
        print("test_key2 correctly expired and returned None.")
    else:
        print("Error: test_key2 should have expired.")

    # Test clear specific key
    set_cache("test_key3", "to_be_cleared")
    set_cache("test_key4", "to_remain")
    print(f"Cache before specific clear: {_CACHE}")
    clear_cache("test_key3")
    if get_cache("test_key3") is None and get_cache("test_key4") is not None:
        print("Specific key 'test_key3' cleared successfully.")
    else:
        print("Error in clearing specific key.")
    print(f"Cache after specific clear: {_CACHE}")

    # Test clear all
    set_cache("test_key5", "temp1")
    set_cache("test_key6", "temp2")
    print(f"Cache before clear all: {_CACHE}")
    clear_cache()
    if not _CACHE: # Check if cache is empty
        print("Cache cleared successfully.")
    else:
        print(f"Error: Cache not empty after clear_cache(): {_CACHE}")

    print("Cache test finished.")
