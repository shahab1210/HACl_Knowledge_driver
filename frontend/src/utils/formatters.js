/**
 * Formatting utility helpers for industrial IoT telemetry and diagnosis data.
 */

export function formatTimestamp(ts) {
  if (!ts) return 'N/A';
  try {
    const date = new Date(ts);
    if (isNaN(date.getTime())) return String(ts);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch {
    return String(ts);
  }
}

export function formatTelemetryValue(val, unit = '', precision = 1) {
  if (val === null || val === undefined || isNaN(Number(val))) {
    return 'N/A';
  }
  const num = Number(val);
  const formatted = precision !== null ? num.toFixed(precision) : String(num);
  return unit ? `${formatted} ${unit}` : formatted;
}

export function formatSimilarity(sim) {
  if (sim === null || sim === undefined || isNaN(Number(sim))) {
    return 'N/A';
  }
  const num = Number(sim);
  return `${(num * 100).toFixed(1)}% (${num.toFixed(4)})`;
}

export function formatDurationSeconds(sec) {
  if (sec === null || sec === undefined || isNaN(Number(sec))) {
    return 'N/A';
  }
  return `${Number(sec).toFixed(2)}s`;
}

export function formatDurationNanos(nanos) {
  if (!nanos || isNaN(Number(nanos))) return 'N/A';
  const ms = Number(nanos) / 1_000_000;
  if (ms >= 1000) {
    return `${(ms / 1000).toFixed(2)}s`;
  }
  return `${ms.toFixed(0)}ms`;
}
