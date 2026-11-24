import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DiscoverView } from '../DiscoverView';
import { HanaWorkspace } from '../HanaWorkspace';
import { TravelIntelligenceView } from '../TravelIntelligenceView';
import { MyTravelView } from '../MyTravelView';
import { ProfileSettingsView } from '../ProfileSettingsView';

describe('FujiNova 5.0 Workspaces', () => {
  it('renders DiscoverView with Mount Fuji hero, search bar and CTAs', () => {
    const handleAskHana = vi.fn();
    const handleExplore3D = vi.fn();
    const handlePlanTrip = vi.fn();

    render(
      <DiscoverView 
        onAskHana={handleAskHana} 
        onExplore3D={handleExplore3D} 
        onPlanTrip={handlePlanTrip} 
      />
    );

    expect(screen.getAllByText(/Mount Fuji & The Five Lakes/).length).toBeGreaterThan(0);
    expect(screen.getByText('Plan with Hana AI')).toBeDefined();
    expect(screen.getByText('Explore 3D Digital Twin')).toBeDefined();

    fireEvent.click(screen.getByText('Explore 3D Digital Twin'));
    expect(handleExplore3D).toHaveBeenCalled();
  });

  it('renders TravelIntelligenceView with monthly climate and emergency safety contacts', () => {
    const handleAskHana = vi.fn();
    render(<TravelIntelligenceView onAskHana={handleAskHana} />);

    expect(screen.getByText('Travel Intelligence Center')).toBeDefined();
    expect(screen.getByText('Fuji Visibility Probability')).toBeDefined();

    // Switch to Emergency and Safety tab
    fireEvent.click(screen.getByText('Emergency & Safety'));
    expect(screen.getByText('Official Climbing Season Notice')).toBeDefined();
    expect(screen.getByText('110')).toBeDefined(); // Police
    expect(screen.getByText('119')).toBeDefined(); // Ambulance
  });

  it('renders MyTravelView with JPY budget manager and phrasebook', () => {
    const handleAskHana = vi.fn();
    render(<MyTravelView onAskHana={handleAskHana} />);

    expect(screen.getByText('My Travel Dashboard')).toBeDefined();
    expect(screen.getByText(/Budget Manager/)).toBeDefined();
    expect(screen.getByText('Estimated Total Expenses')).toBeDefined();

    // Switch to offline tab
    fireEvent.click(screen.getByText('Offline Companion'));
    expect(screen.getByText(/Essential Mount Fuji Travel Phrases/)).toBeDefined();
  });

  it('renders ProfileSettingsView with WCAG 2.2 AA toggles and model telemetry', () => {
    render(<ProfileSettingsView activeModel="gpt-4o-mini" />);

    expect(screen.getByText('Profile & Accessibility Settings')).toBeDefined();
    expect(screen.getByText(/Accessibility & Universal Design/)).toBeDefined();
    expect(screen.getByText('High Contrast Mode')).toBeDefined();
    expect(screen.getByText('Reduced Motion')).toBeDefined();
    expect(screen.getByText('gpt-4o-mini')).toBeDefined();
  });
});
