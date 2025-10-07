import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Upload, TrendingUp, AlertCircle, CheckCircle, Activity, Database } from 'lucide-react';
import { motion } from 'framer-motion';
import { fadeIn, staggerContainer } from '../styles/animations';

const DatasetMetrics = () => {
  // State
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Refs
  const fileInputRef = useRef(null);

  // Focus management
  useEffect(() => {
    document.title = 'Dataset Metrics - DataForgeTest';
  }, []);

  // Handle file selection
  const handleFileChange = (selectedFile) => {
    if (!selectedFile) return;

    // Validate file type
    const validTypes = ['.csv', '.xlsx', '.xls', '.parquet'];
    const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase();
    
    if (!validTypes.includes(fileExt)) {
      setError(`Tipo de arquivo inválido. Tipos permitidos: ${validTypes.join(', ')}`);
      return;
    }

    setFile(selectedFile);
    setError(null);
    setReport(null);
  };

  // Handle file input change
  const handleInputChange = (e) => {
    const selectedFile = e.target.files[0];
    handleFileChange(selectedFile);
  };

  // Handle drag and drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  // Upload file
  const uploadFile = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/metrics/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      setSessionId(data.sessionId);
      
      // Automatically start analysis
      analyzeDataset(data.sessionId);
    } catch (err) {
      setError(err.message);
      setIsUploading(false);
    }
  };

  // Analyze dataset
  const analyzeDataset = async (sid = sessionId) => {
    if (!sid) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('/api/metrics/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId: sid }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
      setIsAnalyzing(false);
    }
  };

  // Reset state
  const reset = () => {
    setFile(null);
    setSessionId(null);
    setReport(null);
    setError(null);
    setIsUploading(false);
    setIsAnalyzing(false);
  };

  // Get quality score color
  const getQualityColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Get severity color
  const getSeverityColor = (severity) => {
    if (severity === 'high') return 'text-red-400';
    if (severity === 'medium') return 'text-yellow-400';
    return 'text-blue-400';
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#1a1a2e] text-white py-12 px-6"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div variants={fadeIn} className="mb-8">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Voltar para Home
          </Link>
          <h1 className="text-4xl font-bold mb-2">
            Métricas de Qualidade de Dados
          </h1>
          <p className="text-gray-300 text-lg">
            Analise a qualidade do seu dataset e obtenha métricas detalhadas sobre completude, unicidade, validade e consistência
          </p>
        </motion.div>

        {/* Error Alert */}
        {error && (
          <motion.div
            variants={fadeIn}
            className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-xl flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-200">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-300"
              aria-label="Fechar alerta"
            >
              ×
            </button>
          </motion.div>
        )}

        {/* Upload Section */}
        {!report && (
          <motion.div variants={fadeIn} className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700/50 mb-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Upload className="w-6 h-6 text-purple-400" />
              Upload do Dataset
            </h2>

            {!file ? (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
                  dragActive
                    ? 'border-purple-500 bg-purple-500/10'
                    : 'border-gray-600 hover:border-purple-500'
                }`}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-300 text-lg mb-2">
                  Arraste seu dataset aqui ou clique para selecionar
                </p>
                <p className="text-gray-500 text-sm mb-4">
                  Formatos suportados: CSV, XLSX, XLS, Parquet (máx 50MB)
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls,.parquet"
                  onChange={handleInputChange}
                  className="hidden"
                  aria-label="Selecionar arquivo"
                />
                <button
                  type="button"
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-semibold transition-colors"
                >
                  Selecionar Arquivo
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Database className="w-8 h-8 text-purple-400" />
                    <div>
                      <p className="text-white font-medium">{file.name}</p>
                      <p className="text-gray-400 text-sm">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={reset}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    Remover
                  </button>
                </div>

                <button
                  onClick={uploadFile}
                  disabled={isUploading || isAnalyzing}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isUploading || isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      {isUploading ? 'Enviando...' : 'Analisando...'}
                    </>
                  ) : (
                    <>
                      <Activity className="w-5 h-5" />
                      Analisar Dataset
                    </>
                  )}
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Results Section */}
        {report && (
          <motion.div variants={fadeIn} className="space-y-6">
            {/* Overall Quality Score */}
            <div className="bg-gradient-to-br from-purple-900/40 to-pink-900/40 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/50">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-white mb-4">Score Geral de Qualidade</h2>
                <div className={`text-7xl font-bold ${getQualityColor(report.overall_quality_score)} mb-2`}>
                  {report.overall_quality_score.toFixed(1)}%
                </div>
                <p className="text-gray-300">
                  {report.overall_quality_score >= 90 ? 'Excelente qualidade!' :
                   report.overall_quality_score >= 70 ? 'Boa qualidade, mas há espaço para melhorias' :
                   'Qualidade necessita atenção'}
                </p>
              </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Completeness */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Completude</h3>
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <div className={`text-4xl font-bold ${getQualityColor(report.metrics.completeness.overall_completeness)} mb-2`}>
                  {report.metrics.completeness.overall_completeness}%
                </div>
                <p className="text-gray-400 text-sm">
                  {report.metrics.completeness.filled_cells} de {report.metrics.completeness.total_cells} células preenchidas
                </p>
              </div>

              {/* Uniqueness */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Unicidade</h3>
                  <TrendingUp className="w-6 h-6 text-blue-400" />
                </div>
                <div className={`text-4xl font-bold ${getQualityColor(report.metrics.uniqueness.overall_uniqueness)} mb-2`}>
                  {report.metrics.uniqueness.overall_uniqueness}%
                </div>
                <p className="text-gray-400 text-sm">
                  {report.metrics.uniqueness.duplicate_rows} linhas duplicadas
                </p>
              </div>

              {/* Validity */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Validade</h3>
                  <AlertCircle className="w-6 h-6 text-yellow-400" />
                </div>
                <div className={`text-4xl font-bold ${getQualityColor(report.metrics.validity.overall_validity)} mb-2`}>
                  {report.metrics.validity.overall_validity}%
                </div>
                <p className="text-gray-400 text-sm">
                  {report.metrics.validity.invalid_cells} valores inválidos
                </p>
              </div>

              {/* Consistency */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Consistência</h3>
                  <Activity className="w-6 h-6 text-purple-400" />
                </div>
                <div className={`text-4xl font-bold ${getQualityColor(report.metrics.consistency.overall_consistency)} mb-2`}>
                  {report.metrics.consistency.overall_consistency.toFixed(1)}%
                </div>
                <p className="text-gray-400 text-sm">
                  Formatação e padrões dos dados
                </p>
              </div>
            </div>

            {/* Dataset Info */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
              <h3 className="text-xl font-bold text-white mb-4">Informações do Dataset</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-1">Total de Linhas</p>
                  <p className="text-2xl font-bold text-white">{report.metrics.dataset_info.rows.toLocaleString()}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-1">Total de Colunas</p>
                  <p className="text-2xl font-bold text-white">{report.metrics.dataset_info.columns}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-1">Uso de Memória</p>
                  <p className="text-2xl font-bold text-white">{report.metrics.dataset_info.memory_usage_mb} MB</p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {report.recommendations && report.recommendations.length > 0 && (
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
                <h3 className="text-xl font-bold text-white mb-4">Recomendações</h3>
                <div className="space-y-3">
                  {report.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-4 bg-gray-900/50 rounded-lg border border-gray-700/30"
                    >
                      <AlertCircle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${getSeverityColor(rec.severity)}`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs font-semibold uppercase ${getSeverityColor(rec.severity)}`}>
                            {rec.severity === 'high' ? 'Alta' : rec.severity === 'medium' ? 'Média' : 'Baixa'}
                          </span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-400">{rec.category}</span>
                        </div>
                        <p className="text-gray-300">{rec.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={reset}
                className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white font-semibold transition-colors"
              >
                Analisar Novo Dataset
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default DatasetMetrics;
