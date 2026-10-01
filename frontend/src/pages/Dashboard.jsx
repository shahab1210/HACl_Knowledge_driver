import React, { useState, useEffect, useCallback } from 'react';
import {
  getLatestDiagnosis,
  getDiagnosesByDeviceId,
  getAlerts,
  acknowledgeAlert,
  getLatestTelemetry,
  getTelemetryHistory,
  ApiError
} from '../services/api';
import { KpiSummaryGrid } from '../components/diagnosis/KpiSummaryGrid';
import { AlertWidget } from '../components/alerts/AlertWidget';
import { TelemetryGrid } from '../components/telemetry/TelemetryGrid';
import { TelemetryTrendChart } from '../components/telemetry/TelemetryTrendChart';
import { LatestDiagnosisCard } from '../components/diagnosis/LatestDiagnosisCard';
import { PrimaryFaultCard } from '../components/diagnosis/PrimaryFaultCard';
import { AlternativeFaultsList } from '../components/diagnosis/AlternativeFaultsList';
import { EvidenceSection } from '../components/diagnosis/EvidenceSection';
import { KnowledgeSourcesTable } from '../components/diagnosis/KnowledgeSourcesTable';
import { RecommendedChecksList } from '../components/diagnosis/RecommendedChecksList';
import { PossibleCausesList } from '../components/diagnosis/PossibleCausesList';
import { GenerationDetailsCard } from '../components/diagnosis/GenerationDetailsCard';
import { DiagnosisHistoryTable } from '../components/diagnosis/DiagnosisHistoryTable';
import { ManualDiagnosisModal } from '../components/diagnosis/ManualDiagnosisModal';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingSkeleton, CardSkeleton } from '../components/common/LoadingSkeleton';

export function Dashboard({ isManualOpen, onCloseManual, onOpenManual, onStatusChange }) {
  const [diagnosis, setDiagnosis] = useState(null);
  const [history, setHistory] = useState([]);
  const [liveTelemetry, setLiveTelemetry] = useState(null);
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchAlerts = useCallback(async () => {
    setAlertsLoading(true);
    try {
      const data = await getAlerts();
      setAlerts(Array.isArray(data) ? data : []);
    } catch {
      // Keep existing alerts on transient error
    } finally {
      setAlertsLoading(false);
    }
  }, []);

  const fetchTelemetry = useCallback(async (devId = null) => {
    try {
      const [latest, hist] = await Promise.all([
        getLatestTelemetry(devId).catch(() => null),
        getTelemetryHistory(devId, 20).catch(() => []),
      ]);
      if (latest && latest.temperature !== undefined) {
        setLiveTelemetry(latest);
      }
      if (Array.isArray(hist) && hist.length > 0) {
        setTelemetryHistory(hist);
      }
    } catch {
      // Graceful fallback to diagnosis telemetry
    }
  }, []);

  const handleAcknowledge = async (id) => {
    try {
      const updated = await acknowledgeAlert(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const fetchData = useCallback(async (isBackground = false) => {
    if (!isBackground) setIsLoading(true);
    setError(null);

    // Fetch alerts and live telemetry in parallel
    fetchAlerts();
    fetchTelemetry(null);

    try {
      const latestData = await getLatestDiagnosis();
      setDiagnosis(latestData);
      onStatusChange?.(true);

      if (latestData?.deviceId) {
        // Also query device-specific telemetry
        fetchTelemetry(latestData.deviceId);
        try {
          const historyData = await getDiagnosesByDeviceId(latestData.deviceId);
          setHistory(Array.isArray(historyData) ? historyData : [historyData]);
        } catch {
          // If history fetch fails or is empty, use the latest record as single point
          setHistory([latestData]);
        }
      } else {
        setHistory([]);
      }
      setError(null);
    } catch (err) {
      if (err instanceof ApiError && err.isNotFound) {
        // Empty database (404) - normal state before any diagnosis is run
        setDiagnosis(null);
        setHistory([]);
        setError(null);
        onStatusChange?.(true);
      } else {
        setError(err.message || 'Failed to fetch latest diagnosis');
        onStatusChange?.(false);
      }
    } finally {
      if (!isBackground) setIsLoading(false);
    }
  }, [onStatusChange, fetchAlerts]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Polling interval (every 10 seconds if auto-refresh is active)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchData(true);
    }, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchData]);

  const handleManualSuccess = (newDiagnosis) => {
    setDiagnosis(newDiagnosis);
    if (newDiagnosis?.deviceId) {
      fetchTelemetry(newDiagnosis.deviceId);
      getDiagnosesByDeviceId(newDiagnosis.deviceId)
        .then((hist) => setHistory(Array.isArray(hist) ? hist : [hist]))
        .catch(() => setHistory([newDiagnosis]));
    }
    setError(null);
  };

  const detail = diagnosis?.diagnosis || {};

  return (
    <div className="space-y-8">
      {/* Top Banner / System Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Industrial Fault Diagnosis Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time IoT telemetry analysis and knowledge-grounded AI fault isolation
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-400 select-none bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-cyan-500 focus:ring-0 focus:ring-offset-0"
            />
            <span>Auto-Poll (10s)</span>
          </label>
        </div>
      </div>

      {/* KPI Summary Grid */}
      <KpiSummaryGrid
        diagnosis={diagnosis}
        historyCount={history.length}
        backendOnline={!error}
      />

      {/* Industrial Alerts & Notifications (P20) */}
      <AlertWidget
        alerts={alerts}
        onAcknowledge={handleAcknowledge}
        isLoading={alertsLoading}
        onRefresh={fetchAlerts}
      />

      {/* Error state */}
      {error && (
        <ErrorAlert
          title="Spring Boot API Connection Error"
          message={error}
          onRetry={() => fetchData(false)}
        />
      )}

      {/* Loading state */}
      {isLoading && !diagnosis && (
        <div className="space-y-6">
          <CardSkeleton />
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !diagnosis && !error && (
        <EmptyState
          title="No Active Diagnosis Found"
          message="PostgreSQL database does not contain any persisted diagnoses yet. You can submit telemetry manually or stream data over MQTT to trigger AI diagnosis."
          onAction={onOpenManual}
          actionLabel="Execute Test Diagnosis"
        />
      )}

      {/* Active Diagnosis Dashboard View */}
      {diagnosis && (
        <div className="space-y-6">
          {/* 1. Latest Diagnosis Card */}
          <LatestDiagnosisCard diagnosis={diagnosis} />

          {/* 2. Telemetry Grid */}
          <TelemetryGrid
            telemetry={liveTelemetry || diagnosis.telemetry}
            isLoading={false}
            isLive={!!liveTelemetry}
          />

          {/* 3. Real Historical Telemetry Progression Chart */}
          <TelemetryTrendChart
            history={history.length > 0 ? history : [diagnosis]}
            liveHistory={telemetryHistory}
          />

          {/* 4. Primary Fault & Diagnostic Analysis */}
          <PrimaryFaultCard
            primaryFault={detail.primaryFault}
            query={detail.query}
            rawLlmResponse={detail.rawLlmResponse}
          />

          {/* 5. Evidence & Recommended Actions Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <EvidenceSection evidence={detail.evidence} />
              <AlternativeFaultsList alternativeFaults={detail.alternativeFaults} />
              <PossibleCausesList possibleCauses={detail.possibleCauses} />
            </div>

            <div className="space-y-6">
              <RecommendedChecksList
                recommendedChecks={detail.recommendedChecks}
                additionalInfo={detail.additionalInformationRequired}
              />
              <KnowledgeSourcesTable knowledgeSources={detail.knowledgeSources} />
              <GenerationDetailsCard
                generationDetails={detail.generationDetails}
                model={detail.model}
              />
            </div>
          </div>

          {/* 6. Historical Diagnosis Table */}
          <DiagnosisHistoryTable
            history={history}
            title={`Persisted Diagnosis History for ${diagnosis.deviceId || 'System'}`}
          />
        </div>
      )}

      {/* Manual Diagnosis Modal */}
      <ManualDiagnosisModal
        isOpen={isManualOpen}
        onClose={onCloseManual}
        onSuccess={handleManualSuccess}
      />
    </div>
  );
}

