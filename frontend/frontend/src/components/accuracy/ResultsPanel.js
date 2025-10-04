import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Download, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

const ResultsPanel = ({ summary, differences, downloadLinks, onDownload }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 10;

  if (!summary) {
    return null;
  }

  const totalPages = Math.ceil(differences.length / rowsPerPage);
  const startIdx = currentPage * rowsPerPage;
  const endIdx = startIdx + rowsPerPage;
  const currentDiffs = differences.slice(startIdx, endIdx);

  return (
    <div className="space-y-6">
      {/* Summary Metrics */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-purple-400" />
          Resumo da Comparação
        </h3>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Linhas GOLD</p>
            <p className="text-2xl font-bold text-white">{summary.rows_gold}</p>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Linhas TARGET</p>
            <p className="text-2xl font-bold text-white">{summary.rows_target}</p>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Chaves Comuns</p>
            <p className="text-2xl font-bold text-white">{summary.common_keys}</p>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Ausentes no TARGET</p>
            <p className="text-2xl font-bold text-orange-400">{summary.missing_in_target}</p>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Extras no TARGET</p>
            <p className="text-2xl font-bold text-blue-400">{summary.extra_in_target}</p>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Divergências</p>
            <p className="text-2xl font-bold text-red-400">{summary.mismatches_total}</p>
          </div>
        </div>

        {/* Accuracy */}
        <div className="mt-6 bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-lg p-6 border border-purple-700/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-gray-300 text-sm">Acurácia dos Dados</p>
                <p className="text-3xl font-bold text-white">
                  {(summary.accuracy * 100).toFixed(2)}%
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-sm">Matches exatos / Total comparado</p>
              <p className="text-gray-300">
                {summary.common_keys - summary.mismatches_total} / {summary.common_keys}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Differences Table */}
      {differences && differences.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-orange-400" />
            Diferenças Detectadas ({differences.length})
          </h3>

          <div className="overflow-x-auto rounded-lg border border-gray-700">
            <table className="w-full text-sm">
              <thead className="bg-gray-900/80">
                <tr>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">Chaves</th>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">Coluna</th>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">GOLD</th>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">TARGET Original</th>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">Corrigido</th>
                  <th className="px-4 py-3 text-left text-purple-400 font-semibold">Delta</th>
                </tr>
              </thead>
              <tbody className="text-gray-300">
                {currentDiffs.map((diff, idx) => (
                  <tr key={idx} className="border-t border-gray-700/50 hover:bg-gray-800/30">
                    <td className="px-4 py-3">
                      <div className="text-xs">
                        {Object.entries(diff.keys || {}).map(([key, value]) => (
                          <div key={key}>
                            <span className="text-gray-500">{key}:</span> {value}
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-pink-400">{diff.column}</td>
                    <td className="px-4 py-3 font-mono text-green-400">
                      {diff.gold !== null && diff.gold !== undefined ? diff.gold.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-mono text-red-400">
                      {diff.target !== null && diff.target !== undefined ? diff.target.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-mono text-blue-400">
                      {diff.corrected !== null && diff.corrected !== undefined ? diff.corrected.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-mono text-orange-400">
                      {diff.delta !== null && diff.delta !== undefined ? diff.delta.toFixed(2) : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-gray-400 text-sm">
                Mostrando {startIdx + 1}-{Math.min(endIdx, differences.length)} de {differences.length}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                  disabled={currentPage === 0}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg transition-colors"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                  disabled={currentPage >= totalPages - 1}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg transition-colors"
                >
                  Próximo
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Download Buttons */}
      {downloadLinks && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Download className="w-6 h-6 text-purple-400" />
            Downloads
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => onDownload(downloadLinks.correctedCsv)}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 rounded-lg text-white font-semibold transition-all duration-300 flex items-center justify-center gap-2"
              aria-label="Baixar dataset corrigido"
            >
              <Download className="w-5 h-5" />
              Dataset Corrigido (.csv)
            </button>
            <button
              onClick={() => onDownload(downloadLinks.diffCsv)}
              className="px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 rounded-lg text-white font-semibold transition-all duration-300 flex items-center justify-center gap-2"
              aria-label="Baixar relatório de diferenças"
            >
              <Download className="w-5 h-5" />
              Diferenças (.csv)
            </button>
            <button
              onClick={() => onDownload(downloadLinks.reportJson)}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-lg text-white font-semibold transition-all duration-300 flex items-center justify-center gap-2"
              aria-label="Baixar relatório JSON"
            >
              <Download className="w-5 h-5" />
              Relatório (.json)
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

ResultsPanel.propTypes = {
  summary: PropTypes.shape({
    rows_gold: PropTypes.number,
    rows_target: PropTypes.number,
    common_keys: PropTypes.number,
    missing_in_target: PropTypes.number,
    extra_in_target: PropTypes.number,
    mismatches_total: PropTypes.number,
    accuracy: PropTypes.number
  }),
  differences: PropTypes.array,
  downloadLinks: PropTypes.shape({
    correctedCsv: PropTypes.string,
    diffCsv: PropTypes.string,
    reportJson: PropTypes.string
  }),
  onDownload: PropTypes.func.isRequired
};

export default ResultsPanel;
