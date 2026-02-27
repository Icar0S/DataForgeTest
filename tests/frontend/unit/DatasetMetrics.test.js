/**
 * Tests for DatasetMetrics component
 * Tests core rendering functionality and user interactions
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import DatasetMetrics from '../../../frontend/src/pages/DatasetMetrics';

// Mock fetch globally
global.fetch = jest.fn();

// Helper function to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('DatasetMetrics Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('Initial Render', () => {
    test('renders page title and description', () => {
      renderWithRouter(<DatasetMetrics />);
      
      expect(screen.getByText('Métricas de Qualidade de Dados')).toBeInTheDocument();
      expect(screen.getByText(/Analise a qualidade do seu dataset/)).toBeInTheDocument();
    });

    test('renders upload section', () => {
      renderWithRouter(<DatasetMetrics />);
      
      expect(screen.getByText('Upload do Dataset')).toBeInTheDocument();
      expect(screen.getByText(/Arraste seu dataset aqui/)).toBeInTheDocument();
      expect(screen.getByText(/Formatos suportados: CSV, XLSX, XLS, Parquet/)).toBeInTheDocument();
    });

    test('renders back to home link', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const backLink = screen.getByRole('link', { name: /Voltar para Home/i });
      expect(backLink).toBeInTheDocument();
      expect(backLink).toHaveAttribute('href', '/');
    });
  });

  describe('File Upload', () => {
    test('accepts file selection', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      
      fireEvent.change(input, { target: { files: [file] } });
      
      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });

    test('shows error for invalid file type', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      const input = screen.getByLabelText('Selecionar arquivo');
      
      fireEvent.change(input, { target: { files: [file] } });
      
      expect(screen.getByText(/Tipo de arquivo inválido/)).toBeInTheDocument();
    });

    test('shows analyze button after file selection', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      
      fireEvent.change(input, { target: { files: [file] } });
      
      expect(screen.getByText('Analisar Dataset')).toBeInTheDocument();
    });
  });

  describe('Analysis Process', () => {
    test('uploads and analyzes file successfully', async () => {
      // Mock successful upload
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          sessionId: 'test-session-id',
          columns: ['col1', 'col2'],
          sample: [{ col1: 1, col2: 'a' }],
          format: 'csv',
          rows: 100,
        }),
      });

      // Mock successful analysis
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          overall_quality_score: 95.5,
          metrics: {
            completeness: {
              overall_completeness: 100,
              total_cells: 200,
              filled_cells: 200,
              missing_cells: 0,
            },
            uniqueness: {
              overall_uniqueness: 95,
              total_rows: 100,
              unique_rows: 95,
              duplicate_rows: 5,
            },
            validity: {
              overall_validity: 98,
              total_cells: 200,
              valid_cells: 196,
              invalid_cells: 4,
            },
            consistency: {
              overall_consistency: 90,
            },
            dataset_info: {
              rows: 100,
              columns: 2,
              memory_usage_mb: 0.5,
            },
          },
          recommendations: [],
          generated_at: '2024-01-01T00:00:00',
        }),
      });

      renderWithRouter(<DatasetMetrics />);
      
      // Upload file
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      fireEvent.change(input, { target: { files: [file] } });
      
      // Click analyze button
      const analyzeButton = screen.getByText('Analisar Dataset');
      fireEvent.click(analyzeButton);
      
      // Wait for results to appear
      await waitFor(() => {
        expect(screen.getByText('Score Geral de Qualidade')).toBeInTheDocument();
      });

      // Check that metrics are displayed
      expect(screen.getByText('95.5%')).toBeInTheDocument();
      expect(screen.getByText('Completude')).toBeInTheDocument();
      expect(screen.getByText('Unicidade')).toBeInTheDocument();
      expect(screen.getByText('Validade')).toBeInTheDocument();
      expect(screen.getByText('Consistência')).toBeInTheDocument();
    });

    test('handles upload error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Upload failed' }),
      });

      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      fireEvent.change(input, { target: { files: [file] } });
      
      const analyzeButton = screen.getByText('Analisar Dataset');
      fireEvent.click(analyzeButton);
      
      await waitFor(() => {
        expect(screen.getByText('Upload failed')).toBeInTheDocument();
      });
    });
  });

  describe('Results Display', () => {
    test('displays recommendations when available', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessionId: 'test-session-id' }),
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          overall_quality_score: 75,
          metrics: {
            completeness: { overall_completeness: 85 },
            uniqueness: { overall_uniqueness: 90 },
            validity: { overall_validity: 80 },
            consistency: { overall_consistency: 70 },
            dataset_info: { rows: 100, columns: 5, memory_usage_mb: 1 },
          },
          recommendations: [
            {
              severity: 'high',
              category: 'completeness',
              message: 'Dataset has missing values',
            },
          ],
          generated_at: '2024-01-01T00:00:00',
        }),
      });

      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      fireEvent.change(input, { target: { files: [file] } });
      
      const analyzeButton = screen.getByText('Analisar Dataset');
      fireEvent.click(analyzeButton);
      
      await waitFor(() => {
        expect(screen.getByText('Recomendações')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Dataset has missing values')).toBeInTheDocument();
    });

    test('allows analyzing new dataset', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessionId: 'test-session-id' }),
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          overall_quality_score: 95,
          metrics: {
            completeness: { overall_completeness: 100 },
            uniqueness: { overall_uniqueness: 100 },
            validity: { overall_validity: 100 },
            consistency: { overall_consistency: 100 },
            dataset_info: { rows: 100, columns: 5, memory_usage_mb: 1 },
          },
          recommendations: [],
          generated_at: '2024-01-01T00:00:00',
        }),
      });

      renderWithRouter(<DatasetMetrics />);
      
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const input = screen.getByLabelText('Selecionar arquivo');
      fireEvent.change(input, { target: { files: [file] } });
      
      const analyzeButton = screen.getByText('Analisar Dataset');
      fireEvent.click(analyzeButton);
      
      await waitFor(() => {
        expect(screen.getByText('Analisar Novo Dataset')).toBeInTheDocument();
      });

      // Click reset button
      const resetButton = screen.getByText('Analisar Novo Dataset');
      fireEvent.click(resetButton);

      // Upload section should be visible again
      expect(screen.getByText(/Arraste seu dataset aqui/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('sets document title', () => {
      renderWithRouter(<DatasetMetrics />);
      expect(document.title).toBe('Dataset Metrics - DataForgeTest');
    });

    test('has proper button roles', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    test('has proper link navigation', () => {
      renderWithRouter(<DatasetMetrics />);
      
      const backLink = screen.getByRole('link', { name: /Voltar para Home/i });
      expect(backLink).toHaveAttribute('href', '/');
    });
  });
});
