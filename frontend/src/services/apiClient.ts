// src/services/apiClient.ts
import axios from 'axios';

// Define the structure for NewPlant payload based on backend's NewPlant Pydantic model
interface NewPlantPayload {
  name: string;
  type: string;
  capacity: number; // MW
  start_date: string; // ISO date string
  lat: number;
  lon: number;
  region: string;
}

// Define the structure for RemovePlant payload
interface RemovePlantPayload {
  name: string;
  type: string;
  region: string;
  capacity?: number; // Optional: MW to remove
}


const API_BASE_URL = '/api'; // Adjust if your backend runs on a different port during dev

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRealtimeData = (region: string) => {
  return apiClient.get(`/realtime?region=${encodeURIComponent(region)}`);
};

// POST /api/simulation/add
export const simulateAddPlant = (plantData: NewPlantPayload) => {
  return apiClient.post('/simulation/add', plantData);
};

// POST /api/simulation/remove
export const simulateRemovePlant = (plantData: RemovePlantPayload) => {
  return apiClient.post('/simulation/remove', plantData);
};


export default apiClient;
