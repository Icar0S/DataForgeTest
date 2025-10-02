import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// Importar o CSS do Tailwind primeiro
import './index.css';
// Depois importar os estilos específicos da aplicação
import './App.css';
import HomePage from './components/HomePage';
import SupportPage from './pages/SupportPage';
import SupportButton from './components/SupportButton';

// Hardcoded questions for now, ideally fetched from backend
const QUESTIONS = {
    "General": [
        "What is the name of the dataset you want to validate? (e.g., customer_data)",
        "What is the source of the data (e.g., a file path like /data/customer.csv, or a database table name like sales.customers)?",
        "What is the format of the data (e.g., CSV, JSON, Parquet, Delta)?"
    ],
    "Schema Validation": [
        "Does the data have a header? (yes/no)",
        "What are the expected column names, in order? (e.g., id, first_name, last_name, email)",
        "What is the expected data type for each column (e.g., integer, string, float, date)? Please list them in the same order as column names, separated by commas. (e.g., integer, string, string, string)"
    ],
    "Data Integrity": [
        "Which columns should not contain any missing values (i.e., are mandatory)? List them separated by commas. (e.g., id, email)",
        "Which columns should contain unique values (i.e., are primary keys)? List them separated by commas. (e.g., id, order_id)",
        "Are there any columns that should have a specific format (e.g., a date format like YYYY-MM-DD)? List as 'column:format', separated by commas. (e.g., registration_date:YYYY-MM-DD, transaction_time:HH:mm:ss)"
    ],
    "Value Constraints": [
        "Are there any columns that should have a minimum or maximum value? List as 'column:min:max', 'column::max', or 'column:min:', separated by commas. (e.g., age:18:99, price::1000, quantity:1:)",
        "Are there any columns that should only contain values from a specific set (e.g., a list of categories)? List as 'column:[value1,value2]', separated by '],'. (e.g., status:[active,inactive,pending], gender:[M,F,Other])",
        "Are there any columns that should match a specific regular expression pattern? List as 'column:pattern', separated by commas. (e.g., email:^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\[a-zA-Z]{2,}$, phone_number:^\\d{3}-\\d{3}-\\d{4}$)",
        "Are there any columns for which you want to check the value distribution (e.g., to ensure certain values appear with a specific frequency)? List as 'column:value:min_freq:max_freq', separated by commas. (e.g., status:active:0.7:1.0, status:inactive:0.0:0.1)"
    ],
    "Cross-Column Validation": [
        "Are there any relationships between two columns that should always hold true (e.g., 'start_date' must be before 'end_date', 'price' must be greater than 'cost')? List as 'column1:operator:column2', separated by commas. Supported operators: <, <=, >, >=, ==, !=. (e.g., start_date:<:end_date, price:>:cost)"
    ]
};

function App() {
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [currentInput, setCurrentInput] = useState('');
  const [generatedPysparkCode, setGeneratedPysparkCode] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [showChat, setShowChat] = useState(false);
  const [allQuestionsAnswered, setAllQuestionsAnswered] = useState(false);
  const [copied, setCopied] = useState(false);

  const sections = Object.keys(QUESTIONS);
  const currentSection = sections[currentSectionIndex];
  const questionsInCurrentSection = QUESTIONS[currentSection];
  const currentQuestion = questionsInCurrentSection ? questionsInCurrentSection[currentQuestionIndex] : null;

  // Handle the start chat action
  const handleStartChat = () => {
    setShowChat(true);
  };

  // Function to copy code to clipboard
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generatedPysparkCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  // Function to send answers to backend and generate code
  const generateCode = async () => {
    setIsLoading(true);
    setErrors([]);
    setWarnings([]);
    
    try {
      // Convert answers to the format expected by backend
      const formattedAnswers = {};
      Object.keys(answers).forEach(key => {
        const [section, questionIndex] = key.split('_');
        const questionText = QUESTIONS[section][parseInt(questionIndex)];
        formattedAnswers[questionText] = answers[key];
      });

      console.log('Sending request to backend with answers:', formattedAnswers);
      
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers: formattedAnswers }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.warnings && data.warnings.length > 0) {
        setWarnings(data.warnings.map(warning => warning.message || warning));
      }
      
      if (data.errors && data.errors.length > 0) {
        setErrors(data.errors.map(error => error.message || error));
      }
      
      if (data.pyspark_code) {
        setGeneratedPysparkCode(data.pyspark_code);
      }
      
      if (data.dsl) {
        console.log('Generated DSL:', data.dsl);
      }
      
    } catch (error) {
      console.error('Error generating code:', error);
      setErrors([`Error connecting to backend: ${error.message}`]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/support-rag" element={<SupportPage />} />
          <Route path="/" element={
            <>
              {!showChat ? (
                <HomePage onStartChat={handleStartChat} />
              ) : (
                <div className="chat-container bg-gradient-to-br from-[#1a1a2e]/90 via-[#16213e]/90 to-[#1a1a2e]/90 backdrop-blur-sm">
          {isLoading ? (
            <div className="loading-container flex items-center justify-center h-screen">
              <div className="loading-spinner"></div>
              <p className="text-lg text-purple-300">Generating code...</p>
            </div>
          ) : (
            <div className="max-w-7xl mx-auto p-6 space-y-6">
              <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
                Data Quality Validation Setup
              </h2>
              
              {/* Section Title */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-purple-300">
                  {currentSection}
                </h3>
                <p className="text-gray-400">
                  Question {currentQuestionIndex + 1} of {questionsInCurrentSection?.length}
                </p>
              </div>

              {/* Chat History */}
              <div className="space-y-4 mb-8">
                {chatHistory.map((chat) => (
                  <div key={chat.text} className={`p-4 rounded-lg ${
                    chat.type === 'question' 
                      ? 'bg-gray-800/50 border border-gray-700'
                      : 'bg-purple-900/30 border border-purple-700'
                  }`}>
                    <p className="text-gray-200">{chat.text}</p>
                  </div>
                ))}
              </div>

              {/* All Questions Completed */}
              {allQuestionsAnswered && !isLoading && (
                <div className="bg-green-900/50 p-6 rounded-xl border border-green-700 mb-6">
                  <h3 className="text-xl font-bold text-green-300 mb-4">✅ All Questions Answered!</h3>
                  <p className="text-green-200 mb-4">
                    You have completed all the data quality validation questions. 
                    Click the button below to generate your PySpark code.
                  </p>
                  <button
                    onClick={generateCode}
                    className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 transition-colors"
                  >
                    🚀 Generate PySpark Code
                  </button>
                </div>
              )}

              {/* Current Question */}
              {currentQuestion && !allQuestionsAnswered && (
                <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
                  <p className="text-gray-200 mb-4">{currentQuestion}</p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={currentInput}
                      onChange={(e) => setCurrentInput(e.target.value)}
                      className="flex-1 bg-gray-900 text-white px-4 py-2 rounded-lg border border-gray-700 focus:border-purple-500 focus:outline-none"
                      placeholder="Type your answer here..."
                    />
                    <button
                      onClick={() => {
                        // Handle answer submission
                        const newAnswers = {
                          ...answers,
                          [`${currentSection}_${currentQuestionIndex}`]: currentInput
                        };
                        setAnswers(newAnswers);
                        
                        // Add to chat history
                        setChatHistory([
                          ...chatHistory,
                          { type: 'question', text: currentQuestion },
                          { type: 'answer', text: currentInput }
                        ]);

                        // Clear input
                        setCurrentInput('');

                        // Move to next question
                        if (currentQuestionIndex < questionsInCurrentSection.length - 1) {
                          setCurrentQuestionIndex(currentQuestionIndex + 1);
                        } else if (currentSectionIndex < sections.length - 1) {
                          setCurrentSectionIndex(currentSectionIndex + 1);
                          setCurrentQuestionIndex(0);
                        } else {
                          // All questions answered
                          setAllQuestionsAnswered(true);
                        }
                      }}
                      className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                    >
                      Submit
                    </button>
                  </div>
                </div>
              )}

              {/* Loading State */}
              {isLoading && (
                <div className="bg-blue-900/50 p-6 rounded-xl border border-blue-700">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-300 mr-3"></div>
                    <p className="text-blue-200">Generating PySpark code...</p>
                  </div>
                </div>
              )}

              {/* Generated Code Display */}
              {generatedPysparkCode && !isLoading && (
                <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-white">Generated PySpark Code:</h3>
                    <button
                      onClick={copyToClipboard}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        copied 
                          ? 'bg-green-600 text-white' 
                          : 'bg-purple-600 text-white hover:bg-purple-700'
                      }`}
                    >
                      {copied ? '✅ Copied!' : '📋 Copy Code'}
                    </button>
                  </div>
                  <div className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
                    <pre className="text-gray-300 text-sm font-mono whitespace-pre-wrap break-words leading-relaxed" style={{
                      fontFamily: "'Fira Code', 'Monaco', 'Consolas', 'Courier New', monospace",
                      lineHeight: '1.6',
                      tabSize: 4
                    }}>
                      <code className="language-python">
                        {generatedPysparkCode}
                      </code>
                    </pre>
                  </div>
                </div>
              )}
              
              {/* Warnings Display */}
              {warnings.length > 0 && (
                <div className="bg-yellow-900/50 p-4 rounded-lg border border-yellow-700 mb-4">
                  <h3 className="text-xl font-bold text-yellow-300 mb-2">⚠️ Warnings:</h3>
                  <ul className="list-disc list-inside text-yellow-200">
                    {warnings.map((warning) => (
                      <li key={`warning-${warning}`}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Error Display */}
              {errors.length > 0 && (
                <div className="bg-red-900/50 p-4 rounded-lg border border-red-700">
                  <h3 className="text-xl font-bold text-red-300 mb-2">❌ Validation Errors:</h3>
                  <ul className="list-disc list-inside text-red-200">
                    {errors.map((error) => (
                      <li key={`error-${error}`}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
            </>
          } />
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