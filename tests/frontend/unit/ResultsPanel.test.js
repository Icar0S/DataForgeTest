/**
 * Tests for ResultsPanel component
 * Covers summary display, pagination, download buttons, accuracy icons
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResultsPanel from '../../../frontend/src/components/accuracy/ResultsPanel';

jest.mock('lucide-react', () => ({
  Download: () => <svg data-testid="download-icon" />,
  TrendingUp: () => <svg data-testid="trending-icon" />,
  AlertTriangle: () => <svg data-testid="alert-icon" />,
  CheckCircle: () => <svg data-testid="check-icon" />,
}));

const mockSummary = {
  rows_gold: 100,
  rows_target: 95,
  common_keys: 90,
  missing_in_target: 10,
  extra_in_target: 5,
  mismatches_total: 3,
  accuracy: 0.9667,
};

const mockDifferences = Array.from({ length: 25 }, (_, i) => ({
  keys: { id: i + 1 },
  column: `col_${i}`,
  gold: 10.0 + i,
  target: 9.0 + i,
  corrected: 10.0 + i,
  delta: 1.0,
}));

const mockDownloadLinks = {
  correctedCsv: '/api/accuracy/download/corrected.csv',
  diffCsv: '/api/accuracy/download/diff.csv',
  reportJson: '/api/accuracy/download/report.json',
};

const defaultProps = {
  summary: mockSummary,
  differences: [],
  downloadLinks: null,
  onDownload: jest.fn(),
};

describe('ResultsPanel Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Null/missing summary', () => {
    test('returns null when summary is not provided', () => {
      const { container } = render(
        <ResultsPanel summary={null} differences={[]} onDownload={jest.fn()} />
      );
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Summary metrics', () => {
    test('renders summary metrics with correct values', () => {
      render(<ResultsPanel {...defaultProps} />);
      expect(screen.getByText('100')).toBeInTheDocument(); // rows_gold
      expect(screen.getByText('95')).toBeInTheDocument();  // rows_target
      expect(screen.getByText('90')).toBeInTheDocument();  // common_keys
      expect(screen.getByText('10')).toBeInTheDocument();  // missing_in_target
      expect(screen.getByText('5')).toBeInTheDocument();   // extra_in_target
      expect(screen.getByText('3')).toBeInTheDocument();   // mismatches_total
    });

    test('renders section labels', () => {
      render(<ResultsPanel {...defaultProps} />);
      expect(screen.getByText('Linhas GOLD')).toBeInTheDocument();
      expect(screen.getByText('Linhas TARGET')).toBeInTheDocument();
      expect(screen.getByText('Chaves Comuns')).toBeInTheDocument();
      expect(screen.getByText('Ausentes no TARGET')).toBeInTheDocument();
      expect(screen.getByText('Extras no TARGET')).toBeInTheDocument();
      expect(screen.getByText('Divergências')).toBeInTheDocument();
    });

    test('renders accuracy percentage correctly', () => {
      render(<ResultsPanel {...defaultProps} />);
      expect(screen.getByText('96.67%')).toBeInTheDocument();
    });

    test('renders accuracy label', () => {
      render(<ResultsPanel {...defaultProps} />);
      expect(screen.getByText('Acurácia dos Dados')).toBeInTheDocument();
    });

    test('renders matches/total comparison', () => {
      render(<ResultsPanel {...defaultProps} />);
      // 90 - 3 = 87 matches / 90 total
      expect(screen.getByText('87 / 90')).toBeInTheDocument();
    });
  });

  describe('Differences table with pagination', () => {
    test('renders differences table when differences exist', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      expect(screen.getByText(/Diferenças Detectadas \(25\)/)).toBeInTheDocument();
    });

    test('renders paginated data - shows first 10 rows on page 1', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      expect(screen.getByText('col_0')).toBeInTheDocument();
      expect(screen.getByText('col_9')).toBeInTheDocument();
      expect(screen.queryByText('col_10')).not.toBeInTheDocument();
    });

    test('shows correct page info text', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      expect(screen.getByText('Mostrando 1-10 de 25')).toBeInTheDocument();
    });

    test('navigates to next page when Próximo is clicked', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      const nextBtn = screen.getByRole('button', { name: /Próximo/i });
      fireEvent.click(nextBtn);
      expect(screen.getByText('col_10')).toBeInTheDocument();
      expect(screen.queryByText('col_0')).not.toBeInTheDocument();
    });

    test('navigates to previous page when Anterior is clicked', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      // Go to page 2 first
      fireEvent.click(screen.getByRole('button', { name: /Próximo/i }));
      // Then go back
      fireEvent.click(screen.getByRole('button', { name: /Anterior/i }));
      expect(screen.getByText('col_0')).toBeInTheDocument();
    });

    test('disables Anterior button on first page', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      const prevBtn = screen.getByRole('button', { name: /Anterior/i });
      expect(prevBtn).toBeDisabled();
    });

    test('disables Próximo button on last page', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      // Navigate to last page (25 items / 10 per page = 3 pages)
      fireEvent.click(screen.getByRole('button', { name: /Próximo/i }));
      fireEvent.click(screen.getByRole('button', { name: /Próximo/i }));
      const nextBtn = screen.getByRole('button', { name: /Próximo/i });
      expect(nextBtn).toBeDisabled();
    });

    test('does not show pagination for fewer than 11 rows', () => {
      const fewDiffs = mockDifferences.slice(0, 5);
      render(<ResultsPanel {...defaultProps} differences={fewDiffs} />);
      expect(screen.queryByRole('button', { name: /Próximo/i })).not.toBeInTheDocument();
    });

    test('does not show differences section when differences is empty', () => {
      render(<ResultsPanel {...defaultProps} differences={[]} />);
      expect(screen.queryByText(/Diferenças Detectadas/)).not.toBeInTheDocument();
    });

    test('shows delta values in differences table', () => {
      render(<ResultsPanel {...defaultProps} differences={mockDifferences} />);
      // Delta is 1.00 for all rows, so '1.00' should appear
      const deltaValues = screen.getAllByText('1.00');
      expect(deltaValues.length).toBeGreaterThan(0);
    });
  });

  describe('Download buttons', () => {
    test('renders download buttons when downloadLinks provided', () => {
      render(<ResultsPanel {...defaultProps} downloadLinks={mockDownloadLinks} />);
      expect(screen.getByLabelText('Baixar dataset corrigido')).toBeInTheDocument();
      expect(screen.getByLabelText('Baixar relatório de diferenças')).toBeInTheDocument();
      expect(screen.getByLabelText('Baixar relatório JSON')).toBeInTheDocument();
    });

    test('calls onDownload with correctedCsv when download button clicked', () => {
      const onDownload = jest.fn();
      render(<ResultsPanel {...defaultProps} downloadLinks={mockDownloadLinks} onDownload={onDownload} />);
      fireEvent.click(screen.getByLabelText('Baixar dataset corrigido'));
      expect(onDownload).toHaveBeenCalledWith(mockDownloadLinks.correctedCsv);
    });

    test('calls onDownload with diffCsv when diff download button clicked', () => {
      const onDownload = jest.fn();
      render(<ResultsPanel {...defaultProps} downloadLinks={mockDownloadLinks} onDownload={onDownload} />);
      fireEvent.click(screen.getByLabelText('Baixar relatório de diferenças'));
      expect(onDownload).toHaveBeenCalledWith(mockDownloadLinks.diffCsv);
    });

    test('calls onDownload with reportJson when JSON download button clicked', () => {
      const onDownload = jest.fn();
      render(<ResultsPanel {...defaultProps} downloadLinks={mockDownloadLinks} onDownload={onDownload} />);
      fireEvent.click(screen.getByLabelText('Baixar relatório JSON'));
      expect(onDownload).toHaveBeenCalledWith(mockDownloadLinks.reportJson);
    });

    test('does not render download section when downloadLinks is null', () => {
      render(<ResultsPanel {...defaultProps} downloadLinks={null} />);
      expect(screen.queryByLabelText('Baixar dataset corrigido')).not.toBeInTheDocument();
    });
  });
});
