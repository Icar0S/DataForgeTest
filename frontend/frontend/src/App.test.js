import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

describe('App Component', () => {
  test('renders HomePage initially', () => {
    render(<App />);
    expect(screen.getByText(/DataForgeTest/i)).toBeInTheDocument();
    expect(screen.getByText(/Big Data Quality Testing/i)).toBeInTheDocument();
  });

  test('shows chat interface after clicking start', () => {
    render(<App />);
    const startButton = screen.getByText(/Start Testing/i);
    fireEvent.click(startButton);
    expect(screen.getByText(/Data Quality Validation Setup/i)).toBeInTheDocument();
  });

  test('shows first question after starting chat', () => {
    render(<App />);
    const startButton = screen.getByText(/Start Testing/i);
    fireEvent.click(startButton);
    expect(screen.getByText(/What is the name of the dataset/i)).toBeInTheDocument();
  });

  test('can submit an answer and move to next question', () => {
    render(<App />);
    const startButton = screen.getByText(/Start Testing/i);
    fireEvent.click(startButton);
    
    const input = screen.getByPlaceholderText(/Type your answer here/i);
    fireEvent.change(input, { target: { value: 'test_dataset' } });
    
    const submitButton = screen.getByText('Submit');
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/What is the source of the data/i)).toBeInTheDocument();
  });
});
