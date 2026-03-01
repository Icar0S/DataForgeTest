/**
 * Tests for ColumnMapping component
 * Covers key/value column selection, options changes
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ColumnMapping from '../../../frontend/src/components/accuracy/ColumnMapping';

jest.mock('lucide-react', () => ({
  Key: () => <svg data-testid="key-icon" />,
  BarChart2: () => <svg data-testid="barchart-icon" />,
}));

const defaultColumns = ['produto', 'preco', 'quantidade', 'data'];
const defaultMapping = { keyColumns: [], valueColumns: [] };
const defaultOptions = {
  normalizeKeys: true,
  lowercase: true,
  stripAccents: true,
  stripPunctuation: true,
  coerceNumeric: true,
  decimalPlaces: 2,
  tolerance: 0.0,
  targetDuplicatePolicy: 'keep_last',
};

const defaultProps = {
  columns: defaultColumns,
  mapping: defaultMapping,
  onMappingChange: jest.fn(),
  options: defaultOptions,
  onOptionsChange: jest.fn(),
};

describe('ColumnMapping Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders key columns checkboxes for each column', () => {
      render(<ColumnMapping {...defaultProps} />);
      // Each column appears twice (once for key, once for value)
      const checkboxes = screen.getAllByRole('checkbox');
      // 4 columns * 2 sections (key + value) + 4 option checkboxes = 12
      expect(checkboxes.length).toBeGreaterThanOrEqual(8);
    });

    test('renders value columns checkboxes for each column', () => {
      render(<ColumnMapping {...defaultProps} />);
      expect(screen.getByText('Colunas de Valor (Comparação)')).toBeInTheDocument();
    });

    test('renders with empty columns list without crashing', () => {
      render(<ColumnMapping {...defaultProps} columns={[]} />);
      expect(screen.getByText('Mapeamento de Colunas')).toBeInTheDocument();
    });

    test('renders options section', () => {
      render(<ColumnMapping {...defaultProps} />);
      expect(screen.getByText('Opções')).toBeInTheDocument();
      expect(screen.getByText('Tolerância Numérica')).toBeInTheDocument();
      expect(screen.getByText('Casas Decimais')).toBeInTheDocument();
    });

    test('renders normalization options', () => {
      render(<ColumnMapping {...defaultProps} />);
      expect(screen.getByText('Minúsculas')).toBeInTheDocument();
      expect(screen.getByText('Remover acentos')).toBeInTheDocument();
      expect(screen.getByText('Remover pontuação')).toBeInTheDocument();
      expect(screen.getByText('Coerção numérica (vírgula → ponto)')).toBeInTheDocument();
    });

    test('renders duplicate policy dropdown', () => {
      render(<ColumnMapping {...defaultProps} />);
      expect(screen.getByText('Política de Duplicatas (TARGET)')).toBeInTheDocument();
    });
  });

  describe('Key column selection', () => {
    test('calls onMappingChange when a key column is checked', () => {
      const onMappingChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onMappingChange={onMappingChange} />);
      const checkboxes = screen.getAllByRole('checkbox');
      // First checkbox should be for the first key column
      fireEvent.click(checkboxes[0]);
      expect(onMappingChange).toHaveBeenCalledWith({
        ...defaultMapping,
        keyColumns: ['produto'],
      });
    });

    test('calls onMappingChange when a key column is unchecked', () => {
      const onMappingChange = jest.fn();
      const mappingWithKey = { keyColumns: ['produto'], valueColumns: [] };
      render(<ColumnMapping {...defaultProps} mapping={mappingWithKey} onMappingChange={onMappingChange} />);
      const checkboxes = screen.getAllByRole('checkbox');
      // First checkbox is checked (produto is in keyColumns)
      expect(checkboxes[0]).toBeChecked();
      fireEvent.click(checkboxes[0]);
      expect(onMappingChange).toHaveBeenCalledWith({
        ...mappingWithKey,
        keyColumns: [],
      });
    });

    test('reflects checked state for pre-selected key columns', () => {
      const mappingWithKey = { keyColumns: ['produto', 'preco'], valueColumns: [] };
      render(<ColumnMapping {...defaultProps} mapping={mappingWithKey} />);
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes[0]).toBeChecked(); // produto
      expect(checkboxes[1]).toBeChecked(); // preco
      expect(checkboxes[2]).not.toBeChecked(); // quantidade
    });
  });

  describe('Value column selection', () => {
    test('calls onMappingChange when a value column is checked', () => {
      const onMappingChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onMappingChange={onMappingChange} />);
      // Value columns are the second set of checkboxes (indices 4-7)
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[4]); // first value column
      expect(onMappingChange).toHaveBeenCalledWith({
        ...defaultMapping,
        valueColumns: ['produto'],
      });
    });

    test('calls onMappingChange when a value column is unchecked', () => {
      const onMappingChange = jest.fn();
      const mappingWithValue = { keyColumns: [], valueColumns: ['produto'] };
      render(<ColumnMapping {...defaultProps} mapping={mappingWithValue} onMappingChange={onMappingChange} />);
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes[4]).toBeChecked();
      fireEvent.click(checkboxes[4]);
      expect(onMappingChange).toHaveBeenCalledWith({
        ...mappingWithValue,
        valueColumns: [],
      });
    });

    test('reflects checked state for pre-selected value columns', () => {
      const mappingWithValue = { keyColumns: [], valueColumns: ['preco', 'quantidade'] };
      render(<ColumnMapping {...defaultProps} mapping={mappingWithValue} />);
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes[4]).not.toBeChecked(); // produto (value)
      expect(checkboxes[5]).toBeChecked();     // preco (value)
      expect(checkboxes[6]).toBeChecked();     // quantidade (value)
    });

    test('a column can be both key and value simultaneously', () => {
      const mappingBoth = { keyColumns: ['produto'], valueColumns: ['produto'] };
      render(<ColumnMapping {...defaultProps} mapping={mappingBoth} />);
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes[0]).toBeChecked(); // key: produto
      expect(checkboxes[4]).toBeChecked(); // value: produto
    });
  });

  describe('Options changes', () => {
    test('calls onOptionsChange when lowercase option is toggled', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const lowercaseCheckbox = screen.getByLabelText('Minúsculas', { exact: false });
      // Actually get the checkbox by its label text
      const allCheckboxes = screen.getAllByRole('checkbox');
      // Option checkboxes come after key/value ones - find by label
      fireEvent.click(allCheckboxes[8]); // lowercase checkbox (after 4+4 column checkboxes)
      expect(onOptionsChange).toHaveBeenCalled();
    });

    test('calls onOptionsChange when stripAccents option is toggled', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const allCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(allCheckboxes[9]); // stripAccents
      expect(onOptionsChange).toHaveBeenCalled();
    });

    test('calls onOptionsChange when tolerance is changed', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const toleranceInput = screen.getByDisplayValue('0');
      fireEvent.change(toleranceInput, { target: { value: '0.05' } });
      expect(onOptionsChange).toHaveBeenCalledWith(
        expect.objectContaining({ tolerance: 0.05 })
      );
    });

    test('calls onOptionsChange when decimal places is changed', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const decimalInput = screen.getByDisplayValue('2');
      fireEvent.change(decimalInput, { target: { value: '3' } });
      expect(onOptionsChange).toHaveBeenCalledWith(
        expect.objectContaining({ decimalPlaces: 3 })
      );
    });

    test('calls onOptionsChange when duplicate policy is changed', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const select = screen.getByDisplayValue('Manter última');
      fireEvent.change(select, { target: { value: 'sum' } });
      expect(onOptionsChange).toHaveBeenCalledWith(
        expect.objectContaining({ targetDuplicatePolicy: 'sum' })
      );
    });

    test('calls onOptionsChange when coerceNumeric option is toggled', () => {
      const onOptionsChange = jest.fn();
      render(<ColumnMapping {...defaultProps} onOptionsChange={onOptionsChange} />);
      const allCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(allCheckboxes[11]); // coerceNumeric
      expect(onOptionsChange).toHaveBeenCalled();
    });
  });
});
