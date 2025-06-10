# backend/api/routes_data.py
from fastapi import APIRouter, HTTPException
from services import entsoe_api # Uncommented to allow import

router = APIRouter()

@router.get("/realtime")
def get_realtime_data(region: str = "Europe"):
    """
    Hämta realtids eldata för angiven region (land eller område).
    Returnerar exempelvis produktion per energikälla, förbrukning, CO2
intensitet och elpris.
    """
    try:
        # data = entsoe_api.fetch_current_data(region) # Kept commented
        # Using dummy data directly from entsoe_api for now
        data = entsoe_api.parse_entsoe_generation_xml("") # Call the parser directly for dummy data
        data["region"] = region # Add region to the dummy data
        # Add a message indicating that this is dummy data
        data["message"] = "Successfully fetched dummy real-time data. ENTSO-E integration pending API key and full implementation."

        # Example of how Nord Pool data could be fetched and potentially merged or provided separately
        # nordpool_data = entsoe_api.fetch_nordpool_data(region)
        # data["nordpool_info"] = nordpool_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kunde inte hämta data: {str(e)}")
    return data
