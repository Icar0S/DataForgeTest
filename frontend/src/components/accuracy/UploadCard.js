import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { Upload, FileText, X } from 'lucide-react';

const UploadCard = ({ role, title, file, onFileSelect, onRemove, preview, isLoading }) => {
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      onFileSelect(droppedFile);
    }
  }, [onFileSelect]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const handleFileInput = useCallback((e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  }, [onFileSelect]);

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">{title}</h3>
        {file && (
          <button
            onClick={onRemove}
            className="text-red-400 hover:text-red-300 transition-colors"
            aria-label={`Remove ${title}`}
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {!file ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-purple-500 transition-colors cursor-pointer"
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-300 mb-2">Arraste e solte o arquivo aqui</p>
          <p className="text-gray-500 text-sm mb-4">ou</p>
          <label className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-semibold cursor-pointer transition-colors inline-block">
            Selecionar Arquivo
            <input
              type="file"
              accept=".csv,.xlsx,.parquet"
              onChange={handleFileInput}
              className="hidden"
              aria-label={`Select file for ${title}`}
            />
          </label>
          <p className="text-gray-500 text-xs mt-4">Tipos aceitos: CSV, XLSX, Parquet</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-gray-900/50 rounded-lg">
            <FileText className="w-8 h-8 text-purple-400" />
            <div className="flex-1">
              <p className="text-white font-medium">{file.name}</p>
              <p className="text-gray-400 text-sm">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>

          {isLoading && (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
              <p className="ml-3 text-gray-300">Carregando preview...</p>
            </div>
          )}

          {preview && preview.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-white font-semibold">Preview (primeiras 20 linhas)</h4>
              <div className="overflow-x-auto max-h-96 rounded-lg border border-gray-700">
                <table className="w-full text-sm">
                  <thead className="bg-gray-900/80 sticky top-0">
                    <tr>
                      {Object.keys(preview[0]).map((col) => (
                        <th key={col} className="px-4 py-2 text-left text-purple-400 font-semibold">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="text-gray-300">
                    {preview.map((row, idx) => (
                      <tr key={idx} className="border-t border-gray-700/50 hover:bg-gray-800/30">
                        {Object.values(row).map((val, colIdx) => (
                          <td key={colIdx} className="px-4 py-2">
                            {val === null || val === undefined ? (
                              <span className="text-gray-500 italic">null</span>
                            ) : (
                              val.toString()
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

UploadCard.propTypes = {
  role: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  file: PropTypes.object,
  onFileSelect: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired,
  preview: PropTypes.array,
  isLoading: PropTypes.bool
};

export default UploadCard;
