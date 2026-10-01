import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom';
import { DeviceDetail } from '../pages/DeviceDetail';
import { DiagnosisDetail } from '../pages/DiagnosisDetail';
import * as api from '../services/api';

describe('Page Routes Suite', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders DeviceDetail with real history and telemetry trend chart', async () => {
    const mockHistory = [
      {
        id: 'diag-ESP32-1',
        deviceId: 'ESP32_001',
        timestamp: '2026-10-01T02:00:00',
        telemetry: {
          deviceId: 'ESP32_001',
          temperature: 92.5,
          vibration: 14.8,
          current: 28.5,
          pressure: 2.1
        },
        diagnosis: {
          primaryFault: { faultId: 'FAULT-001', title: 'Bearing Wear' },
          confidence: { level: 'HIGH' }
        }
      }
    ];

    vi.spyOn(api, 'getDiagnosesByDeviceId').mockResolvedValueOnce(mockHistory);

    render(
      <MemoryRouter initialEntries={['/device/ESP32_001']}>
        <Routes>
          <Route path="/device/:deviceId" element={<DeviceDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Device: ESP32_001')).toBeInTheDocument();
    });

    expect(screen.getByText(/Latest Telemetry Snapshot for ESP32_001/i)).toBeInTheDocument();
    expect(screen.getByText(/Telemetry Progression Trends/i)).toBeInTheDocument();
    expect(screen.getByText('Bearing Wear')).toBeInTheDocument();
  });

  it('renders DiagnosisDetail with full 10 diagnostic sections', async () => {
    const mockRecord = {
      id: 'diag-ESP32_001-XYZ',
      deviceId: 'ESP32_001',
      timestamp: '2026-10-01T02:00:00',
      latencySeconds: 2.3,
      telemetry: {
        deviceId: 'ESP32_001',
        temperature: 94.0,
        vibration: 15.0,
        current: 29.0,
        pressure: 2.2
      },
      diagnosis: {
        query: 'Telemetry assessment query',
        primaryFault: {
          faultId: 'FAULT-002',
          title: 'High Vibration Imbalance',
          explanation: 'Severe imbalance detected'
        },
        confidence: {
          level: 'HIGH',
          reason: 'Vibration exceeding threshold'
        },
        evidence: [
          { type: 'telemetry', parameter: 'vibration', value: 15.0, unit: 'mm/s' }
        ],
        knowledgeSources: [
          { rank: 1, documentId: 'DOC-02', title: 'Imbalance Manual', similarity: 0.91 }
        ],
        possibleCauses: ['Rotor unbalance', 'Shaft misalignment'],
        recommendedChecks: ['Perform dynamic balancing', 'Check alignment'],
        model: 'qwen2.5:1.5b',
        generationDetails: {
          provider: 'ollama',
          latencySeconds: 2.3
        }
      }
    };

    vi.spyOn(api, 'getDiagnosisById').mockResolvedValueOnce(mockRecord);

    render(
      <MemoryRouter initialEntries={['/diagnosis/diag-ESP32_001-XYZ']}>
        <Routes>
          <Route path="/diagnosis/:id" element={<DiagnosisDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText('High Vibration Imbalance').length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Fault Code: FAULT-002')).toBeInTheDocument();
    expect(screen.getByText('Severe imbalance detected')).toBeInTheDocument();
    expect(screen.getByText('Perform dynamic balancing')).toBeInTheDocument();
    expect(screen.getByText('Rotor unbalance')).toBeInTheDocument();
  });
});

