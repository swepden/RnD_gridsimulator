# backend/tests/test_simulation_service.py
from backend.services import simulation # Adjusted import
from backend.api.routes_simulation import NewPlant # For type hinting or creating test objects

def test_calculate_new_generation_solar():
    # Test with dummy weather data from weather_api.py
    # weather_api.get_solar_irradiation will return a dummy value (e.g., 600 W/m^2)
    generation = simulation.calculate_new_generation(
        plant_type="solar",
        capacity=100, # MW
        lat=50.0,
        lon=10.0
    )
    # Based on dummy weather_api (600 W/m^2) and simulation logic (min(600/1000,1)*0.18) * 100
    # = 0.6 * 0.18 * 100 = 10.8 MW (approx)
    assert generation > 0
    # This test is sensitive to dummy values in weather_api and CF in simulation.py
    # A more robust test would mock weather_api calls.
    # For now, check it's a positive number.
    print(f"Solar generation test result: {generation} MW")
    assert isinstance(generation, float)

def test_run_simulation_add_hydrogen():
    class MockPlantToAdd(NewPlant): # Use the Pydantic model
        pass

    base_data = simulation.get_base_data("TestRegionHydrogen")
    hydrogen_plant_data = MockPlantToAdd(
        name="Test H2 Plant",
        type="hydrogen",
        capacity=50,
        start_date="2024-01-01",
        lat=51.0,
        lon=11.0,
        region="TestRegionHydrogen"
    )

    result = simulation.run_simulation(base_data, hydrogen_plant_data)
    assert result["production"]["hydrogen"] > 0
    assert result["simulation_details"]["action"] == "add_plant"
    assert result["simulation_details"]["plant_added"]["type"] == "hydrogen"
    print(f"Hydrogen simulation result: {result['production']['hydrogen']} MW added")
