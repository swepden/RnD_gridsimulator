# backend/main.py
from fastapi import FastAPI
from api import routes_data, routes_simulation # Ensure this line is present and correct

app = FastAPI(title="EnergySim API", description="API för elproduktionssimulering", version="1.0")

app.include_router(routes_data.router, prefix="/api")
app.include_router(routes_simulation.router, prefix="/api/simulation") # Corrected prefix for simulation routes

# (Ev. kod för att starta bakgrundsuppdatering av data-cache)
