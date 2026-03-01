import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatWindow from '../../../frontend/src/components/ChatWindow';

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

describe('ChatWindow Integration Tests', () => {
  let mockOnClose;

  beforeEach(() => {
    mockOnClose = jest.fn();
    MockEventSource.clearInstances();
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Clean up any open EventSource instances
    MockEventSource.instances.forEach(instance => {
      instance.close();
    });
  });

  test('renders ChatWindow with initial UI elements', () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    expect(screen.getByText('AI Documentation Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /clear chat/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /close chat/i })).toBeInTheDocument();
  });

  test('sends message and handles streaming response', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    // Type a message
    fireEvent.change(input, { target: { value: 'Hello, how can you help?' } });
    
    // Send the message
    fireEvent.click(sendButton);

    // Check that user message appears
    expect(screen.getByText('Hello, how can you help?')).toBeInTheDocument();
    
    // Check that input is cleared
    expect(input.value).toBe('');

    // Verify EventSource was created with correct URL
    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const eventSource = MockEventSource.instances[0];
    expect(eventSource.url).toContain('/api/rag/chat?message=');
    expect(eventSource.url).toContain(encodeURIComponent('Hello, how can you help?'));
  });

  test('handles streaming tokens correctly', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const eventSource = MockEventSource.instances[0];

    // Simulate streaming response
    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({ type: 'token', content: 'Hello ' })
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Hello/)).toBeInTheDocument();
    });

    // Add more tokens
    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({ type: 'token', content: 'there! ' })
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Hello there!/)).toBeInTheDocument();
    });

    // Send citations
    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({
          type: 'citations',
          content: {
            citations: [
              {
                id: 1,
                text: 'Sample citation text...',
                metadata: { filename: 'test.txt', type: '.txt' }
              }
            ]
          }
        })
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Sources:/)).toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(screen.getByText(/test.txt/)).toBeInTheDocument();
    });
  });

  test('handles connection errors gracefully', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const eventSource = MockEventSource.instances[0];

    // Simulate connection error
    act(() => {
      eventSource.onerror();
    });

    await waitFor(() => {
      expect(screen.getByText(/Connection error. Please try again./)).toBeInTheDocument();
    });
  });

  test('handles server errors in streaming', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const eventSource = MockEventSource.instances[0];

    // Simulate server error
    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({
          type: 'error',
          content: 'Server internal error'
        })
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Server internal error/)).toBeInTheDocument();
    });
  });

  test('clears chat history when clear button is clicked', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });
    const clearButton = screen.getByRole('button', { name: /clear chat/i });

    // Send a message first
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    // Clear the chat
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(screen.queryByText('Test message')).not.toBeInTheDocument();
    });
  });

  test('calls onClose when close button is clicked', () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const closeButton = screen.getByRole('button', { name: /close chat/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('prevents sending empty messages', () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const sendButton = screen.getByRole('button', { name: /send message/i });
    
    // Try to send empty message
    fireEvent.click(sendButton);

    // Should not create EventSource
    expect(MockEventSource.instances).toHaveLength(0);
  });

  test('handles form submission', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test form submission' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test form submission')).toBeInTheDocument();
    });

    expect(MockEventSource.instances).toHaveLength(1);
  });

  test('displays citations with proper formatting', async () => {
    render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test citations' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const eventSource = MockEventSource.instances[0];

    // Send response with citations
    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({ type: 'token', content: 'Here is the answer: ' })
      });
    });

    act(() => {
      eventSource.onmessage({
        data: JSON.stringify({
          type: 'citations',
          content: {
            citations: [
              {
                id: 1,
                text: 'This is a sample citation with detailed information about the topic...',
                metadata: { filename: 'document1.pdf', type: '.pdf', size: 1024 }
              },
              {
                id: 2,
                text: 'Another citation from a different source with more context...',
                metadata: { filename: 'document2.txt', type: '.txt', size: 512 }
              }
            ]
          }
        })
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Sources:/)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/document1.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/document2.txt/)).toBeInTheDocument();
    expect(screen.getByText(/This is a sample citation/)).toBeInTheDocument();
    expect(screen.getByText(/Another citation from/)).toBeInTheDocument();
  });

  test('cleanup EventSource on component unmount', () => {
    const { unmount } = render(<ChatWindow onClose={mockOnClose} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Test cleanup' } });
    fireEvent.click(sendButton);

    expect(MockEventSource.instances).toHaveLength(1);
    const eventSource = MockEventSource.instances[0];
    const closeSpy = jest.spyOn(eventSource, 'close');

    unmount();

    expect(closeSpy).toHaveBeenCalled();
  });
});
