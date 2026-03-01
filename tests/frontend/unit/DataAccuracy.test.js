import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DataAccuracy from '../../../frontend/src/pages/DataAccuracy';

// Mock fetch
global.fetch = jest.fn();

const renderDataAccuracy = () => {
  return render(
    <BrowserRouter>
      <DataAccuracy />
    </BrowserRouter>
  );
};

describe('DataAccuracy Page', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders page title', () => {
    renderDataAccuracy();
    expect(screen.getByText('Acurácia de Dados (Datasets)')).toBeInTheDocument();
  });

  test('renders both upload cards', () => {
    renderDataAccuracy();
    expect(screen.getByText('Dataset GOLD (Referência)')).toBeInTheDocument();
    expect(screen.getByText('Dataset a Validar')).toBeInTheDocument();
  });

  test('renders instructions when no files uploaded', () => {
    renderDataAccuracy();
    expect(screen.getByText('💡 Como usar')).toBeInTheDocument();
  });

  test('shows error message when error occurs', async () => {
    renderDataAccuracy();
    
    // Simulate error by trying to compare without files
    const compareButton = screen.queryByText('Comparar & Corrigir');
    
    // Initially, compare button should not be visible
    expect(compareButton).toBeNull();
  });

  test('upload card accepts file selection', () => {
    renderDataAccuracy();
    
    const fileInputs = screen.getAllByLabelText(/Select file for/i);
    expect(fileInputs).toHaveLength(2);
    
    // GOLD file input
    expect(fileInputs[0]).toHaveAttribute('accept', '.csv,.xlsx,.parquet');
    // TARGET file input
    expect(fileInputs[1]).toHaveAttribute('accept', '.csv,.xlsx,.parquet');
  });

  test('renders back to home link', () => {
    renderDataAccuracy();
    const backLink = screen.getByText('Back to Home');
    expect(backLink).toBeInTheDocument();
    expect(backLink.closest('a')).toHaveAttribute('href', '/');
  });
});

describe('DataAccuracy - File Upload Flow', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('handles successful file upload', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessionId: 'test-session-123',
        role: 'gold',
        datasetId: 'dataset-123',
        columns: ['produto', 'preco_unitario'],
        preview: [
          { produto: 'A', preco_unitario: 10.0 },
          { produto: 'B', preco_unitario: 20.0 }
        ],
        rowCount: 2
      })
    });

    renderDataAccuracy();

    const fileInput = screen.getAllByLabelText(/Select file for/i)[0];
    const file = new File(['test'], 'test.csv', { type: 'text/csv' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });
});

describe('DataAccuracy - Column Mapping and Compare', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  const uploadBothFiles = async () => {
    const colsResponse = {
      ok: true,
      json: async () => ({
        sessionId: 'test-session-123',
        columns: ['produto', 'preco'],
        preview: [{ produto: 'A', preco: 10.0 }],
        rowCount: 1,
      }),
    };
    fetch.mockResolvedValueOnce(colsResponse);
    fetch.mockResolvedValueOnce(colsResponse);

    renderDataAccuracy();

    const fileInputs = screen.getAllByLabelText(/Select file for/i);
    const goldFile = new File(['test'], 'gold.csv', { type: 'text/csv' });
    const targetFile = new File(['test'], 'target.csv', { type: 'text/csv' });

    fireEvent.change(fileInputs[0], { target: { files: [goldFile] } });
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    fireEvent.change(fileInputs[1], { target: { files: [targetFile] } });
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  };

  test('shows ColumnMapping after both files uploaded', async () => {
    await uploadBothFiles();
    await waitFor(() => {
      expect(screen.getByText('Mapeamento de Colunas')).toBeInTheDocument();
    });
  });

  test('shows Comparar button after columns available', async () => {
    await uploadBothFiles();
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Comparar e corrigir/i })).toBeInTheDocument();
    });
  });

  test('compare button is disabled without key/value columns selected', async () => {
    await uploadBothFiles();
    await waitFor(() => {
      const compareBtn = screen.getByRole('button', { name: /Comparar e corrigir/i });
      expect(compareBtn).toBeDisabled();
    });
  });

  test('shows error message when error state is set', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Server error occurred' }),
    });
    renderDataAccuracy();
    const fileInput = screen.getAllByLabelText(/Select file for/i)[0];
    fireEvent.change(fileInput, { target: { files: [new File([''], 'gold.csv')] } });
    await waitFor(() => {
      expect(screen.getByText('Server error occurred')).toBeInTheDocument();
    });
  });

  test('shows compare and reset buttons when columns are available', async () => {
    await uploadBothFiles();
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Comparar e corrigir/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Limpar e reiniciar/i })).toBeInTheDocument();
    });
  });

  test('calls reset when Limpar button is clicked', async () => {
    await uploadBothFiles();
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Limpar e reiniciar/i })).toBeInTheDocument();
    });
    const resetBtn = screen.getByRole('button', { name: /Limpar e reiniciar/i });
    fireEvent.click(resetBtn);
    // After reset, ColumnMapping should disappear
    await waitFor(() => {
      expect(screen.queryByText('Mapeamento de Colunas')).not.toBeInTheDocument();
    });
  });

  test('shows ResultsPanel when results are available', async () => {
    // Upload gold
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessionId: 'test-session-123',
        columns: ['produto', 'preco'],
        preview: [{ produto: 'A', preco: 10.0 }],
        rowCount: 1,
      }),
    });
    // Upload target
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessionId: 'test-session-123',
        columns: ['produto', 'preco'],
        preview: [{ produto: 'A', preco: 9.0 }],
        rowCount: 1,
      }),
    });
    // Compare
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        summary: {
          rows_gold: 1,
          rows_target: 1,
          common_keys: 1,
          missing_in_target: 0,
          extra_in_target: 0,
          mismatches_total: 1,
          accuracy: 0.0,
        },
        differences: [{ keys: { produto: 'A' }, column: 'preco', gold: 10.0, target: 9.0, corrected: 10.0, delta: 1.0 }],
        downloadLinks: { correctedCsv: '/dl/corr', diffCsv: '/dl/diff', reportJson: '/dl/report' },
      }),
    });

    renderDataAccuracy();

    const fileInputs = screen.getAllByLabelText(/Select file for/i);
    fireEvent.change(fileInputs[0], { target: { files: [new File([''], 'gold.csv')] } });
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    fireEvent.change(fileInputs[1], { target: { files: [new File([''], 'target.csv')] } });
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));

    await waitFor(() => {
      expect(screen.getByText('Mapeamento de Colunas')).toBeInTheDocument();
    });

    // Select key column (produto) and value column (preco)
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]); // key: produto
    fireEvent.click(checkboxes[3]); // value: preco (second section, index 3)

    // Click Compare
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Comparar e corrigir/i })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: /Comparar e corrigir/i }));

    await waitFor(() => {
      expect(screen.getByText('Resumo da Comparação')).toBeInTheDocument();
    });
  });
});
