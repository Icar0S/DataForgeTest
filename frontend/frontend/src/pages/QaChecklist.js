import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Send, Trash2 } from 'lucide-react';
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

const QaChecklist = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const eventSourceRef = useRef(null);
  
  // Auto-focus on input when component mounts
  useEffect(() => {
    inputRef.current?.focus();
  }, []);
  
  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
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
    setError(null);
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#1a1a2e]">
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b border-gray-700/50 bg-gray-900/50 backdrop-blur-sm">
        <Link
          to="/"
          className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white transition-colors rounded-lg hover:bg-gray-800/50"
          aria-label="Voltar para a Home"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Voltar</span>
        </Link>
        <h1 className="text-xl font-semibold text-white">Checklist de Testes QA</h1>
        <button
          onClick={clearChat}
          className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-800/50"
          aria-label="Limpar conversa"
        >
          <Trash2 className="w-5 h-5" />
          <span className="font-medium">Limpar</span>
        </button>
      </header>

      {/* Main Content Container */}
      <div className="flex-1 overflow-hidden">
        <div className="mx-auto max-w-5xl lg:max-w-7xl h-full flex flex-col p-4">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-400">
                  <p className="text-lg mb-2">Bem-vindo ao Checklist de Testes QA</p>
                  <p className="text-sm">Digite sua mensagem para começar</p>
                </div>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-4 rounded-lg ${
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
            
            {error && (
              <div className="p-4 text-red-300 bg-red-900/30 border border-red-700/50 rounded-lg backdrop-blur-sm">
                {error}
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area - Fixed at Bottom */}
          <div className="sticky bottom-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md p-3 rounded-lg border border-gray-700/50 shadow-lg">
            <form
              onSubmit={e => {
                e.preventDefault();
                handleSend();
              }}
              className="flex gap-2"
            >
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
                className="flex-1 p-3 bg-gray-800/90 text-white border border-gray-700/50 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows="3"
                disabled={isLoading}
                aria-label="Campo de mensagem"
              />
              <button
                type="submit"
                aria-label="Enviar mensagem"
                aria-disabled={isLoading || !input.trim()}
                className="px-6 py-3 text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                disabled={isLoading || !input.trim()}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Enviando...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Enviar</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QaChecklist;
