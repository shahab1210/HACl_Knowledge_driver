import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, Plus, RefreshCw, User, LogOut, Shield } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';
import { useAuth } from '../../context/AuthContext';

export function Header({ isRefreshing, onRefresh, onOpenManualDiagnosis, backendOnline = true }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-base tracking-tight text-white">IoT Fault Diagnosis</span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">P_311</span>
                </div>
                <p className="text-[11px] text-slate-400 font-medium">Knowledge-Driven AI Assistant</p>
              </div>
            </Link>

            {/* Navigation links */}
            {isAuthenticated && (
              <nav className="hidden md:flex items-center gap-1 pl-4 border-l border-slate-800">
                <Link
                  to="/"
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    location.pathname === '/'
                      ? 'bg-slate-800/90 text-cyan-400 border border-slate-700/60'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/device/ESP32_001"
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    location.pathname.startsWith('/device')
                      ? 'bg-slate-800/90 text-cyan-400 border border-slate-700/60'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  Device ESP32_001
                </Link>
              </nav>
            )}
          </div>

          {/* Right Action Bar */}
          <div className="flex items-center gap-3">
            {/* Backend Status */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
              <span className="text-xs text-slate-400">Backend API:</span>
              <StatusBadge status={backendOnline ? 'ONLINE' : 'OFFLINE'} />
            </div>

            {/* Refresh Button */}
            {isAuthenticated && onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isRefreshing}
                title="Refresh latest diagnosis"
                className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
              </button>
            )}

            {/* Manual Run Button */}
            {isAuthenticated && onOpenManualDiagnosis && (
              <button
                onClick={onOpenManualDiagnosis}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-md shadow-cyan-900/40 border border-cyan-400/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <Plus className="w-4 h-4" />
                <span>Run Diagnosis</span>
              </button>
            )}

            {/* User Profile & Logout */}
            {isAuthenticated && user && (
              <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="w-6 h-6 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400 text-xs font-bold">
                    {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div className="hidden md:flex flex-col">
                    <span className="text-xs font-bold text-slate-200 leading-none">{user.username}</span>
                    <span className="text-[9px] uppercase tracking-wider font-semibold text-cyan-400 leading-none mt-0.5">
                      {user.role}
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  title="Sign Out"
                  className="p-2 rounded-xl bg-slate-900 hover:bg-red-950/60 text-slate-400 hover:text-red-300 border border-slate-800 hover:border-red-800/60 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
