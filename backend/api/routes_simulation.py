# backend/api/routes_simulation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# Use a relative import so the module works when the package is imported as
# ``backend`` from the project root.
from ..services import simulation
from typing import Optional

router = APIRouter()

class NewPlant(BaseModel):
    name: str
    type: str  # e.g., "solar", "wind", "nuclear", "hydrogen"
    capacity: float  # MW
    start_date: str  # ISO-format
    lat: float
    lon: float
    region: str

class RemovePlant(BaseModel):
    name: str # Name of the plant to remove
    type: str # Type of plant, e.g. "nuclear"
    region: str
    capacity: Optional[float] = None # MW to remove. If None, remove all capacity of this named plant or type.

@router.post("/add")
def simulate_new_capacity(plant: NewPlant):
    """
    Add a new virtual power plant and calculate its effect on the energy system.
    Returns updated data (production per source, emissions, prices, etc.).
    """
    try:
        print(f"Simulate ADD route: Received plant: {plant.dict()}")
        base_data = simulation.get_base_data(plant.region)
        print(f"Simulate ADD route: Base data for {plant.region}: {base_data}")
        result_data = simulation.run_simulation(base_data, plant)
        print(f"Simulate ADD route: Result data for {plant.region} after adding {plant.name}: {result_data}")
        return result_data
    except Exception as e:
        print(f"Error in /simulate/add: {e}")
        raise HTTPException(status_code=500, detail=f"Kunde inte köra simmulering för att lägga till kraftverk: {str(e)}")

@router.post("/remove")
def simulate_remove_capacity(plant: RemovePlant):
    """
    Virtually remove an existing power plant and calculate its effect.
    Returns updated data.
    """
    try:
        print(f"Simulate REMOVE route: Received plant spec: {plant.dict()}")
        base_data = simulation.get_base_data(plant.region)
        print(f"Simulate REMOVE route: Base data for {plant.region}: {base_data}")
        # The run_remove_simulation function needs to handle the 'name' and 'type' to identify
        # what to remove, and 'capacity' for how much.
        result_data = simulation.run_remove_simulation(base_data, plant)
        print(f"Simulate REMOVE route: Result data for {plant.region} after removing {plant.name}: {result_data}")
        return result_data
    except Exception as e:
        print(f"Error in /simulate/remove: {e}")
        raise HTTPException(status_code=500, detail=f"Kunde inte köra simmulering för att ta bort kraftverk: {str(e)}")
