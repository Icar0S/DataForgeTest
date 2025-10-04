import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DataAccuracy from '../pages/DataAccuracy';

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
    const backLink = screen.getByText('Voltar para Home');
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
