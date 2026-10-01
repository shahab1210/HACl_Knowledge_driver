import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Cpu, Clock, Layers, ArrowRight, ShieldCheck } from 'lucide-react';
import {
  getDiagnosesByDeviceId,
  getLatestTelemetry,
  getTelemetryHistory,
  ApiError
} from '../services/api';
import { formatTimestamp, formatDurationSeconds } from '../utils/formatters';
import { ConfidenceBadge } from '../components/diagnosis/ConfidenceBadge';
import { TelemetryGrid } from '../components/telemetry/TelemetryGrid';
import { TelemetryTrendChart } from '../components/telemetry/TelemetryTrendChart';
import { DiagnosisHistoryTable } from '../components/diagnosis/DiagnosisHistoryTable';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { EmptyState } from '../components/common/EmptyState';
import { CardSkeleton } from '../components/common/LoadingSkeleton';

export function DeviceDetail() {
  const { deviceId } = useParams();
  const [diagnoses, setDiagnoses] = useState([]);
  const [liveTelemetry, setLiveTelemetry] = useState(null);
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTelemetry = useCallback(async () => {
    if (!deviceId) return;
    try {
      const [latest, hist] = await Promise.all([
        getLatestTelemetry(deviceId).catch(() => null),
        getTelemetryHistory(deviceId, 20).catch(() => []),
      ]);
      if (latest && latest.temperature !== undefined) {
        setLiveTelemetry(latest);
      }
      if (Array.isArray(hist) && hist.length > 0) {
        setTelemetryHistory(hist);
      }
    } catch {
      // Graceful fallback
    }
  }, [deviceId]);

  const loadDiagnoses = useCallback(async (isBackground = false) => {
    if (!deviceId) return;
    if (!isBackground) setIsLoading(true);
    setError(null);
    try {
      const data = await getDiagnosesByDeviceId(deviceId);
      setDiagnoses(Array.isArray(data) ? data : [data]);
    } catch (err) {
      if (err instanceof ApiError && err.isNotFound) {
        setDiagnoses([]);
      } else {
        setError(err.message || 'Failed to load device diagnoses');
      }
    } finally {
      if (!isBackground) setIsLoading(false);
    }
  }, [deviceId]);

  useEffect(() => {
    loadDiagnoses();
    fetchTelemetry();
  }, [loadDiagnoses, fetchTelemetry]);

  // Polling every 10 seconds for device telemetry
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTelemetry();
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchTelemetry]);

  const latest = diagnoses[0] || null;

  return (
    <div className="space-y-6">
      {/* Back Navigation */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
        <span className="text-xs font-mono text-cyan-400 font-bold bg-cyan-950/60 border border-cyan-800/50 px-2.5 py-0.5 rounded">
          Device: {deviceId}
        </span>
      </div>

      {error && (
        <ErrorAlert
          title="Device Diagnosis History Error"
          message={error}
        />
      )}

      {isLoading && (
        <div className="space-y-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {!isLoading && diagnoses.length === 0 && !liveTelemetry && !error && (
        <EmptyState
          title={`No Diagnoses for Device ${deviceId}`}
          message="There are no historical diagnosis records for this IoT device in the PostgreSQL database."
        />
      )}

      {!isLoading && (diagnoses.length > 0 || liveTelemetry) && (
        <div className="space-y-6">
          {/* Latest Telemetry for Device */}
          {(latest || liveTelemetry) && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                Latest Telemetry Snapshot for {deviceId}
              </h3>
              <TelemetryGrid
                telemetry={liveTelemetry || latest?.telemetry}
                isLoading={false}
                isLive={!!liveTelemetry}
              />
            </div>
          )}

          {/* Telemetry Progression Trend Chart */}
          <TelemetryTrendChart
            history={diagnoses}
            liveHistory={telemetryHistory}
          />

          {/* Diagnosis History Table */}
          {diagnoses.length > 0 && (
            <DiagnosisHistoryTable
              history={diagnoses}
              title={`Diagnosis History for Device ${deviceId}`}
            />
          )}
        </div>
      )}
    </div>
  );
}

