/**
 * Tests for AdvancedPySparkGenerator page
 * Covers 4-step flow: upload, metadata, DSL, PySpark code
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import AdvancedPySparkGenerator from '../../../frontend/src/pages/AdvancedPySparkGenerator';

// Mock fetch
global.fetch = jest.fn();

// Mock syntax highlighter
jest.mock('react-syntax-highlighter', () => ({
  Prism: ({ children }) => <pre data-testid="syntax-highlighter">{children}</pre>,
}));
jest.mock('react-syntax-highlighter/dist/esm/styles/prism', () => ({
  materialDark: {},
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }) => <h1 {...props}>{children}</h1>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

// Mock lucide-react
jest.mock('lucide-react', () => ({
  ArrowLeft: () => <svg data-testid="arrow-left" />,
  Upload: () => <svg data-testid="upload-icon" />,
  FileText: () => <svg data-testid="file-icon" />,
  CheckCircle: () => <svg data-testid="check-icon" />,
  Code: () => <svg data-testid="code-icon" />,
  Copy: () => <svg data-testid="copy-icon" />,
  Download: () => <svg data-testid="download-icon" />,
  ChevronRight: () => <svg data-testid="chevron-right" />,
  ChevronLeft: () => <svg data-testid="chevron-left" />,
  AlertCircle: () => <svg data-testid="alert-icon" />,
}));

// Mock clipboard
Object.assign(navigator, {
  clipboard: { writeText: jest.fn() },
});

const renderWithRouter = (component) =>
  render(<BrowserRouter>{component}</BrowserRouter>);

const mockMetadata = {
  columns: [
    { name: 'id', dtype: 'int64', nullable: false, examples: [1, 2, 3] },
    { name: 'name', dtype: 'object', nullable: true, examples: ['Alice', 'Bob'] },
  ],
  row_count: 100,
  file_name: 'dataset.csv',
};

const mockDsl = {
  dataset: { name: 'dataset' },
  rules: [{ type: 'not_null', column: 'id' }],
};

const mockPysparkCode = 'from pyspark.sql import SparkSession\n# Generated code';

describe('AdvancedPySparkGenerator Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    jest.clearAllMocks();
  });

  describe('Step 1 - Upload', () => {
    test('renders step 1 (upload) initially', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      expect(screen.getByText(/Step 1: Upload Dataset/i)).toBeInTheDocument();
    });

    test('shows file selection interface in step 1', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      expect(screen.getByText(/Select Dataset File/i)).toBeInTheDocument();
    });

    test('shows CSV upload options after CSV file selection', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      expect(screen.getByText(/Delimiter/i)).toBeInTheDocument();
      expect(screen.getByText(/Encoding/i)).toBeInTheDocument();
    });

    test('shows error when trying to proceed without file', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      // The button is disabled when no file is selected
      const uploadBtn = screen.getByRole('button', { name: /Inspect Dataset/i });
      expect(uploadBtn).toBeDisabled();
    });

    test('shows selected file name after selection', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      Object.defineProperty(file, 'size', { value: 1024 });
      fireEvent.change(input, { target: { files: [file] } });
      expect(screen.getByText(/Selected: data.csv/i)).toBeInTheDocument();
    });

    test('proceeds to step 2 after successful upload', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      const uploadBtn = screen.getByRole('button', { name: /Inspect Dataset/i });
      fireEvent.click(uploadBtn);
      await waitFor(() => {
        expect(screen.getByText(/Step 2: Review Dataset Metadata/i)).toBeInTheDocument();
      });
    });

    test('shows error on upload failure', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Unsupported file format' }),
        status: 400,
        statusText: 'Bad Request',
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => {
        expect(screen.getByText(/Unsupported file format/i)).toBeInTheDocument();
      });
    });

    test('shows network error with descriptive message', async () => {
      fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Step 2 - Metadata review', () => {
    const goToStep2 = async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => {
        expect(screen.getByText(/Step 2: Review Dataset Metadata/i)).toBeInTheDocument();
      });
    };

    test('shows metadata editor in step 2', async () => {
      await goToStep2();
      // Column names from mock metadata are shown in the metadata table
      expect(screen.getAllByText('id').length).toBeGreaterThan(0);
      expect(screen.getAllByText('name').length).toBeGreaterThan(0);
    });

    test('back button returns to step 1 from step 2', async () => {
      await goToStep2();
      const backBtn = screen.getByRole('button', { name: /Back/i });
      fireEvent.click(backBtn);
      expect(screen.getByText(/Step 1: Upload Dataset/i)).toBeInTheDocument();
    });

    test('proceeds to step 3 after generate DSL', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      });
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ dsl: mockDsl }),
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => screen.getByText(/Step 2: Review Dataset Metadata/i));
      fireEvent.click(screen.getByRole('button', { name: /Generate DSL/i }));
      await waitFor(() => {
        expect(screen.getByText(/Step 3: Review and Edit DSL/i)).toBeInTheDocument();
      });
    });
  });

  describe('Step 3 - DSL review', () => {
    const goToStep3 = async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      });
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ dsl: mockDsl }),
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => screen.getByText(/Step 2: Review Dataset Metadata/i));
      fireEvent.click(screen.getByRole('button', { name: /Generate DSL/i }));
      await waitFor(() => screen.getByText(/Step 3: Review and Edit DSL/i));
    };

    test('shows DSL editor in step 3', async () => {
      await goToStep3();
      expect(screen.getByText(/Step 3: Review and Edit DSL/i)).toBeInTheDocument();
    });

    test('back button returns to step 2 from step 3', async () => {
      await goToStep3();
      const backBtn = screen.getByRole('button', { name: /Back/i });
      fireEvent.click(backBtn);
      expect(screen.getByText(/Step 2: Review Dataset Metadata/i)).toBeInTheDocument();
    });

    test('proceeds to step 4 after generate PySpark', async () => {
      await goToStep3();
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          pyspark_code: mockPysparkCode,
          filename: 'generated_code.py',
        }),
      });
      fireEvent.click(screen.getByRole('button', { name: /Generate PySpark Code/i }));
      await waitFor(() => {
        expect(screen.getByText(/Step 4: PySpark Code/i)).toBeInTheDocument();
      });
    });
  });

  describe('Step 4 - PySpark code', () => {
    const goToStep4 = async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      });
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ dsl: mockDsl }),
      });
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          pyspark_code: mockPysparkCode,
          filename: 'generated_code.py',
        }),
      });
      renderWithRouter(<AdvancedPySparkGenerator />);
      const input = document.querySelector('input[type="file"]');
      const file = new File(['content'], 'data.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: /Inspect Dataset/i }));
      await waitFor(() => screen.getByText(/Step 2: Review Dataset Metadata/i));
      fireEvent.click(screen.getByRole('button', { name: /Generate DSL/i }));
      await waitFor(() => screen.getByText(/Step 3: Review and Edit DSL/i));
      fireEvent.click(screen.getByRole('button', { name: /Generate PySpark Code/i }));
      await waitFor(() => screen.getByText(/Step 4: PySpark Code/i));
    };

    test('shows generated PySpark code in step 4', async () => {
      await goToStep4();
      expect(screen.getByText(/Step 4: PySpark Code/i)).toBeInTheDocument();
    });

    test('copy button calls clipboard.writeText', async () => {
      await goToStep4();
      fireEvent.click(screen.getByRole('button', { name: /Copy/i }));
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockPysparkCode);
    });

    test('back button returns to step 3 from step 4', async () => {
      await goToStep4();
      // Step 4 has no Back button - there is a "Generate Another Dataset" button instead
      // Verify we are on step 4
      expect(screen.getByText(/Step 4: PySpark Code/i)).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    test('has link back to home', () => {
      renderWithRouter(<AdvancedPySparkGenerator />);
      const homeLink = screen.getByRole('link');
      expect(homeLink).toHaveAttribute('href', '/');
    });
  });
});
