import React, { useState, useEffect } from 'react';
import './App.css';

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
  const [generatedDsl, setGeneratedDsl] = useState(null);
  const [generatedPysparkCode, setGeneratedPysparkCode] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState([]);

  const sections = Object.keys(QUESTIONS);
  const currentSection = sections[currentSectionIndex];
  const questionsInCurrentSection = QUESTIONS[currentSection];
  const currentQuestion = questionsInCurrentSection ? questionsInCurrentSection[currentQuestionIndex] : null;

  useEffect(() => {
    if (currentQuestion) {
      setChatHistory(prev => [...prev, { type: 'question', text: currentQuestion }]);
    } else if (currentSectionIndex < sections.length) {
      // Move to next section if current section is exhausted
      setCurrentSectionIndex(prev => prev + 1);
      setCurrentQuestionIndex(0);
    } else {
      // All questions answered, send to backend
      sendAnswersToBackend();
    }
  }, [currentQuestion, currentSectionIndex]); // Depend on currentQuestion and currentSectionIndex

  const handleInputChange = (e) => {
    setCurrentInput(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!currentInput.trim()) return;

    setChatHistory(prev => [...prev, { type: 'answer', text: currentInput }]);
    setAnswers(prev => ({ ...prev, [currentQuestion]: currentInput }));
    setCurrentInput('');

    if (currentQuestionIndex < questionsInCurrentSection.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      setCurrentSectionIndex(prev => prev + 1);
      setCurrentQuestionIndex(0);
    }
  };

  const sendAnswersToBackend = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/ask', { // Assuming Flask runs on 5000
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers }),
      });
      const data = await response.json();
      setGeneratedDsl(data.dsl);
      setGeneratedPysparkCode(data.pyspark_code);
      setErrors(data.errors || []);
      setChatHistory(prev => [...prev, { type: 'system', text: 'Generated DSL and PySpark code.' }]);
    } catch (error) {
      console.error('Error sending answers to backend:', error);
      setChatHistory(prev => [...prev, { type: 'system', text: 'Error generating code. Please check console for details.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Data Quality Chatbot</h1>
      </header>
      <div className="chat-container">
        <div className="chat-history">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.type}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && <div className="chat-message system">Generating code...</div>}
        </div>

        {!generatedDsl && (
          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              type="text"
              value={currentInput}
              onChange={handleInputChange}
              placeholder="Type your answer here..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>Send</button>
          </form>
        )}

        {generatedDsl && (
          <div className="generated-output">
            <h2>Generated DSL:</h2>
            <pre>{JSON.stringify(generatedDsl, null, 2)}</pre>

            {errors.length > 0 && (
              <div className="errors-section">
                <h3>Errors:</h3>
                <ul>
                  {errors.map((error, index) => (
                    <li key={index}><strong>{error.type}:</strong> {error.message}</li>
                  ))}
                </ul>
              </div>
            )}

            <h2>Generated PySpark Code:</h2>
            <pre>{generatedPysparkCode}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
