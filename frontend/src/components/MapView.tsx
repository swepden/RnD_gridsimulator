// src/components/MapView.tsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import L, { LatLngExpression, FeatureGroup } from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon issue with webpack
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

// It's good practice to delete the default icon options and manually set them.
if (L.Icon.Default.prototype) {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
}


L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetinaUrl,
  iconUrl: iconUrl,
  shadowUrl: shadowUrl,
});

// Define interfaces for data types (can be moved to a types.ts file later)
export interface PowerPlant { // Exporting for use in App.tsx
  id: string;
  name: string; // Corrected str to string
  type: string;
  capacity_mw: number;
  lat: number;
  lon: number;
  region: string;
}

export interface RegionProperties { // Exporting for use in App.tsx
  name: string;
  co2_intensity_g_kwh?: number; // g CO2/kWh
  // Other properties as needed
}

export interface RegionDataFeature extends GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon, RegionProperties> {}


interface MapViewProps {
  powerPlants?: PowerPlant[]; // Made optional
  regionsData?: RegionDataFeature[];
  simulatedPlants?: PowerPlant[];
  onMapClick?: (latlng: L.LatLng) => void;
  mapCenter?: LatLngExpression;
  mapZoom?: number;
}

const DEFAULT_CENTER: LatLngExpression = [54.5, 15.0]; // Europe
const DEFAULT_ZOOM = 4;

const MapView: React.FC<MapViewProps> = ({
  powerPlants = [],
  regionsData = [],
  simulatedPlants = [],
  onMapClick,
  mapCenter = DEFAULT_CENTER,
  mapZoom = DEFAULT_ZOOM
}) => {
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);

  const getRegionStyle = (feature?: RegionDataFeature) => {
    const intensity = feature?.properties?.co2_intensity_g_kwh; // Added optional chaining
    let fillColor = '#D3D3D3'; // Default light grey

    if (intensity === undefined || intensity === null) {
      fillColor = '#D3D3D3';
    } else if (intensity < 50) {
      fillColor = '#4CAF50';
    } else if (intensity < 150) {
      fillColor = '#8BC34A';
    } else if (intensity < 300) {
      fillColor = '#FFEB3B';
    } else if (intensity < 500) {
      fillColor = '#FF9800';
    } else {
      fillColor = '#F44336';
    }
    return {
      fillColor: fillColor,
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  const onEachRegionFeature = (feature: RegionDataFeature, layer: L.Layer) => {
    if (feature.properties && feature.properties.name) {
      let popupContent = `<strong>Region:</strong> ${feature.properties.name}`;
      if (feature.properties.co2_intensity_g_kwh !== undefined) {
        popupContent += `<br/><strong>CO2 Intensity:</strong> ${feature.properties.co2_intensity_g_kwh.toFixed(1)} g/kWh`;
      }
      layer.bindPopup(popupContent);
    }
  };

  useEffect(() => {
    if (mapInstance && onMapClick) {
      const handleClick = (e: L.LeafletMouseEvent) => {
        onMapClick(e.latlng);
      };
      mapInstance.on('click', handleClick);
      return () => {
        mapInstance.off('click', handleClick);
      };
    }
  }, [mapInstance, onMapClick]);

  useEffect(() => {
    if (mapInstance) {
        const allPlants = [...powerPlants, ...simulatedPlants];
        if (allPlants.length > 0) {
            const markerGroup = new FeatureGroup();
            allPlants.forEach(plant => {
                if(plant && typeof plant.lat === 'number' && typeof plant.lon === 'number') { // Ensure lat/lon are valid
                    L.marker([plant.lat, plant.lon]).addTo(markerGroup);
                }
            });
            if (Object.keys(markerGroup.getLayers()).length > 0 && regionsData.length === 0) {
                // mapInstance.fitBounds(markerGroup.getBounds().pad(0.1)); // Commented out auto-fit for now
            }
        }
    }
  }, [powerPlants, simulatedPlants, regionsData, mapInstance]);


  return (
    <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ width: '100%', height: '100%' }} // Changed to 100% to fill container
        whenCreated={setMapInstance}
        minZoom={3}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {regionsData && regionsData.length > 0 && (
        <GeoJSON
          key={JSON.stringify(regionsData)} // Add key to force re-render if data changes
          data={regionsData as GeoJSON.GeoJsonObject} // Type assertion
          style={getRegionStyle as L.StyleFunction} // Type assertion
          onEachFeature={onEachRegionFeature as (feature: GeoJSON.Feature, layer: L.Layer) => void}
        />
      )}

      {powerPlants.map((plant) => {
        if (plant && typeof plant.lat === 'number' && typeof plant.lon === 'number') { // Check for valid plant data
          return (
            <Marker key={`plant-${plant.id}`} position={[plant.lat, plant.lon]}>
              <Popup>
                <strong>{plant.name}</strong><br />
                Type: {plant.type}<br />
                Capacity: {plant.capacity_mw} MW<br />
                Region: {plant.region}
              </Popup>
            </Marker>
          );
        }
        return null; // Skip rendering if plant data is invalid
      })}

      {simulatedPlants.map((plant) => {
         if (plant && typeof plant.lat === 'number' && typeof plant.lon === 'number') {
          return (
            <Marker
                key={`sim-${plant.id}`}
                position={[plant.lat, plant.lon]}
            >
              <Popup>
                <strong>{plant.name} (Simulated)</strong><br />
                Type: {plant.type}<br />
                Capacity: {plant.capacity_mw} MW<br />
                Region: {plant.region}
              </Popup>
            </Marker>
          );
        }
        return null;
      })}
    </MapContainer>
  );
};

export default MapView;
