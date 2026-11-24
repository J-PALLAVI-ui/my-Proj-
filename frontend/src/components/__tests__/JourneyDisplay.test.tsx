import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { JourneyDisplay } from '../JourneyDisplay';
import { Journey } from '../../types';

const mockJourney: Journey = {
  journey_id: 'journey_test_01',
  departure_time: '08:15',
  arrival_time: '09:57',
  total_duration_minutes: 101,
  transfers_count: 1,
  total_fare_jpy: 1740,
  provenance_badges: [
    '[Fujikyu Railway Timetable (Rev. 2026-03-14)]',
    '[Official Fujikyu Bus GTFS-JP]'
  ],
  warnings: [
    'Weekend advisory: Bus may experience 10-15 min traffic delay along the lake.'
  ],
  legs: [
    {
      mode: 'rail',
      operator: 'Fujikyu Railway',
      route_id: 'rail_local_out',
      route_short_name: 'Fuji Kyuko Line',
      route_long_name: '富士山麓電気鉄道 富士急行線（普通 河口湖行）',
      route_color: '#007AC9',
      route_text_color: '#FFFFFF',
      trip_headsign: '河口湖行 (for Kawaguchiko)',
      origin_stop_id: 'rail_otsuki',
      origin_stop_name: '大月駅',
      origin_stop_name_en: 'Otsuki Station',
      departure_time: '08:15',
      departure_timestamp_sec: 29700,
      destination_stop_id: 'rail_kawaguchiko',
      destination_stop_name: '河口湖駅',
      destination_stop_name_en: 'Kawaguchiko Station',
      arrival_time: '09:16',
      arrival_timestamp_sec: 33360,
      duration_minutes: 61,
      intermediate_stops_count: 16,
      intermediate_stops: ['Kami-Otsuki Station', 'Tanokura Station'],
      fare_jpy: 1170,
      provenance: 'MANUALLY_TRANSCRIBED',
      provenance_badge: '[Fujikyu Railway Timetable (Rev. 2026-03-14)]',
      advisory_notes: 'Otsuki station provides 5-min connection to JR Chuo Line.'
    },
    {
      mode: 'walk',
      operator: 'Walk',
      route_short_name: 'Walk',
      route_long_name: 'Walk 33m to Kawaguchiko Sta.',
      route_color: '#757575',
      route_text_color: '#FFFFFF',
      origin_stop_id: 'rail_kawaguchiko',
      origin_stop_name: '河口湖駅',
      origin_stop_name_en: 'Kawaguchiko Station',
      departure_time: '09:16',
      departure_timestamp_sec: 33360,
      destination_stop_id: '0025_01',
      destination_stop_name: '河口湖駅',
      destination_stop_name_en: 'Kawaguchiko Sta.',
      arrival_time: '09:18',
      arrival_timestamp_sec: 33480,
      duration_minutes: 2,
      intermediate_stops_count: 0,
      intermediate_stops: [],
      fare_jpy: 0,
      provenance: 'ESTIMATED',
      provenance_badge: '[Walking Connection]'
    },
    {
      mode: 'bus',
      operator: 'Fujikyu Bus',
      route_id: '44511',
      route_short_name: 'Red Line',
      route_long_name: '河口湖周遊バス（レッドライン）',
      route_color: '#E60012',
      route_text_color: '#FFFFFF',
      trip_headsign: '自然生活館行',
      origin_stop_id: '0025_01',
      origin_stop_name: '河口湖駅',
      origin_stop_name_en: 'Kawaguchiko Sta.',
      departure_time: '09:30',
      departure_timestamp_sec: 34200,
      destination_stop_id: '1857_01',
      destination_stop_name: '河口湖自然生活館',
      destination_stop_name_en: 'Kawaguchiko Shizenseikatsukan',
      arrival_time: '09:57',
      arrival_timestamp_sec: 35820,
      duration_minutes: 27,
      intermediate_stops_count: 20,
      intermediate_stops: ['Funatsuhama-onsen-gai'],
      fare_jpy: 570,
      provenance: 'STATIC',
      provenance_badge: '[Official Fujikyu Bus GTFS-JP]',
      advisory_notes: 'Bus may experience 10-15 min traffic delay along the lake.'
    }
  ]
};

describe('JourneyDisplay Component (Acceptance Test T2-20)', () => {
  it('renders journey header with departure, arrival, duration, transfers, and fare', () => {
    render(<JourneyDisplay journeys={[mockJourney]} />);

    expect(screen.getAllByText('08:15').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('09:57').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/101 min/i)).toBeInTheDocument();
    expect(screen.getByText(/1 transfer/i)).toBeInTheDocument();
    expect(screen.getByText(/¥1,740/i)).toBeInTheDocument();
  });

  it('renders ordered journey legs with operator names, stop details, and official route colors', () => {
    const { container } = render(<JourneyDisplay journeys={[mockJourney]} />);

    // Fujikyu Railway leg
    expect(screen.getByText(/Fuji Kyuko Line/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Otsuki Station/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/¥1,170/i)).toBeInTheDocument();
    expect(screen.getAllByText(/\[Fujikyu Railway Timetable \(Rev\. 2026-03-14\)\]/i).length).toBeGreaterThanOrEqual(1);

    // Fujikyu Bus Red Line leg
    expect(screen.getByText(/Red Line/i)).toBeInTheDocument();
    expect(screen.getByText(/Kawaguchiko Shizenseikatsukan/i)).toBeInTheDocument();
    expect(screen.getByText(/¥570/i)).toBeInTheDocument();
    expect(screen.getAllByText(/\[Official Fujikyu Bus GTFS-JP\]/i).length).toBeGreaterThanOrEqual(1);

    // Walking leg
    expect(screen.getByText(/\[Walking Connection\]/i)).toBeInTheDocument();

    // Check color badge styles in DOM
    const redBadge = screen.getByText('Red Line');
    expect(redBadge).toHaveStyle({ backgroundColor: '#E60012' });

    const railBadge = screen.getByText('Fuji Kyuko Line');
    expect(railBadge).toHaveStyle({ backgroundColor: '#007AC9' });
  });

  it('renders traffic advisory warning when present', () => {
    render(<JourneyDisplay journeys={[mockJourney]} />);
    expect(screen.getByText(/Weekend advisory: Bus may experience 10-15 min traffic delay/i)).toBeInTheDocument();
  });
});
