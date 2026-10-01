import React, { useState } from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle2, ShieldCheck, Clock, RefreshCw, Bell } from 'lucide-react';
import { formatTimestamp } from '../../utils/formatters';

export function AlertWidget({ alerts = [], onAcknowledge, isLoading = false, onRefresh }) {
  const [filter, setFilter] = useState('ACTIVE');
  const [ackingId, setAckingId] = useState(null);

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'ACTIVE') return !alert.acknowledged;
    if (filter === 'ACKNOWLEDGED') return alert.acknowledged;
    return true;
  });

  const activeCount = alerts.filter((a) => !a.acknowledged).length;
  const criticalCount = alerts.filter((a) => !a.acknowledged && a.severity === 'CRITICAL').length;

  const handleAcknowledge = async (id) => {
    if (!onAcknowledge) return;
    setAckingId(id);
    try {
      await onAcknowledge(id);
    } finally {
      setAckingId(null);
    }
  };

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return {
          card: 'border-red-800/80 bg-red-950/20 hover:bg-red-950/30',
          badge: 'bg-red-950 text-red-400 border-red-700/60',
          icon: <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />,
        };
      case 'WARNING':
        return {
          card: 'border-amber-800/80 bg-amber-950/20 hover:bg-amber-950/30',
          badge: 'bg-amber-950 text-amber-400 border-amber-700/60',
          icon: <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />,
        };
      default:
        return {
          card: 'border-cyan-800/80 bg-cyan-950/20 hover:bg-cyan-950/30',
          badge: 'bg-cyan-950 text-cyan-400 border-cyan-700/60',
          icon: <Info className="w-4 h-4 text-cyan-400 shrink-0" />,
        };
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      {/* Widget Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center text-cyan-400 border border-slate-700">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white tracking-wide">System Alerts & Notifications</h3>
              {activeCount > 0 ? (
                <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${
                  criticalCount > 0
                    ? 'bg-red-950/80 text-red-400 border-red-700/80 animate-pulse'
                    : 'bg-amber-950/80 text-amber-400 border-amber-700/80'
                }`}>
                  {activeCount} Active
                </span>
              ) : (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
                  Normal
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time threshold violations and critical diagnosis alarms
            </p>
          </div>
        </div>

        {/* Action and Filter Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800">
            <button
              onClick={() => setFilter('ACTIVE')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors ${
                filter === 'ACTIVE'
                  ? 'bg-slate-800 text-cyan-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Active ({activeCount})
            </button>
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors ${
                filter === 'ALL'
                  ? 'bg-slate-800 text-cyan-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({alerts.length})
            </button>
            <button
              onClick={() => setFilter('ACKNOWLEDGED')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors ${
                filter === 'ACKNOWLEDGED'
                  ? 'bg-slate-800 text-cyan-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Acknowledged
            </button>
          </div>

          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              title="Refresh alerts"
              className="p-1.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {/* Alerts Content */}
      <div className="mt-4">
        {filteredAlerts.length === 0 ? (
          <div className="py-8 px-4 text-center rounded-xl bg-slate-950/50 border border-slate-800/60 flex flex-col items-center justify-center">
            <ShieldCheck className="w-8 h-8 text-emerald-400 mb-2" />
            <h4 className="text-xs font-bold text-slate-300">
              {filter === 'ACTIVE' ? 'No Active Alerts' : 'No Alerts in this View'}
            </h4>
            <p className="text-[11px] text-slate-500 mt-1 max-w-sm">
              All monitored IoT sensor channels are operating within normal authoritative thresholds.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
            {filteredAlerts.map((alert) => {
              const style = getSeverityStyle(alert.severity);
              const isAcking = ackingId === alert.id;

              return (
                <div
                  key={alert.id}
                  className={`p-3.5 rounded-xl border transition-all ${style.card}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                    {/* Left: Severity, Device, Message */}
                    <div className="flex items-start gap-2.5 flex-1 min-w-0">
                      <div className="mt-0.5">{style.icon}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-1.5 mb-1">
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${style.badge}`}>
                            {alert.severity}
                          </span>
                          <span className="text-[10px] font-semibold text-slate-300 px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700">
                            {alert.deviceId}
                          </span>
                          <span className="text-[10px] font-medium text-slate-400 px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800">
                            {alert.alertType}
                          </span>
                          {alert.sensorParameter && (
                            <span className="text-[10px] font-mono text-cyan-300 px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/50">
                              {alert.sensorParameter}: {alert.sensorValue} (Limit: {alert.thresholdValue})
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-200 font-medium leading-relaxed">
                          {alert.message}
                        </p>
                        <div className="flex items-center gap-2 mt-1.5 text-[10px] text-slate-400">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{formatTimestamp(alert.createdAt)}</span>
                          <span className="text-slate-600">•</span>
                          <span>Source: {alert.source}</span>
                        </div>
                      </div>
                    </div>

                    {/* Right: Acknowledge Status & Action */}
                    <div className="shrink-0 flex items-center gap-2 self-end sm:self-center">
                      {alert.acknowledged ? (
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-[11px] font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          <span>
                            Ack by {alert.acknowledgedBy || 'Operator'}
                          </span>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleAcknowledge(alert.id)}
                          disabled={isAcking}
                          aria-label="Acknowledge alert"
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-600/80 text-xs font-semibold shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>{isAcking ? 'Acknowledging...' : 'Acknowledge'}</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default AlertWidget;
