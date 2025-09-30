import React, { useState } from 'react';
import { Zap, Code, Bug, CheckCircle, AlertTriangle, FileText, GitCompare, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { fadeIn, staggerContainer, slideIn, scaleIn } from '../styles/animations';

const DataQualityLLMSystem = ({ onStartChat }) => {
  const [selectedStructure, setSelectedStructure] = useState('synthetic');

  const structures = {
    synthetic: {
      title: 'SyntheticDataset',
      icon: Zap,
      color: 'bg-purple-500',
      description: 'Dataset gerado pela LLM com erros propositais',
      fields: [
        { name: 'dataset_id', type: 'UUID', desc: 'Identificador único do dataset' },
        { name: 'schema', type: 'Map<String, DataType>', desc: 'Schema dos dados (nome_campo → tipo)' },
        { name: 'data', type: 'List<Map<String, Any>>', desc: 'Registros do dataset (formato JSON/Dict)' },
        { name: 'row_count', type: 'Integer', desc: 'Total de linhas geradas' },
        { name: 'generation_prompt', type: 'String', desc: 'Prompt usado para gerar o dataset' },
        { name: 'created_at', type: 'Timestamp', desc: 'Quando foi gerado' }
      ]
    },
    problems: {
      title: 'ExpectedProblems',
      icon: Bug,
      color: 'bg-red-500',
      description: 'Documentação dos problemas injetados pela LLM',
      fields: [
        { name: 'dataset_id', type: 'UUID', desc: 'Referência ao dataset' },
        { name: 'problems', type: 'List<Problem>', desc: 'Lista de problemas injetados' },
        { name: 'total_issues', type: 'Integer', desc: 'Contagem total de problemas' },
        { name: 'issue_distribution', type: 'Map<ProblemType, Integer>', desc: 'Quantos de cada tipo' },
        { name: 'description', type: 'String', desc: 'Descrição geral dos problemas' }
      ]
    },
    problem: {
      title: 'Problem',
      icon: AlertTriangle,
      color: 'bg-orange-500',
      description: 'Detalhes de um problema específico injetado',
      fields: [
        { name: 'problem_id', type: 'UUID', desc: 'ID do problema' },
        { name: 'problem_type', type: 'Enum', desc: 'NULL_VALUE, DUPLICATE, OUT_OF_RANGE, INVALID_FORMAT, INCONSISTENT, MISSING_FK, WRONG_TYPE' },
        { name: 'field_name', type: 'String', desc: 'Campo afetado' },
        { name: 'affected_rows', type: 'List<Integer>', desc: 'Índices das linhas com problema' },
        { name: 'description', type: 'String', desc: 'Descrição do problema' },
        { name: 'severity', type: 'Enum', desc: 'CRITICAL, HIGH, MEDIUM, LOW' },
        { name: 'expected_detection', type: 'String', desc: 'Como deve ser detectado' }
      ]
    },
    pysparkcode: {
      title: 'GeneratedPySparkCode',
      icon: Code,
      color: 'bg-blue-500',
      description: 'Código PySpark gerado pela segunda LLM',
      fields: [
        { name: 'code_id', type: 'UUID', desc: 'ID do código gerado' },
        { name: 'dataset_id', type: 'UUID', desc: 'Dataset alvo' },
        { name: 'source_code', type: 'String', desc: 'Código PySpark completo' },
        { name: 'validation_functions', type: 'List<String>', desc: 'Funções de validação criadas' },
        { name: 'generation_prompt', type: 'String', desc: 'Prompt usado para gerar o código' },
        { name: 'created_at', type: 'Timestamp', desc: 'Quando foi gerado' },
        { name: 'dependencies', type: 'List<String>', desc: 'Bibliotecas necessárias' }
      ]
    },
    validationlog: {
      title: 'ValidationLog',
      icon: FileText,
      color: 'bg-green-500',
      description: 'Logs produzidos pela execução do PySpark',
      fields: [
        { name: 'execution_id', type: 'UUID', desc: 'ID da execução' },
        { name: 'dataset_id', type: 'UUID', desc: 'Dataset validado' },
        { name: 'code_id', type: 'UUID', desc: 'Código executado' },
        { name: 'detected_issues', type: 'List<DetectedIssue>', desc: 'Problemas detectados' },
        { name: 'execution_time_ms', type: 'Long', desc: 'Tempo de execução' },
        { name: 'total_rows_processed', type: 'Long', desc: 'Linhas processadas' },
        { name: 'status', type: 'Enum', desc: 'SUCCESS, FAILED, PARTIAL' },
        { name: 'raw_logs', type: 'String', desc: 'Logs completos da execução' }
      ]
    },
    detectedissue: {
      title: 'DetectedIssue',
      icon: AlertTriangle,
      color: 'bg-yellow-500',
      description: 'Problema detectado pelo código PySpark',
      fields: [
        { name: 'issue_id', type: 'UUID', desc: 'ID do problema detectado' },
        { name: 'issue_type', type: 'String', desc: 'Tipo identificado pelo código' },
        { name: 'field_name', type: 'String', desc: 'Campo problemático' },
        { name: 'affected_rows', type: 'List<Integer>', desc: 'Linhas afetadas encontradas' },
        { name: 'description', type: 'String', desc: 'Descrição gerada pelo código' },
        { name: 'severity', type: 'String', desc: 'Gravidade detectada' },
        { name: 'detection_method', type: 'String', desc: 'Método usado para detectar' }
      ]
    },
    comparison: {
      title: 'ComparisonResult',
      icon: GitCompare,
      color: 'bg-teal-500',
      description: 'Comparação: problemas esperados vs detectados',
      fields: [
        { name: 'comparison_id', type: 'UUID', desc: 'ID da comparação' },
        { name: 'dataset_id', type: 'UUID', desc: 'Dataset testado' },
        { name: 'true_positives', type: 'Integer', desc: 'Problemas corretamente detectados' },
        { name: 'false_positives', type: 'Integer', desc: 'Falsos alarmes' },
        { name: 'false_negatives', type: 'Integer', desc: 'Problemas não detectados' },
        { name: 'precision', type: 'Float', desc: 'TP / (TP + FP)' },
        { name: 'recall', type: 'Float', desc: 'TP / (TP + FN)' },
        { name: 'f1_score', type: 'Float', desc: 'Métrica harmônica' },
        { name: 'matching_details', type: 'List<Match>', desc: 'Detalhes de cada match' }
      ]
    },
    match: {
      title: 'Match',
      icon: CheckCircle,
      color: 'bg-emerald-500',
      description: 'Match entre problema esperado e detectado',
      fields: [
        { name: 'expected_problem_id', type: 'UUID', desc: 'ID do problema esperado' },
        { name: 'detected_issue_id', type: 'UUID', desc: 'ID do problema detectado' },
        { name: 'match_type', type: 'Enum', desc: 'EXACT, PARTIAL, NONE' },
        { name: 'field_match', type: 'Boolean', desc: 'Campo bateu?' },
        { name: 'type_match', type: 'Boolean', desc: 'Tipo bateu?' },
        { name: 'rows_overlap', type: 'Float', desc: '% de sobreposição nas linhas' },
        { name: 'confidence_score', type: 'Float', desc: 'Confiança do match (0-1)' }
      ]
    }
  };

  const StructureIcon = structures[selectedStructure].icon;

  return (
    <motion.div 
      initial="initial"
      animate="animate"
      className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white overflow-x-hidden"
    >
      {/* Hero Section */}
      <motion.div 
        variants={fadeIn}
        className="relative pt-20 pb-32 px-6"
      >
        <div className="max-w-7xl mx-auto text-center">
          <motion.h1 
            variants={slideIn}
            className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600"
          >
            Sistema LLM para
            <br />
            Qualidade de Dados
          </motion.h1>
          <motion.p 
            variants={fadeIn}
            className="text-xl md:text-2xl text-purple-300 mb-8"
          >
            Geração inteligente de datasets com erros + validação automática com PySpark
          </motion.p>
          <motion.button
            variants={scaleIn}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onStartChat}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-semibold text-lg shadow-lg hover:shadow-purple-500/30 transition-all duration-300 flex items-center mx-auto gap-2"
          >
            Iniciar Validação <ArrowRight className="w-5 h-5" />
          </motion.button>
        </div>

        {/* Floating Badges */}
        <div className="absolute top-40 left-10 animate-float-slow">
          <div className="bg-purple-900/30 backdrop-blur-sm p-3 rounded-lg border border-purple-700/30">
            <Bug className="w-6 h-6 text-purple-400" />
          </div>
        </div>
        <div className="absolute top-60 right-20 animate-float-slower">
          <div className="bg-pink-900/30 backdrop-blur-sm p-3 rounded-lg border border-pink-700/30">
            <Code className="w-6 h-6 text-pink-400" />
          </div>
        </div>
      </motion.div>

      {/* Navigation */}
      <motion.div 
        variants={staggerContainer}
        className="max-w-7xl mx-auto px-6 mb-12"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(structures).map(([key, struct]) => {
            const Icon = struct.icon;
            return (
              <motion.button
                key={key}
                variants={fadeIn}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setSelectedStructure(key)}
                className={`p-6 rounded-xl transition-all ${
                  selectedStructure === key
                    ? `${struct.color} shadow-lg shadow-purple-500/20`
                    : 'bg-gray-800/50 hover:bg-gray-800 border border-gray-700'
                }`}
              >
                <Icon className="w-8 h-8 text-white mx-auto mb-3" />
                <div className="text-sm font-medium text-center">
                  {struct.title}
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>

      {/* Selected Structure Details */}
      <motion.div 
        variants={fadeIn}
        className="max-w-7xl mx-auto px-6"
      >
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-gray-700/50">
          <div className="flex items-start gap-6 mb-8">
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className={`p-4 rounded-xl ${structures[selectedStructure].color}`}
            >
              <StructureIcon className="w-12 h-12 text-white" />
            </motion.div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                {structures[selectedStructure].title}
              </h2>
              <p className="text-purple-300 text-lg">
                {structures[selectedStructure].description}
              </p>
            </div>
          </div>

          <motion.div 
            variants={staggerContainer}
            className="space-y-4"
          >
            {structures[selectedStructure].fields.map((field, idx) => (
              <motion.div
                key={idx}
                variants={fadeIn}
                whileHover={{ scale: 1.01 }}
                className="bg-gray-900/50 rounded-xl p-6 hover:bg-gray-900/70 transition-colors border border-gray-700/50"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <code className="text-purple-400 font-mono font-semibold text-lg">
                        {field.name}
                      </code>
                      <span className="px-3 py-1 bg-gray-800 rounded-full text-xs font-medium text-emerald-400 border border-emerald-900/30">
                        {field.type}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {field.desc}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Workflow Section */}
        <motion.div 
          variants={fadeIn}
          className="mt-12 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700/50"
        >
          <h3 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
            <Zap className="text-yellow-400" />
            Fluxo do Sistema
          </h3>
          <div className="space-y-8">
            <motion.div 
              variants={slideIn}
              className="flex items-start gap-6"
            >
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl w-14 h-14 flex items-center justify-center flex-shrink-0 text-white font-bold text-xl shadow-lg shadow-purple-500/20">
                1
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-white mb-2">LLM 1: Geração do Dataset</h4>
                <p className="text-gray-300">
                  Cria <code className="text-purple-400 font-mono">SyntheticDataset</code> + 
                  <code className="text-red-400 font-mono ml-1">ExpectedProblems</code> documentando cada erro injetado
                </p>
              </div>
            </motion.div>

            <motion.div 
              variants={slideIn}
              className="flex items-start gap-6"
            >
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl w-14 h-14 flex items-center justify-center flex-shrink-0 text-white font-bold text-xl shadow-lg shadow-blue-500/20">
                2
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-white mb-2">LLM 2: Geração do Código</h4>
                <p className="text-gray-300">
                  Recebe apenas o dataset e gera <code className="text-blue-400 font-mono">GeneratedPySparkCode</code> para detectar problemas
                </p>
              </div>
            </motion.div>

            <motion.div 
              variants={slideIn}
              className="flex items-start gap-6"
            >
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl w-14 h-14 flex items-center justify-center flex-shrink-0 text-white font-bold text-xl shadow-lg shadow-green-500/20">
                3
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-white mb-2">Execução & Logs</h4>
                <p className="text-gray-300">
                  Roda o PySpark e gera <code className="text-green-400 font-mono">ValidationLog</code> com 
                  <code className="text-yellow-400 font-mono ml-1">DetectedIssue</code> para cada problema encontrado
                </p>
              </div>
            </motion.div>

            <motion.div 
              variants={slideIn}
              className="flex items-start gap-6"
            >
              <div className="bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl w-14 h-14 flex items-center justify-center flex-shrink-0 text-white font-bold text-xl shadow-lg shadow-teal-500/20">
                4
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-white mb-2">Comparação & Score</h4>
                <p className="text-gray-300">
                  Compara <code className="text-red-400 font-mono">ExpectedProblems</code> vs 
                  <code className="text-yellow-400 font-mono ml-1">DetectedIssues</code> gerando 
                  <code className="text-teal-400 font-mono ml-1">ComparisonResult</code> com precisão/recall
                </p>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Problem Types Section */}
        <motion.div 
          variants={fadeIn}
          className="mt-12 bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-sm rounded-2xl p-8 border border-purple-700/50"
        >
          <h3 className="text-2xl font-bold text-white mb-6">🎯 Tipos de Problemas para Injetar</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div 
              variants={slideIn}
              className="bg-black/20 backdrop-blur-sm rounded-xl p-6 border border-purple-700/30"
            >
              <h4 className="text-xl font-bold text-purple-300 mb-4">Problemas de Dados</h4>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  <strong>NULL_VALUE:</strong> Valores nulos em campos obrigatórios
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  <strong>DUPLICATE:</strong> Registros duplicados completos ou parciais
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  <strong>OUT_OF_RANGE:</strong> Valores fora do range esperado
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  <strong>INVALID_FORMAT:</strong> Formato incorreto (email, CPF, data)
                </li>
              </ul>
            </motion.div>

            <motion.div 
              variants={slideIn}
              className="bg-black/20 backdrop-blur-sm rounded-xl p-6 border border-pink-700/30"
            >
              <h4 className="text-xl font-bold text-pink-300 mb-4">Problemas de Integridade</h4>
              <ul className="space-y-3 text-gray-200">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full"></span>
                  <strong>INCONSISTENT:</strong> Dados contraditórios entre campos
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full"></span>
                  <strong>MISSING_FK:</strong> Foreign key sem referência
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full"></span>
                  <strong>WRONG_TYPE:</strong> Tipo de dado incorreto
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full"></span>
                  <strong>OUTLIER:</strong> Valores estatisticamente anormais
                </li>
              </ul>
            </motion.div>
          </div>
        </motion.div>

        {/* Implementation Tips */}
        <motion.div 
          variants={fadeIn}
          className="mt-12 mb-20 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700/50"
        >
          <h3 className="text-2xl font-bold text-white mb-6">💡 Dicas de Implementação</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div 
              variants={slideIn}
              className="space-y-4"
            >
              {/*
                "Use fuzzy matching para comparar descrições esperadas vs detectadas",
                "Implemente tolerance para índices de linhas (±N linhas é aceitável)",
                "Armazene os prompts usados para reprodutibilidade"
              */}
              {["Use fuzzy matching para comparar descrições esperadas vs detectadas",
                "Implemente tolerance para índices de linhas (±N linhas é aceitável)",
                "Armazene os prompts usados para reprodutibilidade"
              ].map((tip, idx) => (
                <div key={idx} className="flex items-start gap-3 bg-gray-900/30 p-4 rounded-lg border border-gray-700/30">
                  <div className="w-8 h-8 bg-purple-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-5 h-5 text-purple-400" />
                  </div>
                  <p className="text-gray-300">{tip}</p>
                </div>
              ))}
            </motion.div>
            <motion.div 
              variants={slideIn}
              className="space-y-4"
            >
              {/*
                "Crie um benchmark suite com datasets de diferentes complexidades",
                "Use embeddings para comparar semanticamente os tipos de problemas",
                "Mantenha versionamento dos datasets e códigos gerados"
              */}
              {["Crie um benchmark suite com datasets de diferentes complexidades",
                "Use embeddings para comparar semanticamente os tipos de problemas",
                "Mantenha versionamento dos datasets e códigos gerados"
              ].map((tip, idx) => (
                <div key={idx} className="flex items-start gap-3 bg-gray-900/30 p-4 rounded-lg border border-gray-700/30">
                  <div className="w-8 h-8 bg-pink-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-5 h-5 text-pink-400" />
                  </div>
                  <p className="text-gray-300">{tip}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default DataQualityLLMSystem;
