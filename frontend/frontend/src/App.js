import React, { useState } from 'react';
// Importar o CSS do Tailwind primeiro
import './index.css';
// Depois importar os estilos específicos da aplicação
import './App.css';
import HomePage from './components/HomePage';

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
  const [generatedPysparkCode] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading] = useState(false);
  const [errors] = useState([]);
  const [showChat, setShowChat] = useState(false);

  const sections = Object.keys(QUESTIONS);
  const currentSection = sections[currentSectionIndex];
  const questionsInCurrentSection = QUESTIONS[currentSection];
  const currentQuestion = questionsInCurrentSection ? questionsInCurrentSection[currentQuestionIndex] : null;

  // Handle the start chat action
  const handleStartChat = () => {
    setShowChat(true);
  };

  return (
    <div className="App">
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
            <div className="max-w-4xl mx-auto p-6 space-y-6">
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

              {/* Current Question */}
              {currentQuestion && (
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
                        }
                      }}
                      className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                    >
                      Submit
                    </button>
                  </div>
                </div>
              )}

              {/* Generated Code Display */}
              {generatedPysparkCode && (
                <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
                  <h3 className="text-xl font-bold text-white mb-4">Generated PySpark Code:</h3>
                  <pre className="text-gray-300 overflow-x-auto">
                    {generatedPysparkCode}
                  </pre>
                </div>
              )}
              
              {/* Error Display */}
              {errors.length > 0 && (
                <div className="bg-red-900/50 p-4 rounded-lg border border-red-700">
                  <h3 className="text-xl font-bold text-red-300 mb-2">Validation Errors:</h3>
                  <ul className="list-disc list-inside text-red-200">
                    {errors.map((error) => (
                      <li key={error}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;