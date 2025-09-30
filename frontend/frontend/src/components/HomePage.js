import React, { useState } from 'react';
import { Zap, Code, Bug, CheckCircle, AlertTriangle, FileText, GitCompare } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Sistema LLM para Qualidade de Dados
          </h1>
          <p className="text-purple-300">Geração de datasets com erros + validação automática com PySpark</p>
          <button
            onClick={onStartChat}
            className="mt-4 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
          >
            Iniciar Chat de Validação
          </button>
        </div>

        {/* Navigation */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {Object.entries(structures).map(([key, struct]) => {
            const Icon = struct.icon;
            return (
              <button
                key={key}
                onClick={() => setSelectedStructure(key)}
                className={`p-4 rounded-lg transition-all transform hover:scale-105 ${
                  selectedStructure === key
                    ? `${struct.color} shadow-lg shadow-purple-500/50`
                    : 'bg-gray-800 hover:bg-gray-700 border border-gray-700'
                }`}
              >
                <Icon className="w-8 h-8 text-white mx-auto mb-2" />
                <div className="text-white text-xs font-semibold text-center">
                  {struct.title}
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected Structure Details */}
        <div className="bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
          <div className="flex items-center gap-4 mb-6">
            <div className={`p-4 rounded-lg ${structures[selectedStructure].color}`}>
              <StructureIcon className="w-10 h-10 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">
                {structures[selectedStructure].title}
              </h2>
              <p className="text-purple-300 mt-1">
                {structures[selectedStructure].description}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {structures[selectedStructure].fields.map((field, idx) => (
              <div
                key={idx}
                className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors border border-gray-600"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <code className="text-purple-400 font-mono font-semibold text-lg">
                        {field.name}
                      </code>
                      <span className="px-3 py-1 bg-gray-600 rounded-full text-xs font-medium text-emerald-400">
                        {field.type}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm">{field.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Workflow */}
        <div className="mt-8 bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <Zap className="text-yellow-400" />
            Fluxo do Sistema
          </h3>
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="bg-purple-500 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 text-white font-bold">
                1
              </div>
              <div className="flex-1">
                <h4 className="text-white font-bold mb-1">LLM 1: Geração do Dataset</h4>
                <p className="text-gray-300 text-sm">Cria <code className="text-purple-400">SyntheticDataset</code> + <code className="text-red-400">ExpectedProblems</code> documentando cada erro injetado</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-blue-500 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 text-white font-bold">
                2
              </div>
              <div className="flex-1">
                <h4 className="text-white font-bold mb-1">LLM 2: Geração do Código</h4>
                <p className="text-gray-300 text-sm">Recebe apenas o dataset e gera <code className="text-blue-400">GeneratedPySparkCode</code> para detectar problemas</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-green-500 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 text-white font-bold">
                3
              </div>
              <div className="flex-1">
                <h4 className="text-white font-bold mb-1">Execução & Logs</h4>
                <p className="text-gray-300 text-sm">Roda o PySpark e gera <code className="text-green-400">ValidationLog</code> com <code className="text-yellow-400">DetectedIssue</code> para cada problema encontrado</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-teal-500 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 text-white font-bold">
                4
              </div>
              <div className="flex-1">
                <h4 className="text-white font-bold mb-1">Comparação & Score</h4>
                <p className="text-gray-300 text-sm">Compara <code className="text-red-400">ExpectedProblems</code> vs <code className="text-yellow-400">DetectedIssues</code> gerando <code className="text-teal-400">ComparisonResult</code> com precisão/recall</p>
              </div>
            </div>
          </div>
        </div>

        {/* Example Types */}
        <div className="mt-8 bg-gradient-to-r from-purple-900 to-pink-900 rounded-xl p-6 border border-purple-700">
          <h3 className="text-xl font-bold text-white mb-4">🎯 Tipos de Problemas para Injetar</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-purple-300 font-bold mb-2">Problemas de Dados</h4>
              <ul className="space-y-1 text-gray-200 text-sm">
                <li>• <strong>NULL_VALUE:</strong> Valores nulos em campos obrigatórios</li>
                <li>• <strong>DUPLICATE:</strong> Registros duplicados completos ou parciais</li>
                <li>• <strong>OUT_OF_RANGE:</strong> Valores fora do range esperado</li>
                <li>• <strong>INVALID_FORMAT:</strong> Formato incorreto (email, CPF, data)</li>
              </ul>
            </div>
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-pink-300 font-bold mb-2">Problemas de Integridade</h4>
              <ul className="space-y-1 text-gray-200 text-sm">
                <li>• <strong>INCONSISTENT:</strong> Dados contraditórios entre campos</li>
                <li>• <strong>MISSING_FK:</strong> Foreign key sem referência</li>
                <li>• <strong>WRONG_TYPE:</strong> Tipo de dado incorreto</li>
                <li>• <strong>OUTLIER:</strong> Valores estatisticamente anormais</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Implementation Tips */}
        <div className="mt-8 bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">💡 Dicas de Implementação</h3>
          <ul className="space-y-2 text-gray-300 text-sm">
            <li>• Use <strong>fuzzy matching</strong> para comparar descrições esperadas vs detectadas</li>
            <li>• Implemente <strong>tolerance</strong> para índices de linhas (±N linhas é aceitável)</li>
            <li>• Armazene os <strong>prompts usados</strong> para reprodutibilidade</li>
            <li>• Crie um <strong>benchmark suite</strong> com datasets de diferentes complexidades</li>
            <li>• Use <strong>embeddings</strong> para comparar semanticamente os tipos de problemas</li>
            <li>• Mantenha <strong>versionamento</strong> dos datasets e códigos gerados</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DataQualityLLMSystem;
