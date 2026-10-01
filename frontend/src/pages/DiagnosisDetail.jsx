import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Database, Clock, Cpu, HardDrive } from 'lucide-react';
import { getDiagnosisById, ApiError } from '../services/api';
import { formatTimestamp, formatDurationSeconds } from '../utils/formatters';
import { ConfidenceBadge } from '../components/diagnosis/ConfidenceBadge';
import { TelemetryGrid } from '../components/telemetry/TelemetryGrid';
import { PrimaryFaultCard } from '../components/diagnosis/PrimaryFaultCard';
import { AlternativeFaultsList } from '../components/diagnosis/AlternativeFaultsList';
import { EvidenceSection } from '../components/diagnosis/EvidenceSection';
import { KnowledgeSourcesTable } from '../components/diagnosis/KnowledgeSourcesTable';
import { RecommendedChecksList } from '../components/diagnosis/RecommendedChecksList';
import { PossibleCausesList } from '../components/diagnosis/PossibleCausesList';
import { GenerationDetailsCard } from '../components/diagnosis/GenerationDetailsCard';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { LoadingSkeleton, CardSkeleton } from '../components/common/LoadingSkeleton';

export function DiagnosisDetail() {
  const { id } = useParams();
  const [diagnosis, setDiagnosis] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      if (!id) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await getDiagnosisById(id);
        setDiagnosis(data);
      } catch (err) {
        setError(err.message || 'Failed to load diagnosis record');
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [id]);

  const detail = diagnosis?.diagnosis || {};
  const primaryFault = detail.primaryFault || {};
  const confidence = detail.confidence || {};

  return (
    <div className="space-y-6">
      {/* Back Navigation Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
        <span className="text-xs font-mono text-slate-500">Record ID: {id}</span>
      </div>

      {error && (
        <ErrorAlert
          title="Diagnosis Record Error"
          message={error}
        />
      )}

      {isLoading && (
        <div className="space-y-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {!isLoading && diagnosis && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs uppercase font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2 py-0.5 rounded">
                    Persisted Diagnosis
                  </span>
                  <span className="text-xs font-mono text-slate-400">{diagnosis.id}</span>
                </div>
                <h1 className="text-2xl font-black text-white mt-2">
                  {primaryFault.title || 'Diagnostic Assessment'}
                </h1>
                {primaryFault.faultId && (
                  <span className="text-xs font-mono text-cyan-400 font-semibold block mt-1">
                    Fault Code: {primaryFault.faultId}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-3">
                <ConfidenceBadge level={confidence.level} reason={confidence.reason} />
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3 pt-5 border-t border-slate-800">
              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/60 text-xs">
                <span className="text-slate-400 block font-semibold">Device</span>
                <Link
                  to={`/device/${encodeURIComponent(diagnosis.deviceId)}`}
                  className="font-bold text-cyan-400 font-mono mt-0.5 block hover:underline"
                >
                  {diagnosis.deviceId}
                </Link>
              </div>

              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/60 text-xs">
                <span className="text-slate-400 block font-semibold">Recorded Timestamp</span>
                <span className="font-semibold text-slate-200 mt-0.5 block">
                  {formatTimestamp(diagnosis.timestamp)}
                </span>
              </div>

              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/60 text-xs font-mono">
                <span className="text-slate-400 block font-sans font-semibold">Inference Latency</span>
                <span className="font-semibold text-emerald-400 mt-0.5 block">
                  {formatDurationSeconds(diagnosis.latencySeconds)}
                </span>
              </div>
            </div>
          </div>

          {/* Telemetry Grid */}
          <TelemetryGrid telemetry={diagnosis.telemetry} isLoading={false} />

          {/* Diagnostic Explanation */}
          <PrimaryFaultCard
            primaryFault={detail.primaryFault}
            query={detail.query}
            rawLlmResponse={detail.rawLlmResponse}
          />

          {/* Child Relations & RAG Evidence */}
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
        </div>
      )}
    </div>
  );
}
