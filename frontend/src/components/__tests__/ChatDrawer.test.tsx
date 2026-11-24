import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatDrawer } from '../ChatDrawer';
import { Place } from '../../types';

const mockPlace: Place = {
  place_id: 'kawaguchiko_oishi_park',
  name_ja: '大石公園',
  name_en: 'Oishi Park',
  latitude: 35.523611,
  longitude: 138.745278,
  coords_source: 'MLIT_P12',
  primary_category: 'viewpoint',
  sub_category: 'botanical_park',
  opening_status: 'ALWAYS_OPEN',
  opening_hours_text: '24 hours',
  opening_hours_source: 'Fujikawaguchiko Town Office',
  general_admission_type: 'FREE',
  general_admission_fee_jpy: null,
  optional_activities_fee_desc: 'Free general park entry; cafe and souvenir shops paid',
  admission_fee_source: 'Fujikawaguchiko Town Office',
  accessibility_status: 'VERIFIED_ACCESSIBLE',
  accessibility_evidence: 'Paved lakefront promenade, flat terrain, wheelchair accessible public toilets',
  stair_step_count: 0,
  accessibility_source: 'Yamanashi Barrier-Free Tourism Directory',
  fuji_view_rating: 5,
  indoor_alternative: false,
  provenance_tier: 'OFFICIAL_GOV',
  source_url: 'https://www.town.fujikawaguchiko.lg.jp/',
  required_attribution: '出典：富士河口湖町公式ウェブサイト',
  source_retrieval_date: '2026-11-08',
  last_verified_date: '2026-11-08'
};

describe('ChatDrawer Component (Acceptance Test T1-15)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    Element.prototype.scrollIntoView = vi.fn();
  });

  it('renders initial welcome message from Hana', () => {
    render(<ChatDrawer sessionId="test_session" />);
    expect(screen.getByText(/Konnichiwa! I'm Hana/i)).toBeInTheDocument();
  });

  it('streams response tokens and renders place card on SSE events', async () => {
    const ssePayload = [
      'event: token\ndata: {"token": "I recommend visiting "}\n\n',
      'event: token\ndata: {"token": "Oishi Park!"}\n\n',
      `event: places\ndata: ${JSON.stringify([mockPlace])}\n\n`,
      'event: done\ndata: {"session_id": "test_session", "profile": {"party_composition": "couple"}}\n\n'
    ].join('');

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(ssePayload));
        controller.close();
      }
    });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: stream
    } as any);

    render(<ChatDrawer sessionId="test_session" />);

    const input = screen.getByPlaceholderText(/Ask Hana/i);
    const sendBtn = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Where should we go?' } });
    fireEvent.click(sendBtn);

    // Verify user message appears
    expect(screen.getByText('Where should we go?')).toBeInTheDocument();

    // Verify streamed tokens assemble in UI
    await waitFor(() => {
      expect(screen.getByText(/I recommend visiting Oishi Park!/i)).toBeInTheDocument();
    });

    // Verify grounded place card is rendered with verified attributes
    await waitFor(() => {
      expect(screen.getByText('大石公園')).toBeInTheDocument();
      expect(screen.getByText('Oishi Park')).toBeInTheDocument();
      expect(screen.getByText(/Barrier-Free Accessible/i)).toBeInTheDocument();
      expect(screen.getByText(/Free Admission/i)).toBeInTheDocument();
      expect(screen.getByText(/Fuji 5\/5/i)).toBeInTheDocument();
    });
  });
});
