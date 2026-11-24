import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DestinationComparisonModal } from '../DestinationComparisonModal';
import { AdaptiveItinerary } from '../AdaptiveItinerary';
import { CrowdDashboard } from '../CrowdDashboard';
import { PlaceCrowdStatus, CrowdAlternativeCard, CrowdSystemStatusResponse, CrowdRecommendationResponse } from '../../types';

describe('Stage 3 CrowdSense Frontend Components', () => {
  const mockOriginal: PlaceCrowdStatus = {
    place_id: 'kawaguchiko_oishi_park',
    name_ja: '大石公園',
    name_en: 'Oishi Park',
    scenario: 'high',
    crowd_level: 'high',
    crowd_index: 88,
    capacity_percentage: 95,
    congestion_advisory: 'Heavy tourist volume. Expect dense crowds at viewpoints.',
    data_classification: 'SIMULATED_BASELINE',
    real_time_telemetry_status: 'UNAVAILABLE',
    image_url: 'https://images.unsplash.com/test-oishi.jpg',
    image_attribution: 'Test Photo',
    fuji_view_rating: 5,
    accessibility_status: 'VERIFIED_ACCESSIBLE',
    primary_category: 'viewpoint',
  };

  const mockAlternative: CrowdAlternativeCard = {
    place_id: 'nagasaki_park',
    name_ja: '長崎公園',
    name_en: 'Nagasaki Park',
    primary_category: 'viewpoint',
    crowd_level: 'low',
    crowd_index: 22,
    crowd_reduction_percent: 75,
    distance_km: 1.8,
    fuji_view_rating: 4,
    accessibility_status: 'VERIFIED_ACCESSIBLE',
    admission_type: 'FREE',
    admission_fee_jpy: null,
    image_url: 'https://images.unsplash.com/test-nagasaki.jpg',
    image_attribution: 'Nagasaki Photo',
    recommendation_reason: 'Direct lakeside view of Mount Fuji comparable to Oishi Park with 75% fewer tourists.',
    match_score: 92,
  };

  describe('DestinationComparisonModal', () => {
    it('renders side-by-side comparison with crowd delta advantage', () => {
      const onSelect = vi.fn();
      const onClose = vi.fn();

      render(
        <DestinationComparisonModal
          isOpen={true}
          onClose={onClose}
          originalPlace={mockOriginal}
          alternative={mockAlternative}
          onSelectAlternative={onSelect}
        />
      );

      expect(screen.getByText('Side-by-Side Destination Comparison')).toBeDefined();
      expect(screen.getByText(/Crowd Reduction Advantage: -75% Fewer Visitors/i)).toBeDefined();
      expect(screen.getByText('Oishi Park')).toBeDefined();
      expect(screen.getAllByText('Nagasaki Park').length).toBeGreaterThan(0);
      expect(screen.getByText(/Why this fits:/i)).toBeDefined();
      expect(screen.getByText(mockAlternative.recommendation_reason)).toBeDefined();
    });

    it('triggers onSelectAlternative when confirm button is clicked', () => {
      const onSelect = vi.fn();
      const onClose = vi.fn();

      render(
        <DestinationComparisonModal
          isOpen={true}
          onClose={onClose}
          originalPlace={mockOriginal}
          alternative={mockAlternative}
          onSelectAlternative={onSelect}
        />
      );

      const selectBtn = screen.getByText(/Select Nagasaki Park & Recalculate Route/i);
      fireEvent.click(selectBtn);

      expect(onSelect).toHaveBeenCalledWith(mockAlternative);
      expect(onClose).toHaveBeenCalled();
    });
  });

  describe('AdaptiveItinerary', () => {
    it('renders adaptive banner when itinerary is adapted', async () => {
      // Mock global fetch for transit
      global.fetch = vi.fn().mockImplementation((url: string) => {
        if (url.includes('/api/transit/plan')) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                journeys: [
                  {
                    journey_id: 'j_adapt_1',
                    departure_time: '09:00',
                    arrival_time: '09:27',
                    total_duration_minutes: 27,
                    transfers_count: 0,
                    total_fare_jpy: null,
                    provenance_badges: ['Fujikyu GTFS'],
                    warnings: [],
                    legs: [
                      {
                        mode: 'bus',
                        operator: 'Fujikyu Bus',
                        route_id: '80611',
                        route_short_name: 'Red Line',
                        route_long_name: '河口湖周遊バス',
                        route_color: '#E60012',
                        route_text_color: '#FFFFFF',
                        origin_stop_id: '0025_01',
                        origin_stop_name: '河口湖駅',
                        origin_stop_name_en: 'Kawaguchiko Station',
                        departure_time: '09:00',
                        departure_timestamp_sec: 32400,
                        destination_stop_id: '1857_01',
                        destination_stop_name: '河口湖自然生活館',
                        destination_stop_name_en: 'Kawaguchiko Natural Living Center',
                        arrival_time: '09:27',
                        arrival_timestamp_sec: 34020,
                        duration_minutes: 27,
                        intermediate_stops_count: 20,
                        intermediate_stops: [],
                        fare_jpy: null,
                        provenance: 'GTFS',
                        provenance_badge: 'Fujikyu GTFS',
                      },
                    ],
                  },
                ],
              }),
          });
        }
        return Promise.resolve({ ok: false });
      });

      render(
        <AdaptiveItinerary
          originName="Kawaguchiko Station"
          activeDestinationName="Nagasaki Park"
          activeDestinationJa="長崎公園"
          originalDestinationName="Oishi Park"
          isAdapted={true}
          crowdReductionPercent={75}
        />
      );

      expect(screen.getByText('Adaptive Transit Itinerary')).toBeDefined();
      expect(screen.getByText(/Adaptive Route Active/i)).toBeDefined();
      expect(screen.getByText(/Crowd Reduction/i)).toBeDefined();

      await waitFor(() => {
        expect(screen.getByText(/Red Line/i)).toBeDefined();
      });
    });
  });

  describe('CrowdDashboard', () => {
    it('renders hero title and scenario controls', async () => {
      global.fetch = vi.fn().mockImplementation((url: string) => {
        if (url.includes('/api/crowd/status')) {
          const res: CrowdSystemStatusResponse = {
            active_scenario: 'high',
            available_scenarios: ['low', 'moderate', 'high'],
            data_classification: 'SIMULATED_BASELINE',
            real_time_telemetry_status: 'UNAVAILABLE',
            hero_image_url: 'https://images.unsplash.com/hero.jpg',
            hero_image_attribution: 'Test Hero Attribution',
            places: [mockOriginal],
          };
          return Promise.resolve({ ok: true, json: () => Promise.resolve(res) });
        }
        if (url.includes('/api/crowd/recommendations')) {
          const res: CrowdRecommendationResponse = {
            current_place_id: 'kawaguchiko_oishi_park',
            current_place_name: 'Oishi Park',
            current_crowd_level: 'high',
            current_congestion_advisory: 'Heavy crowd',
            current_scenario: 'high',
            data_classification: 'SIMULATED_BASELINE',
            real_time_telemetry_status: 'UNAVAILABLE',
            alternatives: [mockAlternative],
          };
          return Promise.resolve({ ok: true, json: () => Promise.resolve(res) });
        }
        if (url.includes('/api/transit/plan')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ journeys: [] }),
          });
        }
        return Promise.resolve({ ok: false });
      });

      render(<CrowdDashboard />);

      expect(screen.getByText('CrowdSense Adaptive Intelligence')).toBeDefined();
      expect(screen.getByText('SIMULATED DATA')).toBeDefined();
      expect(screen.getByText(/Real-time Telemetry: UNAVAILABLE/i)).toBeDefined();
      expect(screen.getByText('🔴 High Crowd')).toBeDefined();
      expect(screen.getByText('🌿 Prefer Quiet')).toBeDefined();

      await waitFor(() => {
        expect(screen.getByText('CrowdSense Recommended Alternatives')).toBeDefined();
      });
    });
  });
});
