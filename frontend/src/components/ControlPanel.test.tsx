// frontend/src/components/ControlPanel.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ControlPanel from './ControlPanel';

describe('ControlPanel', () => {
  const mockAddHandler = jest.fn();
  const mockRemoveHandler = jest.fn();
  const mockClearHandler = jest.fn();

  beforeEach(() => {
    mockAddHandler.mockClear();
    mockRemoveHandler.mockClear();
    mockClearHandler.mockClear();
  });

  test('renders and allows entering simulation mode', () => {
    render(
      <ControlPanel
        onAddSimulatedPlant={mockAddHandler}
        onRemoveSimulatedPlant={mockRemoveHandler}
        onClearSimulations={mockClearHandler}
      />
    );

    const modeButton = screen.getByRole('button', { name: /Enter Simulation Mode/i });
    expect(modeButton).toBeInTheDocument();
    fireEvent.click(modeButton);
    expect(screen.getByRole('button', { name: /Exit Simulation Mode/i })).toBeInTheDocument();
    expect(screen.getByText(/Add New Power Plant/i)).toBeInTheDocument();
  });

  test('calls onAddSimulatedPlant with data when form submitted', () => {
    render(
        <ControlPanel
          onAddSimulatedPlant={mockAddHandler}
          onRemoveSimulatedPlant={mockRemoveHandler}
          onClearSimulations={mockClearHandler}
        />
      );

    // Enter sim mode
    fireEvent.click(screen.getByRole('button', { name: /Enter Simulation Mode/i }));

    // Fill form
    fireEvent.change(screen.getByLabelText(/Name:/i), { target: { value: 'Test Solar' } });
    fireEvent.change(screen.getByLabelText(/Type:/i), { target: { value: 'solar' } });
    fireEvent.change(screen.getByLabelText(/Capacity \(MW\):/i), { target: { value: '150' } });

    fireEvent.click(screen.getByRole('button', { name: /Add Plant to Simulation/i }));

    expect(mockAddHandler).toHaveBeenCalledTimes(1);
    expect(mockAddHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Test Solar',
        type: 'solar',
        capacity: 150,
      })
    );
  });
});
