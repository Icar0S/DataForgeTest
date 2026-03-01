/**
 * Tests for RAGButton component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import RAGButton from '../../../frontend/src/components/RAGButton';

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

jest.mock('react-feather', () => ({
  Book: () => <svg data-testid="book-icon" />,
}));

const renderWithRouter = () =>
  render(<BrowserRouter><RAGButton /></BrowserRouter>);

describe('RAGButton Component', () => {
  test('renders without crashing', () => {
    expect(() => renderWithRouter()).not.toThrow();
  });

  test('renders Support RAG text', () => {
    renderWithRouter();
    expect(screen.getByText('Support RAG')).toBeInTheDocument();
  });

  test('renders link to /support-rag', () => {
    renderWithRouter();
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/support-rag');
  });

  test('renders Book icon', () => {
    renderWithRouter();
    expect(screen.getByTestId('book-icon')).toBeInTheDocument();
  });

  test('has gradient styling', () => {
    renderWithRouter();
    const link = screen.getByRole('link');
    expect(link).toHaveClass('bg-gradient-to-r');
  });
});
