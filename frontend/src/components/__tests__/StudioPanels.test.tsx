import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { YourJourneyPanel } from '../YourJourneyPanel';
import { LiveRegionMap } from '../LiveRegionMap';
import { ItineraryPlan } from '../../types';

describe('YourJourneyPanel Component', () => {
  it('renders empty starter state with quick prompts when itinerary is null', () => {
    const handleAskHana = vi.fn();
    render(<YourJourneyPanel itinerary={null} onAskHana={handleAskHana} />);

    expect(screen.getByText('No Active Itinerary Yet')).toBeDefined();
    expect(screen.getByText('1-Day Classic Fuji & Kawaguchiko Highlights')).toBeDefined();

    fireEvent.click(screen.getByText('1-Day Classic Fuji & Kawaguchiko Highlights'));
    expect(handleAskHana).toHaveBeenCalledWith(expect.stringContaining('1-day itinerary'));
  });

  it('renders day-by-day stops and details when itinerary is populated', () => {
    const mockPlan: ItineraryPlan = {
      plan_id: 'plan_123',
      title: 'Kawaguchiko Classic Highlights',
      total_days: 1,
      party_composition: 'couple',
      budget_tier: 'standard',
      pace: 'moderate',
      days: [
        {
          day_number: 1,
          title: 'Lake Highlights',
          stops: [
            {
              stop_id: 'stop_1',
              place_id: 'kawaguchiko_oishi_park',
              name_en: 'Oishi Park',
              name_ja: '大石公園',
              category: 'viewpoint',
              fuji_view_rating: 5,
              accessibility_status: 'VERIFIED_ACCESSIBLE',
              estimated_arrival: '09:30',
              duration_minutes: 75,
              image_url: '',
              admission_info: 'Free admission'
            }
          ]
        }
      ]
    };

    render(<YourJourneyPanel itinerary={mockPlan} onAskHana={vi.fn()} />);

    expect(screen.getByText('Kawaguchiko Classic Highlights')).toBeDefined();
    expect(screen.getByText('Oishi Park')).toBeDefined();
    expect(screen.getByText('09:30')).toBeDefined();
    expect(screen.getByText('Verified Barrier-Free & Step-Free Accessible')).toBeDefined();
  });
});

describe('LiveRegionMap Component', () => {
  it('renders interactive Mount Fuji map and pins', () => {
    const handleAskHana = vi.fn();
    render(<LiveRegionMap onAskHana={handleAskHana} />);

    expect(screen.getByText('Live Region Map & Five Lakes')).toBeDefined();
    expect(screen.getByText(/Mt. Fuji/)).toBeDefined();
    expect(screen.getByText('Oishi')).toBeDefined();
    expect(screen.getByText('All Lakes')).toBeDefined();
  });
});
