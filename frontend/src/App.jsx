import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { DiagnosisDetail } from './pages/DiagnosisDetail';
import { DeviceDetail } from './pages/DeviceDetail';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function ProtectedApp() {
  const [isManualOpen, setIsManualOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <Layout
      isRefreshing={isRefreshing}
      onRefresh={handleRefresh}
      onOpenManualDiagnosis={() => setIsManualOpen(true)}
      backendOnline={backendOnline}
    >
      <Routes>
        <Route
          path="/"
          element={
            <Dashboard
              isManualOpen={isManualOpen}
              onCloseManual={() => setIsManualOpen(false)}
              onOpenManual={() => setIsManualOpen(true)}
              onStatusChange={setBackendOnline}
            />
          }
        />
        <Route path="/diagnosis/:id" element={<DiagnosisDetail />} />
        <Route path="/device/:deviceId" element={<DeviceDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <ProtectedApp />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
