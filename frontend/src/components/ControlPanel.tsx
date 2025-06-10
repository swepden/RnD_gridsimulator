// src/components/ControlPanel.tsx
import React, { useState } from 'react';

// Define types for plant properties - can be shared/imported
export interface NewPlantData {
  name: string;
  type: string; // e.g., "solar", "wind", "nuclear", "hydrogen"
  capacity: number; // MW
  startDate: string; // ISO Date string
  // lat, lon will be set by map click or manual input
  lat?: number;
  lon?: number;
  region?: string; // Could be auto-detected or manually set
}

interface ControlPanelProps {
  onAddSimulatedPlant: (plantData: NewPlantData) => void;
  onRemoveSimulatedPlant: (plantName: string) => void; // Or plantId
  onClearSimulations: () => void;
  // selectedLocation: { lat: number, lon: number } | null; // For placing plant
}

const availablePlantTypes = ["solar", "wind", "nuclear", "hydrogen", "fossil_gas", "fossil_coal", "hydro"];

const ControlPanel: React.FC<ControlPanelProps> = ({
    onAddSimulatedPlant,
    onRemoveSimulatedPlant,
    onClearSimulations
    /* selectedLocation */
}) => {
  const [simulationMode, setSimulationMode] = useState<boolean>(false);
  const [plantName, setPlantName] = useState<string>('SimPlant-' + Math.floor(Math.random()*1000));
  const [plantType, setPlantType] = useState<string>(availablePlantTypes[0]);
  const [capacity, setCapacity] = useState<number>(100); // Default 100 MW
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split('T')[0]); // Default to today

  // For removal (simplified by name for now)
  const [plantNameToRemove, setPlantNameToRemove] = useState<string>("");


  const handleAddPlant = () => {
    if (!plantName || !plantType || capacity <= 0) {
      alert("Please fill in all plant details correctly (Name, Type, Capacity > 0).");
      return;
    }
    // In a real app, lat/lon might come from a map click interaction stored in App state
    // For now, we can leave them undefined or use placeholder values.
    // The simulation API requires lat/lon.
    const newPlant: NewPlantData = {
      name: plantName,
      type: plantType,
      capacity: capacity,
      startDate: startDate,
      // lat: selectedLocation?.lat,
      // lon: selectedLocation?.lon,
      // region: "SelectedRegion" // This would also need to be determined
    };
    console.log("ControlPanel: Adding plant:", newPlant);
    onAddSimulatedPlant(newPlant);
    // Reset name for next plant
    setPlantName('SimPlant-' + Math.floor(Math.random()*1000));
  };

  const handleRemovePlant = () => {
    if (!plantNameToRemove) {
        alert("Please enter the name of the plant to remove.");
        return;
    }
    console.log("ControlPanel: Removing plant:", plantNameToRemove);
    onRemoveSimulatedPlant(plantNameToRemove);
    setPlantNameToRemove("");
  };

  const toggleSimulationMode = () => {
    setSimulationMode(prev => !prev);
    console.log("Simulation mode:", !simulationMode);
  };

  return (
    <div style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#f9f9f9', height: '100%', overflowY: 'auto' }}>
      <h3>Controls</h3>

      <button onClick={toggleSimulationMode} style={{ marginBottom: '15px', width: '100%', padding: '8px' }}>
        {simulationMode ? 'Exit Simulation Mode' : 'Enter Simulation Mode'}
      </button>

      {simulationMode && (
        <>
          <h4>Add New Power Plant</h4>
          <div style={{ marginBottom: '10px' }}>
            <label htmlFor="plantName" style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
            <input
              type="text"
              id="plantName"
              value={plantName}
              onChange={(e) => setPlantName(e.target.value)}
              style={{ width: 'calc(100% - 10px)', padding: '5px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label htmlFor="plantType" style={{ display: 'block', marginBottom: '5px' }}>Type:</label>
            <select
              id="plantType"
              value={plantType}
              onChange={(e) => setPlantType(e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            >
              {availablePlantTypes.map(type => (
                <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label htmlFor="capacity" style={{ display: 'block', marginBottom: '5px' }}>Capacity (MW):</label>
            <input
              type="number"
              id="capacity"
              value={capacity}
              onChange={(e) => setCapacity(parseFloat(e.target.value))}
              min="0"
              style={{ width: 'calc(100% - 10px)', padding: '5px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label htmlFor="startDate" style={{ display: 'block', marginBottom: '5px' }}>Start Date:</label>
            <input
              type="date"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{ width: 'calc(100% - 10px)', padding: '5px' }}
            />
          </div>

          {/* Placeholder for lat/lon - ideally set by map click
          {selectedLocation && (
            <p>Selected: Lat: {selectedLocation.lat.toFixed(3)}, Lon: {selectedLocation.lon.toFixed(3)}</p>
          )}
          <p style={{fontSize: '0.9em', color: 'gray'}}>Click on the map to set plant location.</p>
          */}

          <button onClick={handleAddPlant} style={{ width: '100%', padding: '8px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer' }}>
            Add Plant to Simulation
          </button>

          <hr style={{margin: '20px 0'}} />

          <h4>Remove Simulated Plant</h4>
           <div style={{ marginBottom: '10px' }}>
            <label htmlFor="plantNameToRemove" style={{ display: 'block', marginBottom: '5px' }}>Plant Name to Remove:</label>
            <input
              type="text"
              id="plantNameToRemove"
              value={plantNameToRemove}
              onChange={(e) => setPlantNameToRemove(e.target.value)}
              placeholder="Enter name of plant to remove"
              style={{ width: 'calc(100% - 10px)', padding: '5px' }}
            />
          </div>
          <button
            onClick={handleRemovePlant}
            style={{ width: '100%', padding: '8px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer', marginTop: '5px' }}
          >
            Remove Plant from Simulation
          </button>

          <hr style={{margin: '20px 0'}} />
          <button
            onClick={onClearSimulations}
            style={{ width: '100%', padding: '8px', backgroundColor: '#777', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer', marginTop: '5px' }}
          >
            Clear All Simulations
          </button>
        </>
      )}

      {!simulationMode && (
        <p>Switch to Simulation Mode to add or remove virtual power plants and see their impact.</p>
      )}
    </div>
  );
};

export default ControlPanel;
