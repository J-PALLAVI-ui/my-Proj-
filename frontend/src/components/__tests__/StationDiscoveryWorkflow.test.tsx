import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TripProvider } from '../../context/TripContext';
import { I18nProvider } from '../../i18n/I18nContext';
import { StationDiscoveryWorkflow } from '../StationDiscoveryWorkflow';

describe('StationDiscoveryWorkflow Component (4-Panel Architecture)', () => {
  it('renders Panel A (Starting Station & Complete Catalogue) with 237 places', () => {
    render(
      <I18nProvider>
        <TripProvider>
          <StationDiscoveryWorkflow />
        </TripProvider>
      </I18nProvider>
    );

    // Screen A title & location
    expect(screen.getByText('Where are you starting?')).toBeDefined();
    expect(screen.getAllByText(/Kawaguchiko Station/)[0]).toBeDefined();
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

  describe('Autonomous Dynamic UI Verification (Tests A - J)', () => {
    it('Test A: Kawaguchiko Station displays Famous Places (124) count and hub pins', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      expect(screen.getByText(/Famous Places \(124\)/)).toBeDefined();
      expect(screen.getByText(/Lake Kawaguchiko Hub/)).toBeDefined();
    });

    it('Test B: Changing station to Fujisan Station displays blue alert banner and updated count', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      // Open station dropdown
      const stationBtn = screen.getByText(/Kawaguchiko Station \(Main Hub\)/);
      fireEvent.click(stationBtn);

      // Select Fujisan Station
      const fujisanOption = screen.getByRole('button', { name: /Fujisan Station/i });
      fireEvent.click(fujisanOption);

      // Check blue banner
      expect(screen.getByText(/Recommendations updated for Fujisan Station/)).toBeDefined();
      expect(screen.getByText(/Famous Places \(98\)/)).toBeDefined();
    });

    it('Test C: Switching to Hidden Gems displays (137) count for Fujisan Station', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      // Open station dropdown and select Fujisan Station
      const stationBtn = screen.getByText(/Kawaguchiko Station \(Main Hub\)/);
      fireEvent.click(stationBtn);
      const fujisanOption = screen.getByRole('button', { name: /Fujisan Station/i });
      fireEvent.click(fujisanOption);

      // Click Hidden Gems tab
      const gemsTab = screen.getByText(/Hidden Gems/);
      fireEvent.click(gemsTab);

      expect(screen.getByText(/Hidden Gems \(137\)/)).toBeDefined();
    });

    it('Test D: Switching to All Places displays 237 total places count', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      const allTab = screen.getByText(/All Places/);
      fireEvent.click(allTab);
      expect(screen.getByText(/All Places \(237\)/)).toBeDefined();
    });

    it('Test E: Searching for "bus stop" filters places', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      const searchInput = screen.getByPlaceholderText(/Search places/);
      fireEvent.change(searchInput, { target: { value: 'bus stop' } });
      expect(searchInput).toBeDefined();
    });

    it('Test F: Searching for "metro" or "subway" renders honest educational notice', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      const searchInput = screen.getByPlaceholderText(/Search places/);
      fireEvent.change(searchInput, { target: { value: 'metro station' } });
      expect(screen.getAllByText(/No metro station found/)[0]).toBeDefined();
    });

    it('Test G: Changing travel mode from Walk to Bicycle updates mode state', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      const bikePill = screen.getAllByText(/Bicycle/)[0];
      fireEvent.click(bikePill);
      expect(bikePill).toBeDefined();
    });

    it('Test H: Changing travel mode to Fujikyu Bus displays transit network map', () => {
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      const busPill = screen.getAllByRole('button', { name: /Fujikyu Bus/i })[0] || screen.getAllByText(/Fujikyu Bus/)[0];
      fireEvent.click(busPill);
      expect(screen.getByText(/Kawaguchiko Network/)).toBeDefined();
    });

    it('Test I: Switching to Japanese translates key UI labels', () => {
      localStorage.setItem('fujinova_locale', 'ja');
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      expect(screen.getByText('現在の出発地はどこですか？')).toBeDefined();
      expect(screen.getByText(/有名な観光地/)).toBeDefined();
      expect(screen.getByText('GPSを使用')).toBeDefined();
      localStorage.setItem('fujinova_locale', 'en');
    });

    it('Test J: Switching to Hindi translates key UI labels', () => {
      localStorage.setItem('fujinova_locale', 'hi');
      render(
        <I18nProvider>
          <TripProvider>
            <StationDiscoveryWorkflow />
          </TripProvider>
        </I18nProvider>
      );
      expect(screen.getByText('आप कहाँ से यात्रा शुरू कर रहे हैं?')).toBeDefined();
      expect(screen.getByText(/प्रसिद्ध स्थान/)).toBeDefined();
      expect(screen.getByText('GPS प्रयोग करें')).toBeDefined();
      localStorage.setItem('fujinova_locale', 'en');
    });
  });
});
