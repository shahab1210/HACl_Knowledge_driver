import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AlertWidget } from '../components/alerts/AlertWidget';
import * as api from '../services/api';

describe('Alerts & Notifications Suite (P20)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockAlerts = [
    {
      id: 1,
      deviceId: 'ESP32_001',
      alertType: 'SENSOR_THRESHOLD',
      severity: 'CRITICAL',
      message: 'Critical temperature (94.5°C >= 90.0°C). Risk of motor burnout.',
      source: 'TELEMETRY_INGESTION',
      sensorParameter: 'temperature',
      sensorValue: 94.5,
      thresholdValue: 90.0,
      createdAt: '2026-10-01T03:00:00',
      acknowledged: false,
    },
    {
      id: 2,
      deviceId: 'ESP32_001',
      alertType: 'SENSOR_THRESHOLD',
      severity: 'WARNING',
      message: 'Elevated vibration (5.10 mm/s >= 4.50 mm/s). Approaching limit.',
      source: 'TELEMETRY_INGESTION',
      sensorParameter: 'vibration',
      sensorValue: 5.1,
      thresholdValue: 4.5,
      createdAt: '2026-10-01T02:55:00',
      acknowledged: false,
    },
    {
      id: 3,
      deviceId: 'ESP32_001',
      alertType: 'SENSOR_THRESHOLD',
      severity: 'WARNING',
      message: 'High humidity detected',
      source: 'TELEMETRY_INGESTION',
      sensorParameter: 'humidity',
      sensorValue: 82.0,
      thresholdValue: 80.0,
      createdAt: '2026-10-01T02:30:00',
      acknowledged: true,
      acknowledgedBy: 'lead_operator',
      acknowledgedAt: '2026-10-01T02:35:00',
    },
  ];

  it('renders clean operational state when alerts list is empty', () => {
    render(<AlertWidget alerts={[]} />);

    expect(screen.getByText(/System Alerts & Notifications/i)).toBeInTheDocument();
    expect(screen.getByText(/^Normal$/i)).toBeInTheDocument();
    expect(screen.getByText(/No Active Alerts/i)).toBeInTheDocument();
    expect(screen.getByText(/All monitored IoT sensor channels are operating within normal authoritative thresholds/i)).toBeInTheDocument();
  });

  it('renders active alerts count badge and severity badges', () => {
    render(<AlertWidget alerts={mockAlerts} />);

    expect(screen.getByText('2 Active')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    expect(screen.getByText('WARNING')).toBeInTheDocument();
    expect(screen.getByText(/Critical temperature \(94.5°C >= 90.0°C\)/i)).toBeInTheDocument();
    expect(screen.getByText(/temperature: 94.5 \(Limit: 90\)/i)).toBeInTheDocument();
  });

  it('filters between Active, All, and Acknowledged views', () => {
    render(<AlertWidget alerts={mockAlerts} />);

    // Default: ACTIVE -> only unacknowledged shown (2 alerts)
    expect(screen.getAllByRole('button', { name: 'Acknowledge alert' }).length).toBe(2);
    expect(screen.queryByText(/Ack by lead_operator/i)).not.toBeInTheDocument();

    // Switch to ALL -> 3 alerts shown
    fireEvent.click(screen.getByRole('button', { name: /All \(3\)/i }));
    expect(screen.getByText(/Ack by lead_operator/i)).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Acknowledge alert' }).length).toBe(2);

    // Switch to ACKNOWLEDGED -> 1 alert shown
    fireEvent.click(screen.getByRole('button', { name: 'Acknowledged' }));
    expect(screen.getByText(/Ack by lead_operator/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Acknowledge alert' })).not.toBeInTheDocument();
  });

  it('triggers onAcknowledge callback when clicking Acknowledge button', async () => {
    const handleAck = vi.fn().mockResolvedValueOnce({ id: 1, acknowledged: true });
    render(<AlertWidget alerts={mockAlerts} onAcknowledge={handleAck} />);

    const ackButtons = screen.getAllByRole('button', { name: 'Acknowledge alert' });
    fireEvent.click(ackButtons[0]);

    expect(handleAck).toHaveBeenCalledWith(1);
  });

  describe('API Service Layer for Alerts', () => {
    it('getAlerts queries endpoint with query parameters', async () => {
      vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockAlerts,
      }));

      const res = await api.getAlerts({ deviceId: 'ESP32_001', acknowledged: false });
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/alerts?deviceId=ESP32_001&acknowledged=false'),
        expect.anything()
      );
      expect(res).toEqual(mockAlerts);
    });

    it('acknowledgeAlert issues POST request', async () => {
      const mockUpdated = { id: 1, acknowledged: true };
      vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockUpdated,
      }));

      const res = await api.acknowledgeAlert(1);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/alerts/1/acknowledge'),
        expect.objectContaining({ method: 'POST' })
      );
      expect(res).toEqual(mockUpdated);
    });
  });
});
