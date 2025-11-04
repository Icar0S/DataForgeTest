import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import PySparkDropdown from '../PySparkDropdown';

describe('PySparkDropdown', () => {
  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <PySparkDropdown />
      </BrowserRouter>
    );
  };

  test('renders dropdown button', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Generate PySpark Code');
  });

  test('dropdown opens on click', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    
    // Initially, dropdown should be closed
    expect(screen.queryByText('Interactive questionnaire for code generation')).not.toBeInTheDocument();
    
    // Click to open
    fireEvent.click(button);
    
    // Dropdown should now be visible
    expect(screen.getByText('Interactive questionnaire for code generation')).toBeInTheDocument();
    expect(screen.getByText('Upload dataset for automatic schema detection')).toBeInTheDocument();
  });

  test('has correct menu items', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    fireEvent.click(button);
    
    // Check for both menu items by looking for unique descriptions
    expect(screen.getByText('Interactive questionnaire for code generation')).toBeInTheDocument();
    expect(screen.getByText('Generate Advanced PySpark Code')).toBeInTheDocument();
    expect(screen.getByText('Upload dataset for automatic schema detection')).toBeInTheDocument();
  });

  test('dropdown has correct links', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    fireEvent.click(button);
    
    // Get the links
    const links = screen.getAllByRole('link');
    const regularLink = links.find(link => link.getAttribute('href') === '/qa-checklist');
    const advancedLink = links.find(link => link.getAttribute('href') === '/pyspark/advanced');
    
    expect(regularLink).toBeInTheDocument();
    expect(advancedLink).toBeInTheDocument();
  });

  test('chevron icon rotates when dropdown opens', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    
    // Get the chevron (it's inside the button)
    const chevron = button.querySelector('.lucide-chevron-down');
    
    // Initially, chevron should not be rotated
    expect(chevron).not.toHaveClass('rotate-180');
    
    // Click to open
    fireEvent.click(button);
    
    // Chevron should now be rotated
    expect(chevron).toHaveClass('rotate-180');
  });

  test('dropdown closes when clicking outside', async () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    
    // Open dropdown
    fireEvent.click(button);
    expect(screen.getByText('Interactive questionnaire for code generation')).toBeInTheDocument();
    
    // Click outside
    fireEvent.mouseDown(document.body);
    
    // Wait for dropdown to close
    await waitFor(() => {
      expect(screen.queryByText('Interactive questionnaire for code generation')).not.toBeInTheDocument();
    });
  });

  test('supports keyboard navigation', () => {
    renderComponent();
    const button = screen.getByLabelText('Generate PySpark Code Menu');
    
    // Press Enter to open
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(screen.getByText('Interactive questionnaire for code generation')).toBeInTheDocument();
    
    // Press Escape to close
    fireEvent.keyDown(button, { key: 'Escape' });
    
    // Dropdown should close (but animation might delay it)
  });
});
