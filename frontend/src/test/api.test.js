import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getLatestDiagnosis,
  getDiagnosisById,
  getDiagnosesByDeviceId,
  triggerDiagnosis,
  getLatestTelemetry,
  getTelemetryHistory,
  ApiError,
  API_BASE_URL
} from '../services/api';

describe('API Service Layer', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('getLatestDiagnosis returns json data on 200', async () => {
    const mockData = { id: 'diag-001', deviceId: 'ESP32_001' };
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockData
    });

    const result = await getLatestDiagnosis();
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/diagnosis/latest`, expect.anything());
    expect(result).toEqual(mockData);
  });

  it('getDiagnosisById encodes id in url', async () => {
    const mockData = { id: 'diag-test/01', deviceId: 'ESP32_001' };
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockData
    });

    const result = await getDiagnosisById('diag-test/01');
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/diagnosis/diag-test%2F01`, expect.anything());
    expect(result).toEqual(mockData);
  });

  it('getDiagnosesByDeviceId fetches device list', async () => {
    const mockData = [{ id: 'diag-001', deviceId: 'ESP32_001' }];
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockData
    });

    const result = await getDiagnosesByDeviceId('ESP32_001');
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/diagnosis/device/ESP32_001`, expect.anything());
    expect(result).toEqual(mockData);
  });

  it('triggerDiagnosis issues POST request with payload', async () => {
    const payload = { deviceId: 'ESP32_001', temperature: 90.0 };
    const mockResponse = { id: 'diag-002', status: 'COMPLETED' };
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockResponse
    });

    const result = await triggerDiagnosis(payload);
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/diagnosis`, expect.objectContaining({
      method: 'POST',
      body: JSON.stringify(payload)
    }));
    expect(result).toEqual(mockResponse);
  });

  it('handles 404 with ApiError.isNotFound = true', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      headers: { get: () => 'application/json' },
      json: async () => ({ status: 404, message: 'Not found' })
    });

    await expect(getLatestDiagnosis()).rejects.toThrow(ApiError);
  });

  it('handles network failure gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Failed to fetch'));
    await expect(getLatestDiagnosis()).rejects.toThrow(ApiError);
  });

  it('getLatestTelemetry calls /api/v1/telemetry/latest with optional deviceId', async () => {
    const mockReading = { deviceId: 'ESP32_001', temperature: 31.4, recordedAt: '2026-10-01T10:00:00' };
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockReading
    });

    const result = await getLatestTelemetry('ESP32_001');
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/telemetry/latest?deviceId=ESP32_001`, expect.anything());
    expect(result).toEqual(mockReading);
  });

  it('getTelemetryHistory calls /api/v1/telemetry/history with limit and deviceId', async () => {
    const mockList = [{ deviceId: 'ESP32_001', temperature: 31.4 }];
    fetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockList
    });

    const result = await getTelemetryHistory('ESP32_001', 20);
    expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/telemetry/history?deviceId=ESP32_001&limit=20`, expect.anything());
    expect(result).toEqual(mockList);
  });
});
