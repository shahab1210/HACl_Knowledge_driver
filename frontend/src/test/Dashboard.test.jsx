import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from '../pages/Dashboard';
import * as api from '../services/api';

describe('Dashboard Page Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading state initially and then shows diagnosis data', async () => {
    const mockDiagnosis = {
      id: 'diag-ESP32_001-TEST',
      deviceId: 'ESP32_001',
      timestamp: '2026-10-01T02:00:00',
      latencySeconds: 2.5,
      telemetry: {
        deviceId: 'ESP32_001',
        temperature: 92.5,
        vibration: 14.8,
        current: 28.5,
        pressure: 2.1,
      },
      diagnosis: {
        query: 'Telemetry query',
        primaryFault: {
          faultId: 'FAULT-001',
          title: 'Bearing Wear Degradation',
          similarity: 0.89,
        },
        confidence: {
          level: 'HIGH',
          reason: 'Vibration match',
        },
        evidence: [
          { type: 'telemetry', parameter: 'temperature', value: 92.5, unit: '°C' }
        ],
        knowledgeSources: [
          { rank: 1, documentId: 'DOC-1', title: 'Bearing Guide', similarity: 0.89 }
        ],
        model: 'qwen2.5:1.5b'
      }
    };

    vi.spyOn(api, 'getLatestDiagnosis').mockResolvedValueOnce(mockDiagnosis);
    vi.spyOn(api, 'getDiagnosesByDeviceId').mockResolvedValueOnce([mockDiagnosis]);

    render(
      <BrowserRouter>
        <Dashboard
          isManualOpen={false}
          onCloseManual={() => {}}
          onOpenManual={() => {}}
          onStatusChange={() => {}}
        />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText('Bearing Wear Degradation').length).toBeGreaterThan(0);
    });

    expect(screen.getAllByText('FAULT-001').length).toBeGreaterThan(0);
    expect(screen.getAllByText('ESP32_001').length).toBeGreaterThan(0);
    expect(screen.getAllByText(/92.5/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/14.8/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/HIGH CONFIDENCE/i).length).toBeGreaterThan(0);
  });

  it('renders empty state when API returns 404', async () => {
    const error404 = new api.ApiError('No diagnoses available yet', 404);
    vi.spyOn(api, 'getLatestDiagnosis').mockRejectedValueOnce(error404);

    render(
      <BrowserRouter>
        <Dashboard
          isManualOpen={false}
          onCloseManual={() => {}}
          onOpenManual={() => {}}
          onStatusChange={() => {}}
        />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No Active Diagnosis Found')).toBeInTheDocument();
    });
  });

  it('renders error alert when API call fails with network error', async () => {
    const errorNet = new api.ApiError('Unable to connect to Spring Boot backend', 0);
    vi.spyOn(api, 'getLatestDiagnosis').mockRejectedValueOnce(errorNet);

    render(
      <BrowserRouter>
        <Dashboard
          isManualOpen={false}
          onCloseManual={() => {}}
          onOpenManual={() => {}}
          onStatusChange={() => {}}
        />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Spring Boot API Connection Error')).toBeInTheDocument();
    });
  });

  it('renders live telemetry and LIVE STREAM badge when getLatestTelemetry succeeds', async () => {
    const mockDiagnosis = {
      id: 'diag-ESP32_001-TEST',
      deviceId: 'ESP32_001',
      timestamp: '2026-10-01T02:00:00',
      telemetry: {
        deviceId: 'ESP32_001',
        temperature: 25.0,
        vibration: 2.0,
        current: 5.0,
        pressure: 2.0,
      },
      diagnosis: {
        primaryFault: { faultId: 'FAULT-001', title: 'Normal Operation' },
        confidence: { level: 'HIGH' }
      }
    };

    const mockLiveTelemetry = {
      deviceId: 'ESP32_001',
      temperature: 31.4,
      vibration: 1.8,
      current: 5.6,
      pressure: 2.7,
      recordedAt: '2026-10-01T12:00:00'
    };

    vi.spyOn(api, 'getLatestDiagnosis').mockResolvedValueOnce(mockDiagnosis);
    vi.spyOn(api, 'getDiagnosesByDeviceId').mockResolvedValueOnce([mockDiagnosis]);
    vi.spyOn(api, 'getLatestTelemetry').mockResolvedValue(mockLiveTelemetry);
    vi.spyOn(api, 'getTelemetryHistory').mockResolvedValue([mockLiveTelemetry]);

    render(
      <BrowserRouter>
        <Dashboard
          isManualOpen={false}
          onCloseManual={() => {}}
          onOpenManual={() => {}}
          onStatusChange={() => {}}
        />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('LIVE STREAM')).toBeInTheDocument();
      expect(screen.getByText('31.4')).toBeInTheDocument();
    });
  });
});
