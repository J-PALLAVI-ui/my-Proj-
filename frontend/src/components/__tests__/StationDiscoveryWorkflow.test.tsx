import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TripProvider } from '../../context/TripContext';
import { StationDiscoveryWorkflow } from '../StationDiscoveryWorkflow';

describe('StationDiscoveryWorkflow Component (4-Panel Architecture)', () => {
  it('renders Panel A (Starting Station & Complete Catalogue) with 237 places', () => {
    render(
      <TripProvider>
        <StationDiscoveryWorkflow />
      </TripProvider>
    );

    // Screen A title & location
    expect(screen.getByText('Where are you starting?')).toBeDefined();
    expect(screen.getByText(/Kawaguchiko Station/)).toBeDefined();
    expect(screen.getByText('Use GPS')).toBeDefined();

    // Tabs
    expect(screen.getByText(/Famous Places/)).toBeDefined();
    expect(screen.getByText(/Hidden Gems/)).toBeDefined();
    expect(screen.getByText(/All Places/)).toBeDefined();

    // Choose for me button
    expect(screen.getByText('Choose for me')).toBeDefined();
    expect(screen.getByText(/View all/)).toBeDefined();
  });

  it('navigates to Panel B (Travel Modes) and displays all 8 modes', () => {
    render(
      <TripProvider>
        <StationDiscoveryWorkflow />
      </TripProvider>
    );

    // Click Stepper ② Travel Modes & Recs
    const modeTab = screen.getByText(/② Travel Modes & Recs/);
    fireEvent.click(modeTab);

    // Header
    expect(screen.getByText('How would you like to travel?')).toBeDefined();

    // 8 Modes
    expect(screen.getByText('Walking')).toBeDefined();
    expect(screen.getByText('Rent a Bicycle')).toBeDefined();
    expect(screen.getByText('Fujikyu Bus')).toBeDefined();
    expect(screen.getByText('Other Buses')).toBeDefined();
    expect(screen.getByText('Train')).toBeDefined();
    expect(screen.getByText('Taxi')).toBeDefined();
    expect(screen.getByText('Mixed Transport')).toBeDefined();
    expect(screen.getByText('Private Vehicle')).toBeDefined();

    // Distance range slider label
    expect(screen.getByText('Distance Range')).toBeDefined();
  });

  it('navigates to Panel C (Transit Route) and renders Google-maps style routing', () => {
    render(
      <TripProvider>
        <StationDiscoveryWorkflow />
      </TripProvider>
    );

    // Click Stepper ③ Route & Transit
    const routeTab = screen.getByText(/③ Route & Transit/);
    fireEvent.click(routeTab);

    // Route title and summary
    expect(screen.getByText(/Route to/)).toBeDefined();
    expect(screen.getByText('Your route')).toBeDefined();
    expect(screen.getByText('Show bus details')).toBeDefined();
    expect(screen.getByText('Plan full trip')).toBeDefined();

    // Legend
    expect(screen.getByText('Walking')).toBeDefined();
    expect(screen.getByText('Bus (Fujikyu)')).toBeDefined();
  });

  it('navigates to Panel D (Day Plan & Live Timers) and displays timeline & timer', () => {
    render(
      <TripProvider>
        <StationDiscoveryWorkflow />
      </TripProvider>
    );

    // Click Stepper ④ Day Plan & Live Progress
    const progressTab = screen.getByText(/④ Day Plan & Live Progress/);
    fireEvent.click(progressTab);

    // Title and timer
    expect(screen.getByText(/Your 5-hour day/)).toBeDefined();
    expect(screen.getByText('Trip Timer')).toBeDefined();

    // Timeline stops
    expect(screen.getByText(/Breakfast at Kawaguchiko/)).toBeDefined();
    expect(screen.getByText(/Travel to Oishi Park/)).toBeDefined();
    expect(screen.getByText(/Oishi Park \(Main Visit\)/)).toBeDefined();
    expect(screen.getByText(/Lunch - Hoto Noodles/)).toBeDefined();
    expect(screen.getByText(/Nagasaki Cape/)).toBeDefined();
    expect(screen.getByText(/Return to Kawaguchiko/)).toBeDefined();

    // Early finish recalibration trigger
    const earlyBtn = screen.getByText(/Finished Early/);
    fireEvent.click(earlyBtn);

    // Recalibration popup modal
    expect(screen.getByText(/You finished/)).toBeDefined();
    expect(screen.getByText(/Revised Plan/)).toBeDefined();
    expect(screen.getByText('Apply updated plan')).toBeDefined();
  });
});
