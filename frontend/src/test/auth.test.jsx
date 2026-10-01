import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { Header } from '../components/layout/Header';
import * as api from '../services/api';

// Helper component for testing ProtectedRoute and AuthContext
function TestProtectedContent() {
  const { user, logout } = useAuth();
  return (
    <div>
      <h1>Protected Dashboard</h1>
      <p>Logged in as: {user?.username}</p>
      <button onClick={logout}>Sign Out Button</button>
    </div>
  );
}

describe('Frontend Authentication Suite (P19)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  describe('Login Page', () => {
    it('renders login form elements correctly', () => {
      render(
        <MemoryRouter>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /IoT Fault Diagnosis/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/Username or Email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
      expect(screen.getByText(/Create Account/i)).toBeInTheDocument();
    });

    it('submits credentials and navigates on successful login', async () => {
      const user = userEvent.setup();
      const mockAuthResponse = {
        token: 'mock-jwt-token-123',
        tokenType: 'Bearer',
        username: 'operator_dan',
        email: 'dan@iot.com',
        role: 'USER',
        expiresInSeconds: 86400,
      };

      vi.spyOn(api, 'login').mockResolvedValueOnce(mockAuthResponse);

      render(
        <MemoryRouter initialEntries={['/login']}>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<div>Dashboard Home</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      await user.type(screen.getByLabelText(/Username or Email/i), 'operator_dan');
      await user.type(screen.getByLabelText(/Password/i), 'secret123');
      await user.click(screen.getByRole('button', { name: /Sign In/i }));

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith({
          usernameOrEmail: 'operator_dan',
          password: 'secret123',
        });
        expect(screen.getByText('Dashboard Home')).toBeInTheDocument();
      });
    });

    it('displays error message on invalid credentials', async () => {
      const user = userEvent.setup();
      vi.spyOn(api, 'login').mockRejectedValueOnce(
        new api.ApiError('Invalid username or password', 401)
      );

      render(
        <MemoryRouter>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </MemoryRouter>
      );

      await user.type(screen.getByLabelText(/Username or Email/i), 'wronguser');
      await user.type(screen.getByLabelText(/Password/i), 'badpass');
      await user.click(screen.getByRole('button', { name: /Sign In/i }));

      await waitFor(() => {
        expect(screen.getByText(/Invalid username or password/i)).toBeInTheDocument();
      });
    });
  });

  describe('Register Page', () => {
    it('renders register form elements correctly', () => {
      render(
        <MemoryRouter>
          <AuthProvider>
            <Register />
          </AuthProvider>
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /Create Account/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Account Role/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
    });

    it('validates password length before submitting', async () => {
      const user = userEvent.setup();
      const registerSpy = vi.spyOn(api, 'register');

      render(
        <MemoryRouter>
          <AuthProvider>
            <Register />
          </AuthProvider>
        </MemoryRouter>
      );

      await user.type(screen.getByLabelText(/Username/i), 'alex');
      await user.type(screen.getByLabelText(/Email Address/i), 'alex@iot.com');
      await user.type(screen.getByLabelText(/Password/i), '123'); // < 6 chars
      await user.click(screen.getByRole('button', { name: /Create Account/i }));

      expect(screen.getByText(/Password must be at least 6 characters long/i)).toBeInTheDocument();
      expect(registerSpy).not.toHaveBeenCalled();
    });

    it('successfully registers and logs user in', async () => {
      const user = userEvent.setup();
      const mockAuthResponse = {
        token: 'registered-jwt-token',
        tokenType: 'Bearer',
        username: 'new_operator',
        email: 'new@iot.com',
        role: 'ADMIN',
        expiresInSeconds: 86400,
      };

      vi.spyOn(api, 'register').mockResolvedValueOnce(mockAuthResponse);

      render(
        <MemoryRouter initialEntries={['/register']}>
          <AuthProvider>
            <Routes>
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<div>Welcome Admin Dashboard</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      await user.type(screen.getByLabelText(/Username/i), 'new_operator');
      await user.type(screen.getByLabelText(/Email Address/i), 'new@iot.com');
      await user.type(screen.getByLabelText(/Password/i), 'strongpassword');
      await user.selectOptions(screen.getByLabelText(/Account Role/i), 'ADMIN');
      await user.click(screen.getByRole('button', { name: /Create Account/i }));

      await waitFor(() => {
        expect(api.register).toHaveBeenCalledWith({
          username: 'new_operator',
          email: 'new@iot.com',
          password: 'strongpassword',
          role: 'ADMIN',
        });
        expect(screen.getByText('Welcome Admin Dashboard')).toBeInTheDocument();
      });
    });

    it('displays error on duplicate username/email conflict', async () => {
      const user = userEvent.setup();
      vi.spyOn(api, 'register').mockRejectedValueOnce(
        new api.ApiError("Username 'duplicate' is already registered", 409)
      );

      render(
        <MemoryRouter>
          <AuthProvider>
            <Register />
          </AuthProvider>
        </MemoryRouter>
      );

      await user.type(screen.getByLabelText(/Username/i), 'duplicate');
      await user.type(screen.getByLabelText(/Email Address/i), 'dup@iot.com');
      await user.type(screen.getByLabelText(/Password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /Create Account/i }));

      await waitFor(() => {
        expect(screen.getByText(/already registered/i)).toBeInTheDocument();
      });
    });
  });

  describe('ProtectedRoute Component', () => {
    it('redirects unauthenticated user to /login', async () => {
      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <TestProtectedContent />
                  </ProtectedRoute>
                }
              />
              <Route path="/login" element={<div>Login Page Target</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Login Page Target')).toBeInTheDocument();
      });
    });

    it('renders protected content when authenticated with valid token', async () => {
      localStorage.setItem('iot_auth_token', 'valid-saved-token');
      vi.spyOn(api, 'getCurrentUser').mockResolvedValueOnce({
        id: 1,
        username: 'active_engineer',
        email: 'eng@iot.com',
        role: 'USER',
      });

      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <TestProtectedContent />
                  </ProtectedRoute>
                }
              />
              <Route path="/login" element={<div>Login Page Target</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Protected Dashboard')).toBeInTheDocument();
        expect(screen.getByText(/Logged in as: active_engineer/i)).toBeInTheDocument();
      });
    });
  });

  describe('Header Component User State', () => {
    it('displays user profile and sign out action when logged in', async () => {
      localStorage.setItem('iot_auth_token', 'valid-header-token');
      vi.spyOn(api, 'getCurrentUser').mockResolvedValueOnce({
        id: 2,
        username: 'lead_operator',
        email: 'lead@iot.com',
        role: 'ADMIN',
      });

      render(
        <MemoryRouter>
          <AuthProvider>
            <Header backendOnline={true} />
          </AuthProvider>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('lead_operator')).toBeInTheDocument();
        expect(screen.getByText('ADMIN')).toBeInTheDocument();
        expect(screen.getByTitle('Sign Out')).toBeInTheDocument();
      });
    });
  });
});
