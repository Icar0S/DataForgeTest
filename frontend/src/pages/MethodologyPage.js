import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Lightbulb, 
  FileText, 
  Database, 
  Target, 
  BarChart3,
  Brain,
  BookOpen,
  ArrowRight,
  CheckCircle
} from 'lucide-react';
import { fadeIn, slideIn, staggerContainer } from '../styles/animations';

const MethodologyPage = () => {
  const phases = [
    {
      number: 1,
      title: 'Planejamento e Definição Estratégica',
      icon: FileText,
      iconColor: 'text-blue-400',
      entrada: 'Requisitos de Negócio e Governança',
      processoA: 'Definição de Metas e Critérios de Aceite',
      processoB: 'Modelagem do Cenário de Teste',
      saida: 'Plano de Testes, Regras de Validação e Checklist de QA',
      suporteIA: 'Sugestão de regras de validação baseadas em histórico ou padrões da indústria'
    },
    {
      number: 2,
      title: 'Mapeamento e Preparação de Fontes',
      icon: Database,
      iconColor: 'text-green-400',
      entrada: 'Plano de Testes aprovado',
      processoA: 'Inventário e Mapeamento de Metadados',
      processoB: 'Definição de Políticas de Tratamento (LGPD)',
      saida: 'Catálogos de Dados Mapeados e Matriz De-Para',
      suporteIA: 'Identificação automática de padrões e anomalias nos metadados'
    },
    {
      number: 3,
      title: 'Geração e Execução de Cenários',
      icon: Target,
      iconColor: 'text-purple-400',
      entrada: 'Fontes de Dados Mapeadas',
      processoA: 'Geração de Dados Sintéticos Realistas',
      processoB: 'Execução do Motor de Validação em Big Data',
      saida: 'Logs de Execução e Datasets Validados',
      suporteIA: 'Auxílio na criação de prompts para gerar dados sintéticos complexos'
    },
    {
      number: 4,
      title: 'Análise de Resultados e Monitoramento',
      icon: BarChart3,
      iconColor: 'text-orange-400',
      entrada: 'Datasets Processados',
      processoA: 'Cálculo de Indicadores de Qualidade',
      processoB: 'Análise Comparativa (Gold vs. Target)',
      saida: 'Relatórios Analíticos, Dashboards e Recomendações',
      suporteIA: 'Interpretação de relatórios e sugestão de correções para falhas detectadas'
    }
  ];

  const qualityDimensions = [
    {
      name: 'Completude',
      description: 'Presença de todos os dados necessários'
    },
    {
      name: 'Unicidade',
      description: 'Ausência de duplicações indevidas'
    },
    {
      name: 'Consistência',
      description: 'Uniformidade entre sistemas'
    },
    {
      name: 'Validade',
      description: 'Conformidade com regras de negócio'
    },
    {
      name: 'Integridade',
      description: 'Manutenção de relacionamentos'
    },
    {
      name: 'Acurácia',
      description: 'Precisão e correção dos valores'
    }
  ];

  return (
    <motion.div
      initial="initial"
      animate="animate"
      className="min-h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#1a1a2e] text-white overflow-x-hidden"
    >
      {/* Header */}
      <motion.div
        variants={fadeIn}
        className="relative pt-8 pb-6 px-6"
      >
        <div className="max-w-7xl mx-auto">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-purple-300 hover:text-purple-200 transition-colors mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Voltar para Home
          </Link>

          <motion.h1
            variants={slideIn}
            className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600"
          >
            Framework Metodológico para QA em Big Data com Suporte de IA
          </motion.h1>
          <motion.p
            variants={fadeIn}
            className="text-lg md:text-xl text-purple-300"
          >
            Modelo de Processo com Camada de Suporte Inteligente Transversal
          </motion.p>
        </div>
      </motion.div>

      {/* AI Support Layer */}
      <motion.div
        variants={fadeIn}
        className="max-w-7xl mx-auto px-6 mb-8"
      >
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 shadow-2xl border border-blue-500/30">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-white/20 p-3 rounded-lg">
              <Lightbulb className="w-8 h-8 text-yellow-300" />
            </div>
            <h2 className="text-2xl md:text-3xl font-bold">
              Inteligência e Suporte à Decisão
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Base de Conhecimento */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="flex items-center gap-3 mb-4">
                <BookOpen className="w-6 h-6 text-blue-200" />
                <h3 className="text-xl font-semibold">Base de Conhecimento Aprimorada</h3>
              </div>
              <p className="text-blue-100 text-sm leading-relaxed">
                Repositório dinâmico com documentação técnica, histórico de testes e 
                revisão multivocal da literatura (Knowledge Retrieval / RAG)
              </p>
            </div>

            {/* Sistema LLM */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-6 h-6 text-purple-200" />
                <h3 className="text-xl font-semibold">Sistema de Suporte Baseado em LLMs</h3>
              </div>
              <p className="text-blue-100 text-sm leading-relaxed">
                Interface conversacional para consulta de checklists, interpretação de regras 
                e análise de causa raiz de falhas
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Workflow - 4 Phases */}
      <motion.div
        variants={staggerContainer}
        className="max-w-7xl mx-auto px-6 mb-8"
      >
        <h2 className="text-3xl font-bold mb-8 text-center">
          Fluxo Principal - Ciclo de Vida de QA
        </h2>

        <div className="space-y-6">
          {phases.map((phase, index) => {
            const PhaseIcon = phase.icon;
            return (
              <motion.div
                key={phase.number}
                variants={fadeIn}
                className="relative"
              >
                {/* Phase Card */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-700/50">
                  {/* Phase Header */}
                  <div className="flex items-center gap-4 mb-6">
                    <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full px-4 py-2 text-sm font-bold">
                      Fase {phase.number}
                    </div>
                    <div className={`${phase.iconColor}`}>
                      <PhaseIcon className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold flex-1">{phase.title}</h3>
                  </div>

                  {/* Phase Content */}
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* Entrada */}
                    <div className="bg-white/5 rounded-xl p-4 border border-gray-600">
                      <div className="text-xs font-semibold text-gray-400 uppercase mb-2">
                        Entrada
                      </div>
                      <p className="text-sm text-gray-200">{phase.entrada}</p>
                    </div>

                    {/* Processos */}
                    <div className="space-y-3">
                      <div className="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
                        <div className="text-xs font-semibold text-blue-300 uppercase mb-2">
                          Processo A
                        </div>
                        <p className="text-sm text-gray-200">{phase.processoA}</p>
                      </div>
                      <div className="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
                        <div className="text-xs font-semibold text-blue-300 uppercase mb-2">
                          Processo B
                        </div>
                        <p className="text-sm text-gray-200">{phase.processoB}</p>
                      </div>
                    </div>

                    {/* Saída */}
                    <div className="bg-white/5 rounded-xl p-4 border-2 border-green-500/50">
                      <div className="text-xs font-semibold text-green-400 uppercase mb-2 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Saída
                      </div>
                      <p className="text-sm text-gray-200">{phase.saida}</p>
                    </div>
                  </div>

                  {/* AI Support Box */}
                  <div className="mt-4 bg-blue-500/10 rounded-xl p-4 border border-blue-500/30">
                    <div className="flex items-start gap-3">
                      <Brain className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <div className="text-xs font-semibold text-blue-400 uppercase mb-1">
                          Suporte IA
                        </div>
                        <p className="text-sm text-blue-200">{phase.suporteIA}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Arrow to next phase */}
                {index < phases.length - 1 && (
                  <div className="flex justify-center my-4">
                    <ArrowRight className="w-6 h-6 text-purple-400" />
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Quality Dimensions */}
      <motion.div
        variants={fadeIn}
        className="max-w-7xl mx-auto px-6 mb-8"
      >
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-gray-700/50">
          <h2 className="text-2xl md:text-3xl font-bold mb-6 text-center">
            Dimensões de Qualidade de Dados
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {qualityDimensions.map((dimension, index) => (
              <motion.div
                key={index}
                variants={fadeIn}
                className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-xl p-6 border border-purple-500/30 hover:border-purple-400/50 transition-all"
              >
                <h3 className="text-lg font-bold mb-2 text-purple-300">
                  {dimension.name}
                </h3>
                <p className="text-sm text-gray-300">
                  {dimension.description}
                </p>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 text-center text-sm text-gray-400 italic">
            Framework aplicável a dados estruturados e semi-estruturados em ambientes de processamento distribuído
          </div>
        </div>
      </motion.div>

      {/* Footer */}
      <motion.div
        variants={fadeIn}
        className="max-w-7xl mx-auto px-6 pb-12"
      >
        <div className="text-center text-gray-400 text-sm">
          <p className="font-semibold">
            Dissertação de Mestrado - Framework Metodológico para Qualidade de Dados em Big Data
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MethodologyPage;
