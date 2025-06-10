// src/App.tsx
import React, { useState, useEffect } from 'react';
import './App.css';
import MapView, { PowerPlant, RegionDataFeature } from './components/MapView';
import ControlPanel, { NewPlantData } from './components/ControlPanel';
import EmissionsChart from './components/EmissionsChart'; // Import EmissionsChart
import L, { LatLngExpression } from 'leaflet';
import { getRealtimeData, simulateAddPlant, simulateRemovePlant } from './services/apiClient';

// Sample Data (initial, can be overridden by API)
const initialPowerPlants: PowerPlant[] = [
  { id: '1', name: 'Germany Central Nuclear', type: 'Nuclear', capacity_mw: 1200, lat: 50.0, lon: 10.0, region: 'DE' },
  { id: '2', name: 'Brandenburg Wind Park', type: 'Wind', capacity_mw: 300, lat: 52.5, lon: 13.5, region: 'DE' },
];

// A very simplified GeoJSON for Europe for demonstration
const europeGeoJsonInitial: RegionDataFeature = {
  type: "Feature",
  geometry: {
    type: "Polygon",
    coordinates: [[
      [-10.83, 34.98], [31.42, 34.98], [31.42, 71.03], [-10.83, 71.03], [-10.83, 34.98]
    ]]
  },
  properties: { name: "Europe", co2_intensity_g_kwh: 180 } // Default overall
};

// Add a more specific region for better chart demo
const germanyGeoJsonInitial: RegionDataFeature = {
    type: "Feature",
    geometry: { // Simplified bounding box for Germany
      type: "Polygon",
      coordinates: [[
        [5.866342, 47.270111], [15.038338, 47.270111],
        [15.038338, 55.058347], [5.866342, 55.058347],
        [5.866342, 47.270111]
      ]]
    },
    properties: { name: "Germany", co2_intensity_g_kwh: 250 }
  };


const initialRegionsData: RegionDataFeature[] = [europeGeoJsonInitial, germanyGeoJsonInitial];


function App() {
  const [powerPlants, setPowerPlants] = useState<PowerPlant[]>(initialPowerPlants);
  const [regionsData, setRegionsData] = useState<RegionDataFeature[]>(initialRegionsData);
  const [simulatedPlants, setSimulatedPlants] = useState<PowerPlant[]>([]);
  const [mapCenter] = useState<LatLngExpression>([51.5, 10.0]); // Centered more on Germany/Europe
  const [mapZoom] = useState<number>(5);
  const [selectedMapLocation, setSelectedMapLocation] = useState<L.LatLng | null>(null);
  const [currentDisplayRegionName, setCurrentDisplayRegionName] = useState<string>("Germany"); // For chart display

  // Derived state for chart: combines existing and simulated plants
  const allPlantsForCharts = [...powerPlants, ...simulatedPlants];
  // Derived state for chart: finds the region data for the currentDisplayRegionName
  const currentRegionForChart = regionsData.find(r => r.properties.name === currentDisplayRegionName) || regionsData[0] || null;


  useEffect(() => {
    const fetchData = async (regionName: string) => {
      // The backend API expects a region code/identifier.
      // We'll use the regionName as the identifier for now, assuming backend can map it or uses it directly.
      const regionIdentifier = regionName; // e.g., "Germany" or "DE" if mapped
      try {
        const response = await getRealtimeData(regionIdentifier);
        console.log(`Realtime data for ${regionIdentifier}:`, response.data);

        // Update CO2 intensity for the region
        if (response.data && response.data.co2_intensity !== undefined) {
          setRegionsData(prevRegions => prevRegions.map(r =>
            r.properties.name === regionName
            ? { ...r, properties: { ...r.properties, co2_intensity_g_kwh: response.data.co2_intensity, price: response.data.price } } // Assuming price is also in response
            : r
          ));
        }
        // Update power plants from API (illustrative, as API gives aggregate)
        // This part would need refinement based on how you want to display API-driven plants
      } catch (error) {
        console.error(`Failed to fetch realtime data for ${regionIdentifier}:`, error);
      }
    };
    fetchData(currentDisplayRegionName);
  }, [currentDisplayRegionName]);

  const handleMapClick = (latlng: L.LatLng) => {
    setSelectedMapLocation(latlng);
    // TODO: Could try to determine region from click to set currentDisplayRegionName
  };

  const handleAddSimulatedPlant = async (plantData: NewPlantData) => {
    if (selectedMapLocation === null && (plantData.lat === undefined || plantData.lon === undefined)) {
        alert("Please click on the map to set the plant's location, or provide lat/lon manually.");
        return;
    }
    const regionForPlant = plantData.region || currentDisplayRegionName; // Use form region or current

    const finalPlantData: PowerPlant = {
      id: `sim-${plantData.name}-${Date.now()}`,
      name: plantData.name,
      type: plantData.type,
      capacity_mw: plantData.capacity,
      lat: plantData.lat ?? selectedMapLocation!.lat,
      lon: plantData.lon ?? selectedMapLocation!.lng,
      region: regionForPlant,
    };

    try {
      const apiPayload = { ...plantData, lat: finalPlantData.lat, lon: finalPlantData.lon, region: regionForPlant, capacity: plantData.capacity };
      const response = await simulateAddPlant(apiPayload);
      setSimulatedPlants(prev => [...prev, finalPlantData]);
      if (response.data && response.data.updated_data) {
        setRegionsData(prevRegions => prevRegions.map(r =>
          r.properties.name === regionForPlant
          ? { ...r, properties: {
              ...r.properties,
              co2_intensity_g_kwh: response.data.updated_data.co2_intensity,
              price: response.data.updated_data.price // Assuming backend sends price
            } }
          : r
        ));
      }
      setSelectedMapLocation(null);
    } catch (error) { console.error("Failed to simulate adding plant:", error); }
  };

  const handleRemoveSimulatedPlant = async (plantNameOrId: string) => {
    const plantToRemove = simulatedPlants.find(p => p.name === plantNameOrId || p.id === plantNameOrId);
    if (!plantToRemove) return;
    try {
      const apiPayload = { name: plantToRemove.name, type: plantToRemove.type, region: plantToRemove.region, capacity: plantToRemove.capacity_mw };
      const response = await simulateRemovePlant(apiPayload);
      setSimulatedPlants(prev => prev.filter(p => p.id !== plantToRemove.id));
      if (response.data && response.data.updated_data) {
         setRegionsData(prevRegions => prevRegions.map(r =>
          r.properties.name === plantToRemove.region
          ? { ...r, properties: {
              ...r.properties,
              co2_intensity_g_kwh: response.data.updated_data.co2_intensity,
              price: response.data.updated_data.price
            } }
          : r
        ));
      }
    } catch (error) { console.error("Failed to simulate removing plant:", error); }
  };

  const handleClearSimulations = () => {
    setSimulatedPlants([]);
    fetchData(currentDisplayRegionName); // Reset region data
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Energy Simulation Tool</h1>
        <select value={currentDisplayRegionName} onChange={(e) => setCurrentDisplayRegionName(e.target.value)} style={{padding: '5px', marginLeft: '20px'}}>
            {regionsData.map(r => <option key={r.properties.name} value={r.properties.name}>{r.properties.name}</option>)}
        </select>
      </header>
      <main className="App-main">
        <div className="map-container">
          <MapView
            powerPlants={powerPlants}
            regionsData={regionsData}
            simulatedPlants={simulatedPlants}
            onMapClick={handleMapClick}
            mapCenter={mapCenter}
            mapZoom={mapZoom}
          />
          {selectedMapLocation && (
            <div style={{position: 'absolute', bottom: '10px', left: '10px', backgroundColor: 'white', padding: '5px', zIndex: 1000, border: '1px solid black'}}>
                Clicked: Lat: {selectedMapLocation.lat.toFixed(3)}, Lon: {selectedMapLocation.lng.toFixed(3)}
            </div>
          )}
        </div>
        <div className="controls-container">
          <ControlPanel
            onAddSimulatedPlant={handleAddSimulatedPlant}
            onRemoveSimulatedPlant={handleRemoveSimulatedPlant}
            onClearSimulations={handleClearSimulations}
          />
        </div>
        <div className="charts-container">
           <h3>Data for: {currentDisplayRegionName}</h3>
          <EmissionsChart
            regionData={currentRegionForChart}
            powerPlants={allPlantsForCharts.filter(p => p.region === currentDisplayRegionName || currentDisplayRegionName === "Europe")} // Filter plants for the selected region or show all for "Europe"
          />
        </div>
      </main>
    </div>
  );
}

export default App;
