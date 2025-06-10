# Energy Simulation Tool

This project is a prototype of an AI-generated software tool for simulating electricity production and its real-time impact. It allows users to visualize current energy data and simulate the addition or removal of power plants to see effects on CO2 emissions, electricity prices, and grid balance.

## Project Structure

```
energy-sim-tool/
├── backend/ (Python FastAPI)
│   ├── main.py             # FastAPI app entry point
│   ├── api/                # API route definitions
│   │   ├── routes_data.py
│   │   └── routes_simulation.py
│   ├── services/           # Business logic and external API integrations
│   │   ├── entsoe_api.py   # ENTSO-E and Nord Pool (placeholder) data
│   │   ├── weather_api.py  # NASA POWER/Copernicus (placeholder) weather data
│   │   ├── simulation.py   # Core simulation logic
│   │   └── data_store.py   # In-memory caching
│   └── requirements.txt    # Python dependencies
├── frontend/ (React + TypeScript)
│   ├── public/             # Static assets and index.html
│   ├── src/
│   │   ├── components/     # React components (MapView, ControlPanel, EmissionsChart)
│   │   ├── services/       # Frontend API client (apiClient.ts)
│   │   ├── App.tsx         # Main application component
│   │   ├── index.tsx       # React entry point
│   │   └── ... (CSS, other TS files)
│   ├── package.json        # Node dependencies and scripts
│   └── tsconfig.json       # TypeScript configuration
└── README.md               # This file
```

## Features Implemented (Prototype Stage)

*   **Backend (FastAPI)**:
    *   API endpoints for fetching real-time data (dummy) and running simulations.
    *   Simulation logic for adding various power plant types (including **hydrogen**) and removing existing plants.
    *   Calculation of impacts on CO2 intensity and electricity prices (simplified model).
    *   Placeholders for integration with ENTSO-E, Nord Pool (data source), NASA POWER, and Copernicus.
    *   In-memory caching for API responses.
*   **Frontend (React + TypeScript)**:
    *   Interactive map display using Leaflet (`MapView`) showing power plants and regional CO2 intensity.
    *   Control panel (`ControlPanel`) for adding/removing simulated power plants and toggling simulation mode.
    *   Charts (`EmissionsChart`) for visualizing production mix, CO2 intensity, and prices.
    *   API client for communication with the backend.
    *   Proxy setup for local development to avoid CORS issues.

## Prerequisites

*   Node.js and npm (or yarn) for the frontend.
*   Python 3.8+ and pip for the backend.

## Setup and Running Locally

### Backend (FastAPI)

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create a virtual environment (recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the backend server**:
    The FastAPI application is served using Uvicorn.
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The backend API will be available at `http://localhost:8000`.
    *   Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
    *   Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

    **Note on API Keys**:
    *   The `backend/services/entsoe_api.py` file has a placeholder `API_TOKEN = "YOUR_ENTSOE_API_KEY_HERE"`. For actual ENTSO-E API calls, you need to replace this with your valid ENTSO-E API key. Otherwise, it will return dummy data.
    *   Similar placeholders or dummy data mechanisms are in place for weather APIs.

### Frontend (React)

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install Node dependencies**:
    ```bash
    npm install
    # or if you prefer yarn:
    # yarn install
    ```

3.  **Run the frontend development server**:
    ```bash
    npm start
    # or
    # yarn start
    ```
    The React application will open in your browser, usually at `http://localhost:3000`.
    The `proxy` setting in `frontend/package.json` will forward API requests from `http://localhost:3000/api/...` to the backend at `http://localhost:8000/api/...`.

## How to Use

1.  Ensure both backend and frontend servers are running.
2.  Open the frontend application in your browser (`http://localhost:3000`).
3.  The map will display sample power plants and regional CO2 data.
4.  Use the "Controls" panel:
    *   Click "Enter Simulation Mode".
    *   Fill in the details for a new power plant (name, type including "hydrogen", capacity).
    *   Click on the map to select a location for the new plant.
    *   Click "Add Plant to Simulation". The plant will appear on the map, and regional CO2/price data (in charts/text) should update based on the simulation.
    *   To remove a simulated plant, enter its name and click "Remove Plant from Simulation".
    *   "Clear All Simulations" will remove all simulated plants and reset data.
5.  Select different regions from the dropdown in the header to see their specific data in the charts.

## Further Development Considerations

*   **Real API Integration**: Replace dummy data and placeholder API calls in backend services (`entsoe_api.py`, `weather_api.py`) with actual, robust API integrations. This includes proper error handling, data parsing, and management of API keys.
*   **Nord Pool Integration**: Fully implement data fetching and processing from Nord Pool as a distinct data source.
*   **Advanced Simulation Logic**:
    *   More sophisticated CO2 displacement models.
    *   Detailed electricity price calculation (e.g., merit order).
    *   Consideration of grid constraints, import/export dynamics.
    *   Time-based simulations (e.g., effect over a day/year).
*   **Real-time Updates**: Implement WebSockets or Server-Sent Events for true real-time data synchronization across clients or for live data feeds.
*   **Database**: For persistent storage of power plant data, user scenarios, or historical data, integrate a database.
*   **UI/UX Enhancements**: Improve styling, add more visual feedback, loading states, error notifications.
*   **Testing**: Comprehensive unit and integration tests for both backend and frontend.
*   **Deployment**: Containerization (Docker) and deployment strategies.
```
