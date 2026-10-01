/**
 * Severity and confidence styling definitions for industrial monitoring UI.
 */

export function getConfidenceStyle(level) {
  const norm = (level || '').toLowerCase();
  switch (norm) {
    case 'high':
      return {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
        dot: 'bg-emerald-500',
        label: 'HIGH'
      };
    case 'medium':
      return {
        bg: 'bg-amber-500/10',
        text: 'text-amber-400',
        border: 'border-amber-500/30',
        dot: 'bg-amber-500',
        label: 'MEDIUM'
      };
    case 'low':
      return {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500/30',
        dot: 'bg-blue-500',
        label: 'LOW'
      };
    default:
      return {
        bg: 'bg-slate-500/10',
        text: 'text-slate-400',
        border: 'border-slate-500/30',
        dot: 'bg-slate-500',
        label: (level || 'UNKNOWN').toUpperCase()
      };
  }
}

export function getSensorStatus(type, value) {
  if (value === null || value === undefined) return { label: 'OFFLINE', color: 'slate' };
  const num = Number(value);
  if (isNaN(num)) return { label: 'UNKNOWN', color: 'slate' };

  switch (type.toLowerCase()) {
    case 'temperature':
      if (num > 85) return { label: 'CRITICAL', color: 'red', text: 'Critical Thermal Alert' };
      if (num > 70) return { label: 'WARNING', color: 'amber', text: 'Elevated Temperature' };
      return { label: 'NORMAL', color: 'emerald', text: 'Normal Operating Range' };
    case 'vibration':
      if (num > 10) return { label: 'CRITICAL', color: 'red', text: 'Excessive Vibration' };
      if (num > 6) return { label: 'WARNING', color: 'amber', text: 'Elevated Vibration' };
      return { label: 'NORMAL', color: 'emerald', text: 'Normal Vibration' };
    case 'current':
      if (num > 25) return { label: 'HIGH LOAD', color: 'amber', text: 'High Current Load' };
      return { label: 'NORMAL', color: 'emerald', text: 'Nominal Current' };
    case 'pressure':
      if (num < 1.0 || num > 5.0) return { label: 'WARNING', color: 'amber', text: 'Abnormal Pressure' };
      return { label: 'NORMAL', color: 'emerald', text: 'Nominal Pressure' };
    default:
      return { label: 'NORMAL', color: 'emerald', text: 'Normal' };
  }
}
