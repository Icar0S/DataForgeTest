import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { MessageCircle, Send, Trash2, X } from 'react-feather';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const CodeComponent = ({node, inline, className, children, ...props}) => {
  const match = /language-(\w+)/.exec(className || '');
  return !inline && match ? (
    <SyntaxHighlighter
      children={Array.isArray(children) ? String(children).replace(/\n$/, '') : String(children)}
      style={materialDark}
      language={match[1]}
      PreTag="div"
      {...props}
    />
  ) : (
    <code className={className} {...props}>
      {children}
    </code>
  );
};

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState([]);
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);
  
  useEffect(() => {
    // Scroll to bottom on new messages
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  useEffect(() => {
    // Cleanup EventSource on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Add empty assistant message for streaming
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
      
      // Start streaming response
      eventSourceRef.current = new EventSource(
        `/api/rag/chat?message=${encodeURIComponent(userMessage)}`
      );
      
      let currentMessage = '';
      
      eventSourceRef.current.onmessage = (event) => {
        if (event.data === '[DONE]') {
          setIsLoading(false);
          eventSourceRef.current.close();
          return;
        }
        
        const data = JSON.parse(event.data);
        
        if (data.type === 'token') {
          currentMessage += data.content;
          setMessages(prev => [
            ...prev.slice(0, -1),
            { role: 'assistant', content: currentMessage }
          ]);
        }
        else if (data.type === 'citations') {
          setSources(data.content.citations);
          setIsLoading(false);
          eventSourceRef.current.close();
        }
        else if (data.type === 'error') {
          setError(data.content);
          setIsLoading(false);
          eventSourceRef.current.close();
        }
      };
      
      eventSourceRef.current.onerror = () => {
        setError('Connection error. Please try again.');
        eventSourceRef.current.close();
        setIsLoading(false);
      };
      
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };
  
  const clearChat = () => {
    setMessages([]);
    setSources([]);
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700/50">
        <div className="flex items-center space-x-3">
          <MessageCircle className="w-6 h-6 text-purple-400" />
          <h2 className="text-lg font-semibold text-white">AI Documentation Assistant</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            className="p-2 text-gray-400 hover:text-gray-200 transition-colors"
            aria-label="Clear chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-200 transition-colors"
            aria-label="Close chat"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                : 'bg-gray-800/50 text-gray-100 border border-gray-700/50'
            }`}>
              <ReactMarkdown
                components={{
                  code: CodeComponent
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
        
        {/* Citations */}
        {sources.length > 0 && (
          <div className="mt-4 p-4 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50">
            <h3 className="font-semibold mb-2 text-purple-300">Sources:</h3>
            <ul className="space-y-2">
              {sources.map((source, idx) => (
                <li key={idx} className="text-sm">
                  <span className="font-mono text-purple-400">[{source.id}]</span>{" "}
                  <span className="text-gray-300">{source.text}</span>
                  <div className="text-xs text-gray-400">
                    From: {source.metadata.filename}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {error && (
          <div className="p-4 text-red-300 bg-red-900/30 border border-red-700/50 rounded-lg backdrop-blur-sm">
            {error}
          </div>
        )}
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-gray-700/50 bg-gray-900/30">
        <form
          onSubmit={e => {
            e.preventDefault();
            handleSend();
          }}
          className="flex space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-3 bg-gray-800/90 text-white border border-gray-700/50 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            aria-label="Send message"
            className="p-3 text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all duration-200 disabled:opacity-50"
            disabled={isLoading}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

ChatWindow.propTypes = {
  onClose: PropTypes.func.isRequired
};

export default ChatWindow;