import React, { useState } from 'react';
import { X, Play, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';
import { triggerDiagnosis } from '../../services/api';

export function ManualDiagnosisModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    deviceId: 'ESP32_001',
    temperature: '92.5',
    vibration: '14.8',
    current: '28.5',
    humidity: '45.0',
    pressure: '2.1',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const payload = {
        deviceId: formData.deviceId.trim(),
        temperature: formData.temperature ? parseFloat(formData.temperature) : null,
        vibration: formData.vibration ? parseFloat(formData.vibration) : null,
        current: formData.current ? parseFloat(formData.current) : null,
        humidity: formData.humidity ? parseFloat(formData.humidity) : null,
        pressure: formData.pressure ? parseFloat(formData.pressure) : null,
      };

      const result = await triggerDiagnosis(payload);
      setIsLoading(false);
      onSuccess?.(result);
      onClose();
    } catch (err) {
      setIsLoading(false);
      setError(err.message || 'Failed to trigger diagnosis.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden relative animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-950/60">
          <div>
            <h3 className="text-base font-bold text-white">Trigger On-Demand AI Diagnosis</h3>
            <p className="text-xs text-slate-400 mt-0.5">Submit IoT telemetry parameters to local Ollama AI</p>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-950/50 border border-rose-800/80 text-rose-200 text-xs flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Device Identifier *
            </label>
            <input
              type="text"
              name="deviceId"
              required
              value={formData.deviceId}
              onChange={handleChange}
              disabled={isLoading}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              placeholder="e.g. ESP32_001"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Temperature (°C)
              </label>
              <input
                type="number"
                step="0.1"
                name="temperature"
                value={formData.temperature}
                onChange={handleChange}
                disabled={isLoading}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
                placeholder="e.g. 92.5"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Vibration (mm/s)
              </label>
              <input
                type="number"
                step="0.1"
                name="vibration"
                value={formData.vibration}
                onChange={handleChange}
                disabled={isLoading}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
                placeholder="e.g. 14.8"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Current (A)
              </label>
              <input
                type="number"
                step="0.1"
                name="current"
                value={formData.current}
                onChange={handleChange}
                disabled={isLoading}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
                placeholder="e.g. 28.5"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Pressure (bar)
              </label>
              <input
                type="number"
                step="0.1"
                name="pressure"
                value={formData.pressure}
                onChange={handleChange}
                disabled={isLoading}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:outline-none focus:border-cyan-500"
                placeholder="e.g. 2.1"
              />
            </div>
          </div>

          {isLoading && (
            <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/40 flex items-center gap-3 animate-pulse">
              <Loader2 className="w-5 h-5 text-cyan-400 animate-spin shrink-0" />
              <div className="text-xs text-cyan-200">
                <span className="font-bold block">Running AI Diagnosis Engine...</span>
                <span>Retrieving RAG knowledge chunks and generating Ollama LLM diagnosis (~30-45s).</span>
              </div>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-950/60 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute Diagnosis</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
