import { describe, it, expect } from 'vitest';
import {
  formatTimestamp,
  formatTelemetryValue,
  formatSimilarity,
  formatDurationSeconds,
  formatDurationNanos
} from '../utils/formatters';

describe('formatters utility', () => {
  it('formats telemetry values correctly', () => {
    expect(formatTelemetryValue(92.543, '°C', 1)).toBe('92.5 °C');
    expect(formatTelemetryValue(null, '°C')).toBe('N/A');
    expect(formatTelemetryValue(undefined, 'mm/s')).toBe('N/A');
    expect(formatTelemetryValue(NaN, 'A')).toBe('N/A');
    expect(formatTelemetryValue(14.8, 'mm/s')).toBe('14.8 mm/s');
  });

  it('formats similarity scores', () => {
    expect(formatSimilarity(0.85)).toBe('85.0% (0.8500)');
    expect(formatSimilarity(0.7634)).toBe('76.3% (0.7634)');
    expect(formatSimilarity(null)).toBe('N/A');
    expect(formatSimilarity(undefined)).toBe('N/A');
  });

  it('formats seconds and durations', () => {
    expect(formatDurationSeconds(3.1415)).toBe('3.14s');
    expect(formatDurationSeconds(null)).toBe('N/A');
    expect(formatDurationNanos(38000000000)).toBe('38.00s');
    expect(formatDurationNanos(450000000)).toBe('450ms');
    expect(formatDurationNanos(null)).toBe('N/A');
  });

  it('formats timestamps', () => {
    expect(formatTimestamp(null)).toBe('N/A');
    expect(formatTimestamp('2026-10-01T02:00:00')).toContain('2026');
  });
});
