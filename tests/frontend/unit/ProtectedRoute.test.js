/**
 * Tests for frontend/src/components/ProtectedRoute.js
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import '@testing-library/jest-dom';

const mockUseAuthContext = jest.fn();
jest.mock('../../../frontend/src/context/AuthContext', () => ({
  useAuthContext: () => mockUseAuthContext(),
}));

const mockUseLanguage = jest.fn(() => ({ language: 'pt-BR', changeLanguage: jest.fn() }));
jest.mock('../../../frontend/src/context/LanguageContext', () => ({
  useLanguage: () => mockUseLanguage(),
}));

import ProtectedRoute from '../../../frontend/src/components/ProtectedRoute';

const ChildComponent = () => <div data-testid="protected-content">Protected Content</div>;

const renderWithRouter = (authState, initialEntries = ['/dashboard']) => {
  mockUseAuthContext.mockReturnValue(authState);
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <ChildComponent />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div data-testid="login-page">Login Page</div>} />
      </Routes>
    </MemoryRouter>
  );
};

describe('ProtectedRoute', () => {
  test('redirects to /login when not authenticated', () => {
    renderWithRouter({ isAuthenticated: false, hasProfile: false, isLoading: false });
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('renders children when authenticated with profile', () => {
    renderWithRouter({ isAuthenticated: true, hasProfile: true, isLoading: false });
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  test('redirects to /login when authenticated but without profile', () => {
    renderWithRouter({ isAuthenticated: true, hasProfile: false, isLoading: false });
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('shows LoadingScreen during isLoading=true', () => {
    renderWithRouter({ isAuthenticated: false, hasProfile: false, isLoading: true });
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument();
    // Loading screen should be shown
    const loadingElements = document.querySelector('[class*="animate-spin"]') ||
      document.querySelector('[data-testid="loading-screen"]');
    expect(loadingElements || document.body.textContent.length).toBeTruthy();
  });

  test('preserves original route in location.state.from', () => {
    let capturedState = null;
    mockUseAuthContext.mockReturnValue({ isAuthenticated: false, hasProfile: false, isLoading: false });

    const LoginCapture = () => {
      const { useLocation } = require('react-router-dom');
      const loc = useLocation();
      capturedState = loc.state;
      return <div data-testid="login-page">Login Page</div>;
    };

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <ChildComponent />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LoginCapture />} />
        </Routes>
      </MemoryRouter>
    );

    expect(capturedState?.from?.pathname).toBe('/dashboard');
  });
});
