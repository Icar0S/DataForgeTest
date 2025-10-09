/**
 * Tests for SupportButton component
 * Tests basic rendering and interaction functionality
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SupportButton from '../SupportButton';

// Mock ChatWindow to avoid complex dependencies
jest.mock('../ChatWindow', () => {
  // eslint-disable-next-line react/prop-types
  return function MockChatWindow({ onClose }) {
    return (
      <div data-testid="chat-window">
        <button onClick={onClose}>Close Chat</button>
      </div>
    );
  };
});

describe('SupportButton Component', () => {
  describe('Initial Render', () => {
    test('renders support button', () => {
      render(<SupportButton />);
      
      const button = screen.getByRole('button', { name: /open support chat/i });
      expect(button).toBeInTheDocument();
    });

    test('has correct accessibility label', () => {
      render(<SupportButton />);
      
      const button = screen.getByRole('button', { name: /open support chat/i });
      expect(button).toHaveAttribute('aria-label', 'Open support chat');
    });

    test('chat window is not visible initially', () => {
      render(<SupportButton />);
      
      const chatWindow = screen.queryByTestId('chat-window');
      expect(chatWindow).not.toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('opens chat window when button is clicked', () => {
      render(<SupportButton />);
      
      const button = screen.getByRole('button', { name: /open support chat/i });
      fireEvent.click(button);
      
      const chatWindow = screen.getByTestId('chat-window');
      expect(chatWindow).toBeInTheDocument();
    });

    test('closes chat window when close is triggered', () => {
      render(<SupportButton />);
      
      // Open chat
      const openButton = screen.getByRole('button', { name: /open support chat/i });
      fireEvent.click(openButton);
      
      // Verify it's open
      expect(screen.getByTestId('chat-window')).toBeInTheDocument();
      
      // Close chat
      const closeButton = screen.getByRole('button', { name: /close chat/i });
      fireEvent.click(closeButton);
      
      // Verify it's closed
      expect(screen.queryByTestId('chat-window')).not.toBeInTheDocument();
    });

    test('can toggle chat window multiple times', () => {
      render(<SupportButton />);
      
      const openButton = screen.getByRole('button', { name: /open support chat/i });
      
      // Open
      fireEvent.click(openButton);
      expect(screen.getByTestId('chat-window')).toBeInTheDocument();
      
      // Close
      const closeButton = screen.getByRole('button', { name: /close chat/i });
      fireEvent.click(closeButton);
      expect(screen.queryByTestId('chat-window')).not.toBeInTheDocument();
      
      // Open again
      fireEvent.click(openButton);
      expect(screen.getByTestId('chat-window')).toBeInTheDocument();
    });
  });

  describe('Layout and Styling', () => {
    test('button has fixed positioning classes', () => {
      render(<SupportButton />);
      
      const button = screen.getByRole('button', { name: /open support chat/i });
      expect(button).toHaveClass('fixed');
      expect(button).toHaveClass('bottom-6');
      expect(button).toHaveClass('right-6');
    });

    test('chat overlay has correct backdrop classes when open', () => {
      render(<SupportButton />);
      
      const button = screen.getByRole('button', { name: /open support chat/i });
      fireEvent.click(button);
      
      // The overlay is the grandparent of the chat-window
      const chatContainer = screen.getByTestId('chat-window').parentElement.parentElement;
      expect(chatContainer).toHaveClass('fixed');
      expect(chatContainer).toHaveClass('inset-0');
      expect(chatContainer).toHaveClass('z-50');
    });
  });
});
