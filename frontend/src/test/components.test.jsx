import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { TelemetryCard } from '../components/telemetry/TelemetryCard';
import { TelemetryGrid } from '../components/telemetry/TelemetryGrid';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfidenceBadge } from '../components/diagnosis/ConfidenceBadge';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { EmptyState } from '../components/common/EmptyState';
import { KnowledgeSourcesTable } from '../components/diagnosis/KnowledgeSourcesTable';
import { KpiSummaryGrid } from '../components/diagnosis/KpiSummaryGrid';
import { TelemetryTrendChart } from '../components/telemetry/TelemetryTrendChart';
import { DiagnosisHistoryTable } from '../components/diagnosis/DiagnosisHistoryTable';
import { PrimaryFaultCard } from '../components/diagnosis/PrimaryFaultCard';
import { AlternativeFaultsList } from '../components/diagnosis/AlternativeFaultsList';
import { EvidenceSection } from '../components/diagnosis/EvidenceSection';
import { RecommendedChecksList } from '../components/diagnosis/RecommendedChecksList';
import { PossibleCausesList } from '../components/diagnosis/PossibleCausesList';
import { GenerationDetailsCard } from '../components/diagnosis/GenerationDetailsCard';

describe('Frontend Component Suite', () => {
  it('renders TelemetryCard with value and critical alert for high temp', () => {
    render(<TelemetryCard type="temperature" label="Temperature" value={92.5} unit="°C" />);
    expect(screen.getByText('Temperature')).toBeInTheDocument();
    expect(screen.getByText('92.5')).toBeInTheDocument();
    expect(screen.getByText('°C')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
  });

  it('renders TelemetryCard N/A for null value', () => {
    render(<TelemetryCard type="pressure" label="Pressure" value={null} unit="bar" />);
    expect(screen.getByText('Pressure')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  it('renders StatusBadge correctly', () => {
    render(<StatusBadge status="ONLINE" />);
    expect(screen.getByText('ONLINE')).toBeInTheDocument();
  });

  it('renders ConfidenceBadge with level and reason', () => {
    render(<ConfidenceBadge level="HIGH" reason="Knowledge base match" />);
    expect(screen.getByText(/HIGH CONFIDENCE/i)).toBeInTheDocument();
    expect(screen.getByText('Knowledge base match')).toBeInTheDocument();
  });

  it('renders ErrorAlert with title and message', () => {
    render(<ErrorAlert title="Backend Offline" message="Could not connect to port 8080" />);
    expect(screen.getByText('Backend Offline')).toBeInTheDocument();
    expect(screen.getByText('Could not connect to port 8080')).toBeInTheDocument();
  });

  it('renders EmptyState correctly', () => {
    render(<EmptyState title="No Diagnoses" message="Database is empty" />);
    expect(screen.getByText('No Diagnoses')).toBeInTheDocument();
    expect(screen.getByText('Database is empty')).toBeInTheDocument();
  });

  it('renders KnowledgeSourcesTable with ranked RAG documents and cosine bar', () => {
    const mockSources = [
      { rank: 1, documentId: 'DOC-01', title: 'Bearing Guide', source: 'kb/bearing.md', similarity: 0.85 }
    ];
    render(<KnowledgeSourcesTable knowledgeSources={mockSources} />);
    expect(screen.getByText(/RAG Grounding Knowledge Sources/i)).toBeInTheDocument();
    expect(screen.getByText('Bearing Guide')).toBeInTheDocument();
    expect(screen.getByText('0.8500')).toBeInTheDocument();
  });


  it('renders KpiSummaryGrid with 6 operational metrics', () => {
    const mockDiagnosis = {
      id: 'diag-1',
      deviceId: 'ESP32_001',
      latencySeconds: 3.12,
      diagnosis: {
        primaryFault: { faultId: 'FAULT-001', title: 'Bearing Degradation' },
        confidence: { level: 'HIGH' }
      }
    };

    render(
      <BrowserRouter>
        <KpiSummaryGrid diagnosis={mockDiagnosis} historyCount={5} backendOnline={true} />
      </BrowserRouter>
    );

    expect(screen.getByText('System API')).toBeInTheDocument();
    expect(screen.getByText('ONLINE (8080)')).toBeInTheDocument();
    expect(screen.getByText('ESP32_001')).toBeInTheDocument();
    expect(screen.getByText('FAULT-001')).toBeInTheDocument();
    expect(screen.getByText('5 Records')).toBeInTheDocument();
    expect(screen.getByText(/3.12s/i)).toBeInTheDocument();
  });

  it('renders TelemetryTrendChart with multi-series data points', () => {
    const mockHistory = [
      {
        id: 'diag-1',
        timestamp: '2026-10-01T01:00:00',
        telemetry: { temperature: 88.0, vibration: 12.0, current: 24.0 }
      },
      {
        id: 'diag-2',
        timestamp: '2026-10-01T02:00:00',
        telemetry: { temperature: 94.0, vibration: 15.5, current: 29.0 }
      }
    ];

    render(<TelemetryTrendChart history={mockHistory} />);
    expect(screen.getByText(/Telemetry Progression Trends/i)).toBeInTheDocument();
    expect(screen.getByText(/Extracted from 2 real diagnosis records in PostgreSQL/i)).toBeInTheDocument();
    expect(screen.getByText('88.0°C')).toBeInTheDocument();
    expect(screen.getByText('94.0°C')).toBeInTheDocument();
  });

  it('renders DiagnosisHistoryTable with links and telemetry snapshots', () => {
    const mockHistory = [
      {
        id: 'diag-TEST-123',
        timestamp: '2026-10-01T02:00:00',
        latencySeconds: 2.4,
        telemetry: { temperature: 92.5, vibration: 14.8, current: 28.5 },
        diagnosis: {
          primaryFault: { faultId: 'FAULT-001', title: 'Bearing Wear' },
          confidence: { level: 'HIGH' }
        }
      }
    ];

    render(
      <BrowserRouter>
        <DiagnosisHistoryTable history={mockHistory} title="Device History" />
      </BrowserRouter>
    );

    expect(screen.getByText(/Device History \(1\)/i)).toBeInTheDocument();
    expect(screen.getByText('diag-TEST-123')).toBeInTheDocument();
    expect(screen.getByText('Bearing Wear')).toBeInTheDocument();
    expect(screen.getByText(/T: 92.5 °C/i)).toBeInTheDocument();
  });

  it('renders PrimaryFaultCard, EvidenceSection, RecommendedChecksList, and GenerationDetailsCard', () => {
    const mockPrimary = {
      faultId: 'FAULT-001',
      title: 'Motor Overheat',
      explanation: 'Temperature is critically elevated beyond safe envelope.'
    };

    const mockEvidence = [
      { type: 'telemetry', parameter: 'temperature', value: 95.0, unit: '°C' }
    ];

    const mockChecks = ['Check cooling fans', 'Inspect bearing lubrication'];
    const mockCauses = ['Airflow blockage', 'High ambient temperature'];

    const mockGen = {
      provider: 'ollama',
      model: 'qwen2.5:1.5b',
      latencySeconds: 2.8,
      temperature: 0.1
    };

    render(
      <div>
        <PrimaryFaultCard primaryFault={mockPrimary} />
        <EvidenceSection evidence={mockEvidence} />
        <RecommendedChecksList recommendedChecks={mockChecks} />
        <PossibleCausesList possibleCauses={mockCauses} />
        <GenerationDetailsCard generationDetails={mockGen} model="qwen2.5:1.5b" />
      </div>
    );

    expect(screen.getByText('Motor Overheat')).toBeInTheDocument();
    expect(screen.getByText('Temperature is critically elevated beyond safe envelope.')).toBeInTheDocument();
    expect(screen.getByText('Check cooling fans')).toBeInTheDocument();
    expect(screen.getByText('Airflow blockage')).toBeInTheDocument();
    expect(screen.getByText('qwen2.5:1.5b')).toBeInTheDocument();
  });

  it('renders TelemetryGrid with LIVE STREAM badge and updated timestamp when isLive is true', () => {
    const mockTelemetry = {
      deviceId: 'ESP32_001',
      temperature: 31.4,
      vibration: 1.8,
      current: 5.6,
      pressure: 2.7,
      recordedAt: '2026-10-01T12:00:00Z'
    };

    render(<TelemetryGrid telemetry={mockTelemetry} isLoading={false} isLive={true} />);
    expect(screen.getByText('LIVE STREAM')).toBeInTheDocument();
    expect(screen.getByText('Live IoT Telemetry')).toBeInTheDocument();
    expect(screen.getByText('31.4')).toBeInTheDocument();
    expect(screen.getByText('Device: ESP32_001')).toBeInTheDocument();
  });

  it('renders TelemetryGrid with DIAGNOSIS SNAPSHOT badge when isLive is false', () => {
    const mockTelemetry = {
      deviceId: 'ESP32_001',
      temperature: 88.5,
      vibration: 12.0,
      current: 24.0,
      pressure: 2.0
    };

    render(<TelemetryGrid telemetry={mockTelemetry} isLoading={false} isLive={false} />);
    expect(screen.getByText('DIAGNOSIS SNAPSHOT')).toBeInTheDocument();
    expect(screen.getByText('88.5')).toBeInTheDocument();
  });

  it('renders TelemetryTrendChart with liveHistory from sensor_readings', () => {
    const mockLiveHistory = [
      { id: 1, temperature: 28.0, vibration: 1.5, current: 4.8, recordedAt: '2026-10-01T11:58:00' },
      { id: 2, temperature: 31.4, vibration: 1.8, current: 5.6, recordedAt: '2026-10-01T12:00:00' }
    ];

    render(<TelemetryTrendChart history={[]} liveHistory={mockLiveHistory} />);
    expect(screen.getByText(/Telemetry Progression Trends/i)).toBeInTheDocument();
    expect(screen.getByText(/Extracted from 2 real sensor readings in PostgreSQL \(sensor_readings\)/i)).toBeInTheDocument();
    expect(screen.getByText('28.0°C')).toBeInTheDocument();
    expect(screen.getByText('31.4°C')).toBeInTheDocument();
  });
});

