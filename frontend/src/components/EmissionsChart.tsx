// src/components/EmissionsChart.tsx
import React from 'react';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Colors // Import Colors plugin
} from 'chart.js';
import { RegionDataFeature, PowerPlant } from './MapView'; // Assuming types are exported from MapView

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Colors // Register Colors plugin
);

interface EmissionsChartProps {
  regionData: RegionDataFeature | null; // Display data for a single selected/aggregated region
  powerPlants: PowerPlant[]; // Both existing and simulated for production mix
  // Historical data could be added later
  // historicalPrices?: { date: string, price: number }[];
  // historicalEmissions?: { date: string, intensity: number }[];
}

// Helper to aggregate production data from power plants
const getProductionMixData = (plants: PowerPlant[]) => {
  const mix: { [key: string]: number } = {};
  plants.forEach(plant => {
    mix[plant.type] = (mix[plant.type] || 0) + plant.capacity_mw;
  });
  return {
    labels: Object.keys(mix),
    datasets: [{
      label: 'Production Capacity (MW)',
      data: Object.values(mix),
      // Chart.js Colors plugin will pick colors if not specified here
      // backgroundColor: ['rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', ...],
    }]
  };
};


const EmissionsChart: React.FC<EmissionsChartProps> = ({ regionData, powerPlants }) => {
  const productionData = getProductionMixData(powerPlants);

  const co2IntensityData = {
    labels: ['Current'], // Could be time series later
    datasets: [{
      label: `CO2 Intensity (g CO2/kWh) - ${regionData?.properties.name || 'Region'}`,
      data: [regionData?.properties.co2_intensity_g_kwh ?? 0],
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      type: 'bar' as const, // Can be bar for single value, line for series
    }]
  };

  // Placeholder for price data - extend when available
  const priceData = {
    labels: ['Current'], // Could be time series later
    datasets: [{
      label: `Electricity Price (€/MWh) - ${regionData?.properties.name || 'Region'}`,
      data: [regionData && (regionData.properties as any).price ? (regionData.properties as any).price : 50 + Math.random()*10], // Example price
      borderColor: 'rgb(53, 162, 235)',
      backgroundColor: 'rgba(53, 162, 235, 0.5)',
      type: 'line' as const,
      yAxisID: 'yPrice',
    }]
  };

  const optionsBase = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        // text: 'Chart Title', // Will be set per chart
      },
      colors: { // Enable the Colors plugin
        enabled: true
      }
    },
  };

  const productionOptions = { ...optionsBase, plugins: { ...optionsBase.plugins, title: { display: true, text: 'Production Mix (Capacity MW)' } } };
  const co2Options = { ...optionsBase, plugins: { ...optionsBase.plugins, title: { display: true, text: 'CO2 Intensity' } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'g CO2/kWh'} } } };
  const priceOptions = { ...optionsBase, plugins: { ...optionsBase.plugins, title: { display: true, text: 'Electricity Price' } }, scales: { yPrice: { type: 'linear' as const, display: true, position: 'left' as const, title: {display: true, text: 'EUR/MWh'} } } };


  if (!regionData && powerPlants.length === 0) {
    return <p>No data available for charts. Select a region or add power plants.</p>;
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ flex: 1, minHeight: '200px' }}>
        <h4>Production Mix</h4>
        {powerPlants.length > 0 ? <Bar options={productionOptions} data={productionData} /> : <p>No production data.</p>}
      </div>
      <div style={{ flex: 1, minHeight: '200px' }}>
        <h4>CO2 & Price Overview</h4>
        {/* For simplicity, showing CO2 as Bar and Price as Line on the same conceptual chart area, but they are separate charts here */}
        {regionData ? <Bar options={co2Options} data={co2IntensityData} /> : <p>No CO2 data.</p>}
        {/* Price chart can be added here or combined if scales match */}
        {regionData ? <Line options={priceOptions} data={priceData} /> : <p>No price data.</p>}
      </div>
    </div>
  );
};

export default EmissionsChart;
