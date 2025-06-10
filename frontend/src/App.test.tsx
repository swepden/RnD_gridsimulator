// frontend/src/App.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Energy Simulation Tool header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Energy Simulation Tool/i);
  expect(headerElement).toBeInTheDocument();
});

// Add a placeholder test for MapView to show structure
test('renders map placeholder initially in App', () => {
    render(<App />);
    // In App.tsx, MapView is rendered. If MapView initially shows "Loading Map..." or similar:
    // const mapPlaceholder = screen.getByText(/Loading Map.../i); // Or whatever MapView shows
    // expect(mapPlaceholder).toBeInTheDocument();
    // For now, just check if the map container is there from App.css
    const mainElement = screen.getByRole('main');
    expect(mainElement.querySelector('.map-container')).toBeInTheDocument();
  });
