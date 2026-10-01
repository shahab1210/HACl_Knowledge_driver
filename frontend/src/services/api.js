/**
 * Centralized API Service for IoT Fault Diagnosis Spring Boot Backend (P14/P15/P19).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
export const AUTH_TOKEN_KEY = 'iot_auth_token';

export function getAuthToken() {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token) {
  try {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
  } catch {
    // ignore storage errors
  }
}

export function removeAuthToken() {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  } catch {
    // ignore storage errors
  }
}

export class ApiError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.isNotFound = status === 404;
    this.isServiceUnavailable = status === 503;
    this.isBadRequest = status === 400;
    this.isUnauthorized = status === 401;
    this.isForbidden = status === 403;
    this.isConflict = status === 409;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...options.headers,
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    const contentType = response.headers.get('content-type') || '';
    let data = null;

    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { message: text } : null;
    }

    if (!response.ok) {
      if (response.status === 401 && !endpoint.startsWith('/api/v1/auth/login')) {
        // Token is invalid/expired
        removeAuthToken();
      }
      const message = data?.message || data?.error || `HTTP error ${response.status}`;
      throw new ApiError(message, response.status, data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network / connection refused errors
    throw new ApiError(
      error.message || 'Unable to connect to Spring Boot backend. Ensure the server is running on ' + API_BASE_URL,
      0,
      { originalError: error }
    );
  }
}

/* =========================================================================
   Authentication API (P19)
   ========================================================================= */

/**
 * Register a new user.
 * @param {Object} payload { username, email, password, role }
 * @returns {Promise<Object>} AuthResponse { token, tokenType, username, email, role, expiresInSeconds }
 */
export async function register(payload) {
  const data = await request('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (data?.token) {
    setAuthToken(data.token);
  }
  return data;
}

/**
 * Login with username/email and password.
 * @param {Object} payload { usernameOrEmail, password }
 * @returns {Promise<Object>} AuthResponse { token, tokenType, username, email, role, expiresInSeconds }
 */
export async function login(payload) {
  const data = await request('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (data?.token) {
    setAuthToken(data.token);
  }
  return data;
}

/**
 * Fetch the authenticated user's profile.
 * @returns {Promise<Object>} UserResponse { id, username, email, role, createdAt }
 */
export async function getCurrentUser() {
  return request('/api/v1/auth/me');
}

/**
 * Log out user by removing stored authentication credentials.
 */
export function logout() {
  removeAuthToken();
}

/* =========================================================================
   Diagnosis API (P14/P15)
   ========================================================================= */

/**
 * Retrieve the most recent fault diagnosis across all IoT devices.
 * @returns {Promise<Object>} DiagnosisResponse
 */
export async function getLatestDiagnosis() {
  return request('/api/v1/diagnosis/latest');
}

/**
 * Retrieve a specific diagnosis by its unique ID (e.g. diag-ESP32_001-12345).
 * @param {string} id
 * @returns {Promise<Object>} DiagnosisResponse
 */
export async function getDiagnosisById(id) {
  if (!id) throw new Error('Diagnosis ID is required');
  return request(`/api/v1/diagnosis/${encodeURIComponent(id)}`);
}

/**
 * Retrieve all diagnosis records for a specific device.
 * @param {string} deviceId
 * @returns {Promise<Array>} List of DiagnosisResponse
 */
export async function getDiagnosesByDeviceId(deviceId) {
  if (!deviceId) throw new Error('Device ID is required');
  return request(`/api/v1/diagnosis/device/${encodeURIComponent(deviceId)}`);
}

/**
 * Submit raw IoT sensor telemetry to trigger an on-demand AI fault diagnosis.
 * @param {Object} telemetry { deviceId, temperature, humidity, vibration, current, pressure }
 * @returns {Promise<Object>} DiagnosisResponse
 */
export async function triggerDiagnosis(telemetry) {
  return request('/api/v1/diagnosis', {
    method: 'POST',
    body: JSON.stringify(telemetry),
  });
}

/* =========================================================================
   Alerts & Notifications API (P20)
   ========================================================================= */

/**
 * Retrieve alerts filtered by device, acknowledged status, or severity.
 * @param {Object} params { deviceId, acknowledged, severity }
 * @returns {Promise<Array>} List of AlertResponse
 */
export async function getAlerts(params = {}) {
  const query = new URLSearchParams();
  if (params.deviceId) query.append('deviceId', params.deviceId);
  if (params.acknowledged !== undefined && params.acknowledged !== null) {
    query.append('acknowledged', params.acknowledged);
  }
  if (params.severity) query.append('severity', params.severity);

  const queryString = query.toString();
  const endpoint = queryString ? `/api/v1/alerts?${queryString}` : '/api/v1/alerts';
  return request(endpoint);
}

/**
 * Retrieve the single latest alert across all devices.
 * @returns {Promise<Object>} AlertResponse
 */
export async function getLatestAlert() {
  return request('/api/v1/alerts/latest');
}

/**
 * Retrieve an alert by its ID.
 * @param {number|string} id
 * @returns {Promise<Object>} AlertResponse
 */
export async function getAlertById(id) {
  if (!id) throw new Error('Alert ID is required');
  return request(`/api/v1/alerts/${encodeURIComponent(id)}`);
}

/**
 * Acknowledge an active alert by ID.
 * @param {number|string} id
 * @returns {Promise<Object>} AlertResponse
 */
export async function acknowledgeAlert(id) {
  if (!id) throw new Error('Alert ID is required');
  return request(`/api/v1/alerts/${encodeURIComponent(id)}/acknowledge`, {
    method: 'POST',
  });
}

/* =========================================================================
   Live Raw Telemetry API (sensor_readings)
   ========================================================================= */

/**
 * Retrieve the most recent raw sensor telemetry reading from PostgreSQL.
 * @param {string} [deviceId] Optional device ID filter (e.g. ESP32_001)
 * @returns {Promise<Object>} TelemetryResponse { deviceId, temperature, humidity, vibration, current, pressure, recordedAt }
 */
export async function getLatestTelemetry(deviceId) {
  const query = deviceId ? `?deviceId=${encodeURIComponent(deviceId)}` : '';
  return request(`/api/v1/telemetry/latest${query}`);
}

/**
 * Retrieve recent raw sensor telemetry readings in chronological order for charting.
 * @param {string} [deviceId] Optional device ID filter (e.g. ESP32_001)
 * @param {number} [limit=20] Max readings to return (1-100)
 * @returns {Promise<Array>} List of TelemetryResponse
 */
export async function getTelemetryHistory(deviceId, limit = 20) {
  const params = new URLSearchParams();
  if (deviceId) params.append('deviceId', deviceId);
  if (limit) params.append('limit', limit);
  return request(`/api/v1/telemetry/history?${params.toString()}`);
}

export { API_BASE_URL };
