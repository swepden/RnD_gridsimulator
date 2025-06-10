# backend/services/simulation.py
import copy
from . import weather_api, entsoe_api # Use relative imports for services within the same package

# Default CO2 emission factors (g CO2eq / kWh) - based on IPCC, IEA, or similar.
# These are illustrative and should be refined with more accurate regional data.
EMISSION_FACTORS_GCO2_KWH = {
    "solar": 0, # Lifecycle emissions are non-zero, but operational are near zero
    "wind": 0,  # Operational emissions near zero
    "hydro": 0, # Operational emissions near zero
    "nuclear": 0, # Operational emissions near zero
    "hydrogen": 0, # Assuming "green" hydrogen produced from renewables. "Blue/Grey" hydrogen has emissions.
    "biomass": 230, # Varies greatly depending on source and sustainability
    "geothermal": 45,
    "fossil_gas": 490,
    "fossil_coal": 820,
    "fossil_oil": 650,
    "other": 300, # Generic placeholder
    "default_fossil_mix": 700 # Used if specific fossil type isn't detailed
}

# Average capacity factors (illustrative, should ideally come from more dynamic source or be configurable)
# These are very rough estimates. Real capacity factors vary significantly by location, technology, and time.
DEFAULT_CAPACITY_FACTORS = {
    "solar": 0.15,       # Average over day/year
    "wind": 0.30,        # Onshore average
    "nuclear": 0.90,
    "hydrogen": 0.95,    # Assuming it's a dispatchable source like a fuel cell or turbine
    "hydro": 0.40,       # Varies greatly with rainfall and reservoir levels
    "fossil_gas": 0.7,   # Dispatchable
    "fossil_coal": 0.75, # Baseload/dispatchable
    # other types would also need defaults
}


def get_base_data(region: str) -> dict:
    """Fetches base scenario data for simulation (e.g., latest hour's data for the region)."""
    # In a real system, this might involve more complex logic,
    # like fetching from a data cache or directly from entsoe_api
    print(f"Simulation: Getting base data for region {region} using entsoe_api (dummy).")
    base_data = entsoe_api.fetch_current_data(region) # Uses dummy data from entsoe_api.py

    # Ensure base_data has a "production" dictionary and a "total" within it.
    if "production" not in base_data:
        base_data["production"] = {}

    # Ensure all known energy types have a zero value if not present, for consistent calculations
    # This makes +/- operations easier later.
    for plant_type in list(EMISSION_FACTORS_GCO2_KWH.keys()) + list(DEFAULT_CAPACITY_FACTORS.keys()):
        base_data["production"].setdefault(plant_type, 0.0)

    base_data["production"]["total"] = sum(base_data["production"].get(ptype, 0.0) for ptype in base_data["production"] if ptype != "total")

    if "co2_intensity" not in base_data or base_data.get("co2_intensity") is None:
         base_data["co2_intensity"] = calculate_co2_intensity(base_data["production"], base_data.get("consumption", 0.0))

    if "price" not in base_data or base_data.get("price") is None:
        base_data["price"] = 50.0 # Default price if not available

    if "consumption" not in base_data or base_data.get("consumption") is None:
        base_data["consumption"] = sum(base_data["production"].values()) * 0.9 # Assume some demand if not present

    return base_data


def calculate_new_generation(plant_type: str, capacity: float, lat: float, lon: float) -> float:
    """Calculates expected generation from a new plant based on type, capacity, and location."""
    plant_type_lower = plant_type.lower()
    new_generation = 0.0

    if plant_type_lower == "wind":
        wind_speed = weather_api.get_wind_speed(lat, lon) # m/s (dummy from weather_api)
        # Simplified model: capacity_factor increases with wind speed, capped at 1.0
        # (15 m/s is a strong wind, often near rated speed for many turbines)
        capacity_factor = min(wind_speed / 15.0, 1.0) * DEFAULT_CAPACITY_FACTORS.get("wind", 0.35)
        new_generation = capacity * capacity_factor
    elif plant_type_lower == "solar":
        irradiation = weather_api.get_solar_irradiation(lat, lon) # W/m^2 (dummy from weather_api)
        # Simplified model: capacity_factor increases with irradiation, capped
        # (1000 W/m^2 is strong sunlight)
        capacity_factor = min(irradiation / 1000.0, 1.0) * DEFAULT_CAPACITY_FACTORS.get("solar", 0.18)
        new_generation = capacity * capacity_factor
    elif plant_type_lower == "nuclear":
        new_generation = capacity * DEFAULT_CAPACITY_FACTORS.get("nuclear", 0.9)
    elif plant_type_lower == "hydrogen": # New energy type
        # Assuming hydrogen is used in a dispatchable way (e.g., fuel cell, turbine)
        # Could also have its own capacity factor based on technology or operational mode
        new_generation = capacity * DEFAULT_CAPACITY_FACTORS.get("hydrogen", 0.95)
    elif plant_type_lower in DEFAULT_CAPACITY_FACTORS:
        new_generation = capacity * DEFAULT_CAPACITY_FACTORS[plant_type_lower]
    else:
        # For other types not explicitly modeled with weather or specific CFs, assume a generic high CF or direct output.
        # This could be refined.
        print(f"Warning: Using default capacity factor (1.0) for plant type '{plant_type_lower}' as it's not specifically handled.")
        new_generation = capacity * 1.0 # Default to full capacity if type is unknown or unmodelled for CF

    return new_generation


def calculate_co2_intensity(production_mix: dict, total_demand: float) -> float:
    """Calculates CO2 intensity (g CO2/kWh) based on the production mix and demand."""
    total_emissions_g = 0.0
    total_generation_kwh = 0.0 # Assuming MW values are effectively MWh/h, so kWh for calculations

    for plant_type, generation_mw in production_mix.items():
        if plant_type == "total" or generation_mw == 0:
            continue

        # Use specific fossil types if available, otherwise a generic fossil mix
        emission_factor_key = plant_type
        if plant_type.startswith("fossil") and plant_type not in EMISSION_FACTORS_GCO2_KWH:
            emission_factor_key = "default_fossil_mix"

        emissions_g_per_kwh = EMISSION_FACTORS_GCO2_KWH.get(emission_factor_key, EMISSION_FACTORS_GCO2_KWH["other"])
        total_emissions_g += generation_mw * 1000 * emissions_g_per_kwh # MW * 1000 kW * g/kWh
        total_generation_kwh += generation_mw * 1000 # MW * 1000 kW

    if total_demand <= 0 : # If no demand, or generation is zero, intensity is undefined or zero.
        # Or if total_generation_kwh is zero. Using total_demand as per original prompt's formula structure.
        return 0.0

    # Intensity is emissions per unit of *consumed* electricity.
    # If generation > demand, the intensity is based on demand met.
    # If generation < demand, the intensity is based on local generation's contribution.
    # The prompt's formula: (new_total_emissions * 1000.0 / demand)
    # This implies 'new_total_emissions' is in kg, hence *1000 to get g.
    # Our total_emissions_g is already in grams.
    # So, intensity = total_emissions_g / (total_demand * 1000) if demand is in MWh and we want g/kWh.
    # If demand is in MW (like generation), then it's total_emissions_g / (total_demand_mw * 1000 kwh/MWh)

    # Let's assume demand is in MW (like generation values).
    # Intensity = (Total Grams of CO2 from generation) / (Total kWh of consumption)
    # Total Grams of CO2 = sum(generation_mw[type] * 1000 * emission_factor_g_kwh[type])
    # Total kWh of consumption = total_demand_mw * 1000 (if demand is what's consumed from this mix)

    # Simplified: if total_demand (in MW) is what's being supplied by this mix:
    co2_intensity = total_emissions_g / (total_demand * 1000) if total_demand > 0 else 0
    return co2_intensity


def run_simulation(base_data: dict, plant_to_add) -> dict:
    """Runs the simulation of adding 'plant_to_add' to the base_data and calculates new values."""
    data = copy.deepcopy(base_data)
    plant_type = plant_to_add.type.lower()
    capacity = plant_to_add.capacity  # MW

    original_fossil_production = sum(data["production"].get(ft, 0.0) for ft in EMISSION_FACTORS_GCO2_KWH if ft.startswith("fossil"))
    original_total_production = data["production"].get("total", sum(v for k, v in data["production"].items() if k != "total"))
    original_co2_intensity = data.get("co2_intensity", 0.0)
    original_demand = data.get("consumption", original_total_production) # Assume demand = production if not specified

    # Step 1: Calculate expected elproduction from the new kraftverket
    new_single_plant_generation = calculate_new_generation(plant_type, capacity, plant_to_add.lat, plant_to_add.lon)

    # Step 2: Uppdatera produktionsmixen
    data["production"][plant_type] = data["production"].get(plant_type, 0.0) + new_single_plant_generation
    data["production"]["total"] = sum(v for k, v in data["production"].items() if k != "total")

    # Step 3: Justera förbrukning och export/import (Simplified)
    # Assume demand stays constant. New generation either displaces other generation or adds to export.
    current_supply = data["production"]["total"]
    demand = data.get("consumption", current_supply) # Use existing demand, or assume it matches new supply if not set
    data["consumption"] = demand # Keep demand constant for this simplified simulation step

    if current_supply >= demand:
        data["export"] = current_supply - demand
        data["import"] = 0.0
    else:
        data["export"] = 0.0
        data["import"] = demand - current_supply # Region is a net importer

    # Step 4: Beräkna påverkan på CO2-utsläpp
    # If new plant is clean, assume it displaces the dirtiest (fossil) generation first.
    co2_reduction_g = 0.0
    if EMISSION_FACTORS_GCO2_KWH.get(plant_type, EMISSION_FACTORS_GCO2_KWH["other"]) == 0: # If it's a "clean" source
        # Try to reduce fossil fuel generation
        displaced_generation = new_single_plant_generation

        # Prioritize reducing the dirtiest fossil fuels first (e.g., coal, then oil, then gas)
        fossil_types_ordered = ["fossil_coal", "fossil_oil", "fossil_gas", "default_fossil_mix"]

        for fossil_type in fossil_types_ordered:
            if data["production"].get(fossil_type, 0.0) > 0 and displaced_generation > 0:
                reduction_from_this_fossil = min(data["production"][fossil_type], displaced_generation)
                data["production"][fossil_type] -= reduction_from_this_fossil

                # Calculate CO2 reduction in grams (generation_MWh * 1000 kWh/MWh * g/kWh)
                co2_reduction_g += reduction_from_this_fossil * 1000 * EMISSION_FACTORS_GCO2_KWH.get(fossil_type, EMISSION_FACTORS_GCO2_KWH["default_fossil_mix"])
                displaced_generation -= reduction_from_this_fossil

        # Update total production after fossil displacement
        data["production"]["total"] = sum(v for k, v in data["production"].items() if k != "total")

    # Recalculate CO2 intensity with the new mix and potentially displaced fossil fuels
    data["co2_intensity"] = calculate_co2_intensity(data["production"], demand)

    # Step 5: Beräkna påverkan på elpris (Very simplified model)
    price_before = data.get("price", 50.0) # EUR/MWh
    # If new clean capacity was added and displaced fossil fuels, or increased export, price might go down.
    # This is highly heuristic.
    if data.get("export", 0) > 0 or co2_reduction_g > 0 : # If exporting or reduced CO2 (implies cleaner, often cheaper, source added)
        # Price reduction proportional to the new plant's capacity relative to demand, capped at 20%
        reduction_factor = min( (new_single_plant_generation / demand) if demand > 0 else 0.1, 1.0) * 0.2 # Max 20% impact from one plant
        data["price"] = price_before * (1 - reduction_factor)
    elif data.get("import", 0) > 0 and data["import"] < (demand - current_supply + new_single_plant_generation): # Import decreased but still importing
         # If import decreased, price might slightly decrease
        data["price"] = price_before * 0.98 # Small decrease
    # No change if new plant is also expensive or demand significantly outstrips supply.

    data["simulation_details"] = {
        "action": "add_plant",
        "plant_added": plant_to_add.dict(),
        "new_plant_generation_MW": new_single_plant_generation,
        "co2_reduction_grams_approx": co2_reduction_g,
        "original_co2_intensity_g_kwh": original_co2_intensity,
        "new_co2_intensity_g_kwh": data["co2_intensity"],
        "original_price_eur_mwh": price_before,
        "new_price_eur_mwh": data["price"]
    }
    return data


def run_remove_simulation(base_data: dict, plant_to_remove) -> dict:
    """Runs the simulation of removing 'plant_to_remove' from the base_data and calculates new values."""
    data = copy.deepcopy(base_data)
    plant_type_to_remove = plant_to_remove.type.lower()
    # Capacity of the plant to remove is needed. Assuming 'name' helps identify it,
    # but for simulation, we need to know how much capacity of 'plant_type_to_remove' is being removed.
    # The issue description implies removing "existing power plants". This requires knowing their capacity.
    # For this prototype, let's assume 'plant_to_remove.capacity' is provided, representing the capacity being removed.
    # If not provided in RemovePlant model, this function would need a way to look up the plant's capacity.

    # Let's assume plant_to_remove object will have a 'capacity' field.
    # If not, we need to modify the Pydantic model or make an assumption.
    # For now, let's assume RemovePlant will be augmented with capacity or we remove ALL of that type.
    # The current Pydantic model `RemovePlant` only has name, region, type.
    # Let's assume 'capacity' is the amount to remove for that type. If not specified, remove all.

    capacity_to_remove = getattr(plant_to_remove, 'capacity', None)

    removed_generation_mw = 0.0
    original_production_of_type = data["production"].get(plant_type_to_remove, 0.0)

    if capacity_to_remove is None or capacity_to_remove >= original_production_of_type:
        removed_generation_mw = original_production_of_type
        data["production"][plant_type_to_remove] = 0.0
    else:
        removed_generation_mw = capacity_to_remove
        data["production"][plant_type_to_remove] -= capacity_to_remove

    if original_production_of_type == 0:
        print(f"Warning: Tried to remove {plant_type_to_remove} but it has 0 production in base data for region {plant_to_remove.region}.")
        # No changes needed if there was nothing to remove.
        data["simulation_details"] = {
            "action": "remove_plant",
            "plant_removed_spec": plant_to_remove.dict(),
            "message": f"No {plant_type_to_remove} production to remove."
        }
        return data

    data["production"]["total"] = sum(v for k, v in data["production"].items() if k != "total")

    original_demand = data.get("consumption", sum(v for k,v in base_data["production"].items() if k!="total"))
    data["consumption"] = original_demand # Assume demand is constant

    current_supply = data["production"]["total"]

    # If supply is now less than demand, it implies increased import or unmet demand.
    # This might trigger peaker plants (often fossil) if a more complex model was used.
    # For simplicity, we'll note the change in import/export.
    if current_supply >= original_demand:
        data["export"] = current_supply - original_demand
        data["import"] = 0.0
    else:
        data["export"] = 0.0
        data["import"] = original_demand - current_supply
        # If a clean plant was removed and demand isn't met, CO2 intensity might worsen
        # if we assume dirtier (e.g. imported or fallback fossil) power makes up the difference.
        # This simplified model doesn't automatically add new fossil generation to meet shortfall,
        # but the CO2 intensity calculation will reflect the new, potentially dirtier, local mix.

    # Recalculate CO2 intensity
    data["co2_intensity"] = calculate_co2_intensity(data["production"], original_demand)

    # Estimate price impact (Very simplified)
    price_before = data.get("price", 50.0)
    if removed_generation_mw > 0 and EMISSION_FACTORS_GCO2_KWH.get(plant_type_to_remove, 100) == 0 : # If a clean plant was removed
        # Removing a cheap/clean source could increase price if demand is constant
        increase_factor = min( (removed_generation_mw / original_demand) if original_demand > 0 else 0.1, 1.0) * 0.15 # Max 15% impact
        data["price"] = price_before * (1 + increase_factor)
    elif data.get("import", 0) > base_data.get("import",0): # If import increased
        data["price"] = price_before * 1.05 # Slight price increase due to higher import needs

    data["simulation_details"] = {
        "action": "remove_plant",
        "plant_removed_spec": plant_to_remove.dict(),
        "removed_generation_mw": removed_generation_mw,
        "new_co2_intensity_g_kwh": data["co2_intensity"],
        "new_price_eur_mwh": data["price"]
    }
    return data


if __name__ == '__main__':
    print("Testing simulation.py...")
    # Mock plant objects similar to Pydantic models for testing
    class MockPlant:
        def __init__(self, name, type, capacity, lat, lon, region):
            self.name = name
            self.type = type
            self.capacity = capacity
            self.lat = lat
            self.lon = lon
            self.region = region
        def dict(self): # To mimic Pydantic's .dict()
            return self.__dict__

    # Test adding a plant
    print("\n--- Test Add Solar Plant ---")
    base_scenario_europe = get_base_data("Europe-Test") # Using a test region string
    print(f"Base Scenario (Europe-Test): Production Total={base_scenario_europe['production']['total']:.2f} MW, CO2 Intensity={base_scenario_europe['co2_intensity']:.2f} g/kWh, Price={base_scenario_europe['price']:.2f} EUR/MWh")

    solar_plant = MockPlant(name="Test Solar Park", type="solar", capacity=500, lat=48.0, lon=10.0, region="Europe-Test")
    sim_results_add_solar = run_simulation(copy.deepcopy(base_scenario_europe), solar_plant)
    print(f"After Adding Solar: Production Total={sim_results_add_solar['production']['total']:.2f} MW, Solar Gen={sim_results_add_solar['production']['solar']:.2f} MW, CO2 Intensity={sim_results_add_solar['co2_intensity']:.2f} g/kWh, Price={sim_results_add_solar['price']:.2f} EUR/MWh")
    print(f"Simulation details: {sim_results_add_solar['simulation_details']}")

    # Test adding a hydrogen plant
    print("\n--- Test Add Hydrogen Plant ---")
    hydrogen_plant = MockPlant(name="Test Hydrogen Fuel Cell", type="hydrogen", capacity=200, lat=49.0, lon=11.0, region="Europe-Test")
    sim_results_add_hydrogen = run_simulation(copy.deepcopy(base_scenario_europe), hydrogen_plant)
    print(f"After Adding Hydrogen: Production Total={sim_results_add_hydrogen['production']['total']:.2f} MW, Hydrogen Gen={sim_results_add_hydrogen['production']['hydrogen']:.2f} MW, CO2 Intensity={sim_results_add_hydrogen['co2_intensity']:.2f} g/kWh, Price={sim_results_add_hydrogen['price']:.2f} EUR/MWh")
    print(f"Simulation details: {sim_results_add_hydrogen['simulation_details']}")

    # Test removing a plant
    # First, let's create a scenario with some nuclear to remove
    print("\n--- Test Remove Nuclear Plant ---")
    scenario_with_nuclear = copy.deepcopy(base_scenario_europe)
    scenario_with_nuclear['production']['nuclear'] = 1000.0 # Add 1000MW of nuclear
    scenario_with_nuclear['production']['total'] = sum(v for k,v in scenario_with_nuclear['production'].items() if k!='total')
    scenario_with_nuclear['co2_intensity'] = calculate_co2_intensity(scenario_with_nuclear['production'], scenario_with_nuclear['consumption'])
    print(f"Scenario with Nuclear: Production Total={scenario_with_nuclear['production']['total']:.2f} MW, Nuclear Gen={scenario_with_nuclear['production']['nuclear']:.2f} MW, CO2 Intensity={scenario_with_nuclear['co2_intensity']:.2f} g/kWh")

    # Remove 500MW of this nuclear plant
    # For remove, the Pydantic model needs 'name', 'region', 'type'. We'll add 'capacity' to it for the subtask.
    # Here, we create a mock object that includes capacity for removal.
    nuclear_plant_to_remove = MockPlant(name="Old Nuclear Plant", type="nuclear", capacity=500, lat=0, lon=0, region="Europe-Test")
    sim_results_remove_nuclear = run_remove_simulation(scenario_with_nuclear, nuclear_plant_to_remove)
    print(f"After Removing 500MW Nuclear: Production Total={sim_results_remove_nuclear['production']['total']:.2f} MW, Nuclear Gen={sim_results_remove_nuclear['production']['nuclear']:.2f} MW, CO2 Intensity={sim_results_remove_nuclear['co2_intensity']:.2f} g/kWh, Price={sim_results_remove_nuclear['price']:.2f} EUR/MWh")
    print(f"Simulation details: {sim_results_remove_nuclear['simulation_details']}")

    # Test removing all of a plant type (e.g. all remaining nuclear)
    print("\n--- Test Remove ALL Remaining Nuclear Plant ---")
    # The 'capacity' field in plant_to_remove will be None if we want to remove all.
    # Our current RemovePlant model in routes_simulation.py doesn't have capacity.
    # Let's assume if capacity is not given to run_remove_simulation, it removes all.
    class MockRemovePlantAll:
         def __init__(self, name, type, region):
            self.name = name # Name might be used to identify specific plant from a list
            self.type = type
            self.region = region
            # No capacity implies remove all of this type, or the specific named plant fully.
            # For this test, it means remove all of 'type'.
         def dict(self): return self.__dict__

    nuclear_plant_to_remove_all = MockRemovePlantAll(name="Any Nuclear Plant", type="nuclear", region="Europe-Test")
    # Use the result from the previous removal as the new base
    sim_results_remove_all_nuclear = run_remove_simulation(copy.deepcopy(sim_results_remove_nuclear), nuclear_plant_to_remove_all)
    print(f"After Removing All Nuclear: Production Total={sim_results_remove_all_nuclear['production']['total']:.2f} MW, Nuclear Gen={sim_results_remove_all_nuclear['production']['nuclear']:.2f} MW, CO2 Intensity={sim_results_remove_all_nuclear['co2_intensity']:.2f} g/kWh, Price={sim_results_remove_all_nuclear['price']:.2f} EUR/MWh")
    print(f"Simulation details: {sim_results_remove_all_nuclear['simulation_details']}")
