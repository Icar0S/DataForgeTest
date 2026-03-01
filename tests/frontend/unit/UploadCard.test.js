/**
 * Tests for UploadCard component
 * Covers all branches: no-file state, file selected, loading, preview
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UploadCard from '../../../frontend/src/components/accuracy/UploadCard';

jest.mock('lucide-react', () => ({
  Upload: () => <svg data-testid="upload-icon" />,
  FileText: () => <svg data-testid="file-icon" />,
  X: () => <svg data-testid="x-icon" />,
}));

const defaultProps = {
  role: 'gold',
  title: 'Dataset GOLD',
  file: null,
  onFileSelect: jest.fn(),
  onRemove: jest.fn(),
  preview: null,
  isLoading: false,
};

describe('UploadCard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('No-file state', () => {
    test('renders upload area when no file is selected', () => {
      render(<UploadCard {...defaultProps} />);
      expect(screen.getByText('Arraste e solte o arquivo aqui')).toBeInTheDocument();
      expect(screen.getByText('Selecionar Arquivo')).toBeInTheDocument();
      expect(screen.getByTestId('upload-icon')).toBeInTheDocument();
    });

    test('renders file input with correct accept attribute', () => {
      render(<UploadCard {...defaultProps} />);
      const input = screen.getByLabelText(/Select file for Dataset GOLD/i);
      expect(input).toHaveAttribute('accept', '.csv,.xlsx,.parquet');
    });

    test('calls onFileSelect when file is selected via input', () => {
      const onFileSelect = jest.fn();
      render(<UploadCard {...defaultProps} onFileSelect={onFileSelect} />);
      const input = screen.getByLabelText(/Select file for Dataset GOLD/i);
      const file = new File(['content'], 'test.csv', { type: 'text/csv' });
      fireEvent.change(input, { target: { files: [file] } });
      expect(onFileSelect).toHaveBeenCalledWith(file);
    });

    test('does not call onFileSelect if no file in input', () => {
      const onFileSelect = jest.fn();
      render(<UploadCard {...defaultProps} onFileSelect={onFileSelect} />);
      const input = screen.getByLabelText(/Select file for Dataset GOLD/i);
      fireEvent.change(input, { target: { files: [] } });
      expect(onFileSelect).not.toHaveBeenCalled();
    });

    test('calls onFileSelect when file is dropped', () => {
      const onFileSelect = jest.fn();
      render(<UploadCard {...defaultProps} onFileSelect={onFileSelect} />);
      const dropZone = screen.getByText('Arraste e solte o arquivo aqui').closest('div');
      const file = new File(['content'], 'dropped.csv', { type: 'text/csv' });
      fireEvent.drop(dropZone, {
        dataTransfer: { files: [file] },
      });
      expect(onFileSelect).toHaveBeenCalledWith(file);
    });

    test('does not call onFileSelect when dropped with no files', () => {
      const onFileSelect = jest.fn();
      render(<UploadCard {...defaultProps} onFileSelect={onFileSelect} />);
      const dropZone = screen.getByText('Arraste e solte o arquivo aqui').closest('div');
      fireEvent.drop(dropZone, { dataTransfer: { files: [] } });
      expect(onFileSelect).not.toHaveBeenCalled();
    });

    test('prevents default on dragOver', () => {
      render(<UploadCard {...defaultProps} />);
      const dropZone = screen.getByText('Arraste e solte o arquivo aqui').closest('div');
      // dragOver should not throw (preventDefault is called)
      expect(() => fireEvent.dragOver(dropZone)).not.toThrow();
    });
  });

  describe('File selected state', () => {
    const TWO_MB = 2 * 1024 * 1024;
    const file = new File(['content'], 'mydata.csv', { type: 'text/csv' });
    Object.defineProperty(file, 'size', { value: TWO_MB }); // 2 MB

    test('shows file name when file is provided', () => {
      render(<UploadCard {...defaultProps} file={file} />);
      expect(screen.getByText('mydata.csv')).toBeInTheDocument();
    });

    test('shows file size in MB when file is provided', () => {
      render(<UploadCard {...defaultProps} file={file} />);
      expect(screen.getByText(/MB/)).toBeInTheDocument();
    });

    test('shows remove button when file is provided', () => {
      render(<UploadCard {...defaultProps} file={file} />);
      expect(screen.getByRole('button', { name: /Remove Dataset GOLD/i })).toBeInTheDocument();
    });

    test('calls onRemove when remove button is clicked', () => {
      const onRemove = jest.fn();
      render(<UploadCard {...defaultProps} file={file} onRemove={onRemove} />);
      fireEvent.click(screen.getByRole('button', { name: /Remove Dataset GOLD/i }));
      expect(onRemove).toHaveBeenCalledTimes(1);
    });

    test('does not render drag-and-drop area when file is selected', () => {
      render(<UploadCard {...defaultProps} file={file} />);
      expect(screen.queryByText('Arraste e solte o arquivo aqui')).not.toBeInTheDocument();
    });

    test('shows file icon when file is provided', () => {
      render(<UploadCard {...defaultProps} file={file} />);
      expect(screen.getByTestId('file-icon')).toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    const file = new File(['content'], 'data.csv', { type: 'text/csv' });

    test('shows loading spinner when isLoading is true', () => {
      render(<UploadCard {...defaultProps} file={file} isLoading={true} />);
      expect(screen.getByText('Carregando preview...')).toBeInTheDocument();
    });

    test('hides loading spinner when isLoading is false', () => {
      render(<UploadCard {...defaultProps} file={file} isLoading={false} />);
      expect(screen.queryByText('Carregando preview...')).not.toBeInTheDocument();
    });
  });

  describe('Preview state', () => {
    const file = new File(['content'], 'data.csv', { type: 'text/csv' });
    const previewData = [
      { id: 1, name: 'Alice', value: 100 },
      { id: 2, name: 'Bob', value: 200 },
    ];

    test('renders preview table when preview data exists', () => {
      render(<UploadCard {...defaultProps} file={file} preview={previewData} />);
      expect(screen.getByText('Preview (primeiras 20 linhas)')).toBeInTheDocument();
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    test('renders column headers from preview data', () => {
      render(<UploadCard {...defaultProps} file={file} preview={previewData} />);
      expect(screen.getByText('id')).toBeInTheDocument();
      expect(screen.getByText('name')).toBeInTheDocument();
      expect(screen.getByText('value')).toBeInTheDocument();
    });

    test('does not render preview table when preview is empty array', () => {
      render(<UploadCard {...defaultProps} file={file} preview={[]} />);
      expect(screen.queryByText('Preview (primeiras 20 linhas)')).not.toBeInTheDocument();
    });

    test('does not render preview table when preview is null', () => {
      render(<UploadCard {...defaultProps} file={file} preview={null} />);
      expect(screen.queryByText('Preview (primeiras 20 linhas)')).not.toBeInTheDocument();
    });

    test('renders null values as "null" text', () => {
      const previewWithNull = [{ id: 1, name: null }];
      render(<UploadCard {...defaultProps} file={file} preview={previewWithNull} />);
      expect(screen.getByText('null')).toBeInTheDocument();
    });
  });

  describe('Title rendering', () => {
    test('renders correct title', () => {
      render(<UploadCard {...defaultProps} title="My Custom Title" />);
      expect(screen.getByText('My Custom Title')).toBeInTheDocument();
    });
  });
});
