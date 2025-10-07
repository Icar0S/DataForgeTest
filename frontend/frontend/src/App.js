import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// Importar o CSS do Tailwind primeiro
import './index.css';
// Depois importar os estilos específicos da aplicação
import './App.css';
import HomePage from './components/HomePage';
import SupportPage from './pages/SupportPage';
import DataAccuracy from './pages/DataAccuracy';
import TestDatasetGold from './pages/TestDatasetGold';
import QaChecklist from './pages/QaChecklist';
import GenerateDataset from './pages/GenerateDataset';
import SupportButton from './components/SupportButton';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/support-rag" element={<SupportPage />} />
          <Route path="/data-accuracy" element={<DataAccuracy />} />
          <Route path="/data-accuracy/test-gold" element={<TestDatasetGold />} />
          <Route path="/qa-checklist" element={<QaChecklist />} />
          <Route path="/generate-dataset" element={<GenerateDataset />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
        {/* Add support button on all pages except support page */}
        {window.location.pathname !== '/support-rag' && (
          <SupportButton />
        )}
      </div>
    </Router>
  );
}

export default App;