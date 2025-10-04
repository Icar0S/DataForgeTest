import React from 'react';
import PropTypes from 'prop-types';
import { Key, BarChart2 } from 'lucide-react';

const ColumnMapping = ({ columns, mapping, onMappingChange, options, onOptionsChange }) => {
  const handleKeyColumnToggle = (column) => {
    const newKeyColumns = mapping.keyColumns.includes(column)
      ? mapping.keyColumns.filter(c => c !== column)
      : [...mapping.keyColumns, column];
    onMappingChange({ ...mapping, keyColumns: newKeyColumns });
  };

  const handleValueColumnToggle = (column) => {
    const newValueColumns = mapping.valueColumns.includes(column)
      ? mapping.valueColumns.filter(c => c !== column)
      : [...mapping.valueColumns, column];
    onMappingChange({ ...mapping, valueColumns: newValueColumns });
  };

  const handleOptionChange = (key, value) => {
    onOptionsChange({ ...options, [key]: value });
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 space-y-6">
      <h3 className="text-xl font-bold text-white mb-4">Mapeamento de Colunas</h3>

      {/* Column Selection */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Key Columns */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Key className="w-5 h-5 text-purple-400" />
            <label className="text-white font-semibold">Colunas Chave (Identificadores)</label>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {columns.map((col) => (
              <label key={col} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={mapping.keyColumns.includes(col)}
                  onChange={() => handleKeyColumnToggle(col)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-gray-300 group-hover:text-white transition-colors">{col}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Value Columns */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BarChart2 className="w-5 h-5 text-pink-400" />
            <label className="text-white font-semibold">Colunas de Valor (Comparação)</label>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {columns.map((col) => (
              <label key={col} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={mapping.valueColumns.includes(col)}
                  onChange={() => handleValueColumnToggle(col)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-pink-600 focus:ring-pink-500"
                />
                <span className="text-gray-300 group-hover:text-white transition-colors">{col}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Options */}
      <div className="space-y-4 border-t border-gray-700 pt-4">
        <h4 className="text-white font-semibold">Opções</h4>

        {/* Numeric Options */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-300 text-sm mb-2">
              Tolerância Numérica
            </label>
            <input
              type="number"
              step="0.01"
              value={options.tolerance}
              onChange={(e) => handleOptionChange('tolerance', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-gray-300 text-sm mb-2">
              Casas Decimais
            </label>
            <input
              type="number"
              min="0"
              max="10"
              value={options.decimalPlaces}
              onChange={(e) => handleOptionChange('decimalPlaces', parseInt(e.target.value) || 2)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {/* Normalization Options */}
        <div>
          <label className="block text-gray-300 font-semibold mb-2">Normalização de Chaves</label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.lowercase}
                onChange={(e) => handleOptionChange('lowercase', e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600"
              />
              <span className="text-gray-300">Minúsculas</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.stripAccents}
                onChange={(e) => handleOptionChange('stripAccents', e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600"
              />
              <span className="text-gray-300">Remover acentos</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.stripPunctuation}
                onChange={(e) => handleOptionChange('stripPunctuation', e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600"
              />
              <span className="text-gray-300">Remover pontuação</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.coerceNumeric}
                onChange={(e) => handleOptionChange('coerceNumeric', e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600"
              />
              <span className="text-gray-300">Coerção numérica (vírgula → ponto)</span>
            </label>
          </div>
        </div>

        {/* Duplicate Policy */}
        <div>
          <label className="block text-gray-300 font-semibold mb-2">
            Política de Duplicatas (TARGET)
          </label>
          <select
            value={options.targetDuplicatePolicy}
            onChange={(e) => handleOptionChange('targetDuplicatePolicy', e.target.value)}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="keep_last">Manter última</option>
            <option value="sum">Somar valores</option>
            <option value="mean">Média dos valores</option>
          </select>
        </div>
      </div>
    </div>
  );
};

ColumnMapping.propTypes = {
  columns: PropTypes.array.isRequired,
  mapping: PropTypes.shape({
    keyColumns: PropTypes.array.isRequired,
    valueColumns: PropTypes.array.isRequired
  }).isRequired,
  onMappingChange: PropTypes.func.isRequired,
  options: PropTypes.object.isRequired,
  onOptionsChange: PropTypes.func.isRequired
};

export default ColumnMapping;
