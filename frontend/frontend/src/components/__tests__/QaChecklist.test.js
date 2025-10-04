import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import QaChecklist from '../../pages/QaChecklist';

// Use manual mock for react-router-dom
jest.mock('react-router-dom');

// Mock EventSource
class MockEventSource {
  constructor(url) {
    this.url = url;
    this.readyState = 1;
    this.onmessage = null;
    this.onerror = null;
    this.onopen = null;
    MockEventSource.instances.push(this);
  }

  close() {
    this.readyState = 2;
  }

  static instances = [];
  static clearInstances() {
    this.instances = [];
  }
}

global.EventSource = MockEventSource;

// Mock react-markdown and react-syntax-highlighter
jest.mock('react-markdown', () => {
  function ReactMarkdown({ children }) {
    return <div data-testid="markdown-content">{children}</div>;
  }
  return ReactMarkdown;
});

jest.mock('react-syntax-highlighter', () => ({
  Prism: function SyntaxHighlighter({ children }) {
    return <pre data-testid="syntax-highlighter">{children}</pre>;
  }
}));

jest.mock('react-syntax-highlighter/dist/esm/styles/prism', () => ({
  materialDark: {}
}));

// Helper to render component
const renderComponent = (component) => {
  return render(component);
};

describe('QaChecklist Component', () => {
  beforeEach(() => {
    MockEventSource.clearInstances();
    jest.clearAllMocks();
  });

  afterEach(() => {
    MockEventSource.instances.forEach(instance => {
      instance.close();
    });
  });

  test('renders QaChecklist page with all elements', () => {
    renderComponent(<QaChecklist />);
    
    expect(screen.getByText('Checklist de Testes QA')).toBeInTheDocument();
    expect(screen.getByText('Voltar')).toBeInTheDocument();
    expect(screen.getByText('Limpar')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Digite sua mensagem/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Enviar mensagem/i })).toBeInTheDocument();
  });

  test('auto-focuses on input field when page loads', () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    expect(textarea).toHaveFocus();
  });

  test('sends message when Enter key is pressed', async () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    
    // Press Enter key
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });
    
    // Check that message was sent
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
    
    // Check that input was cleared
    expect(textarea.value).toBe('');
    
    // Check that EventSource was created
    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });
  });

  test('creates new line when Shift+Enter is pressed', () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    
    // Type initial text
    fireEvent.change(textarea, { target: { value: 'Line 1' } });
    
    // Press Shift+Enter - should NOT send message
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });
    
    // EventSource should NOT be created
    expect(MockEventSource.instances).toHaveLength(0);
    
    // The textarea should still have content
    expect(textarea.value).toBe('Line 1');
  });

  test('back button navigates to home page', () => {
    renderComponent(<QaChecklist />);
    
    const backButton = screen.getByRole('link', { name: /Voltar para a Home/i });
    expect(backButton).toHaveAttribute('href', '/');
  });

  test('disables send button while loading', async () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    
    // Type and send message
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    // Button should be disabled and show loading state
    await waitFor(() => {
      expect(sendButton).toBeDisabled();
      expect(screen.getByText('Enviando...')).toBeInTheDocument();
    });
  });

  test('disables send button when input is empty', () => {
    renderComponent(<QaChecklist />);
    
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    
    // Button should be disabled when input is empty
    expect(sendButton).toBeDisabled();
  });

  test('enables send button when input has text', () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    
    // Initially disabled
    expect(sendButton).toBeDisabled();
    
    // Type text
    fireEvent.change(textarea, { target: { value: 'Some text' } });
    
    // Should now be enabled
    expect(sendButton).not.toBeDisabled();
  });

  test('clears chat when clear button is clicked', async () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    const clearButton = screen.getByRole('button', { name: /Limpar conversa/i });
    
    // Send a message
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
    
    // Clear chat
    fireEvent.click(clearButton);
    
    // Message should be gone
    await waitFor(() => {
      expect(screen.queryByText('Test message')).not.toBeInTheDocument();
    });
    
    // Welcome message should be visible again
    expect(screen.getByText(/Bem-vindo ao Checklist de Testes QA/)).toBeInTheDocument();
  });

  test('displays welcome message when no messages', () => {
    renderComponent(<QaChecklist />);
    
    expect(screen.getByText('Bem-vindo ao Checklist de Testes QA')).toBeInTheDocument();
    expect(screen.getByText('Digite sua mensagem para começar')).toBeInTheDocument();
  });

  test('handles responsive layout classes', () => {
    renderComponent(<QaChecklist />);
    
    // Find the main content container by its classes instead of DOM navigation
    const containers = document.querySelectorAll('.max-w-5xl');
    expect(containers.length).toBeGreaterThan(0);
    
    const container = containers[0];
    expect(container).toHaveClass('max-w-5xl');
    expect(container).toHaveClass('lg:max-w-7xl');
  });

  test('textarea has proper accessibility attributes', () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    
    expect(textarea).toHaveAttribute('aria-label', 'Campo de mensagem');
  });

  test('send button has proper accessibility attributes', () => {
    renderComponent(<QaChecklist />);
    
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    
    expect(sendButton).toHaveAttribute('aria-label', 'Enviar mensagem');
    expect(sendButton).toHaveAttribute('aria-disabled', 'true');
  });

  test('displays error message when connection fails', async () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    const sendButton = screen.getByRole('button', { name: /Enviar mensagem/i });
    
    // Send message
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });
    
    const eventSource = MockEventSource.instances[0];
    
    // Simulate connection error wrapped in act
    await waitFor(() => {
      eventSource.onerror();
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Connection error. Please try again./)).toBeInTheDocument();
    });
  });

  test('form submission works correctly', async () => {
    renderComponent(<QaChecklist />);
    
    const textarea = screen.getByPlaceholderText(/Digite sua mensagem/);
    const form = textarea.closest('form');
    
    // Type message
    fireEvent.change(textarea, { target: { value: 'Form test' } });
    
    // Submit form
    fireEvent.submit(form);
    
    // Message should appear
    await waitFor(() => {
      expect(screen.getByText('Form test')).toBeInTheDocument();
    });
    
    // Input should be cleared
    expect(textarea.value).toBe('');
  });
});
