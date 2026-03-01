/**
 * Tests for TestDatasetGold component
 * Tests core rendering functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import TestDatasetGold from '../../../frontend/src/pages/TestDatasetGold';

// Mock fetch globally
global.fetch = jest.fn();

// Helper function to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('TestDatasetGold Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('Initial Render', () => {
    test('renders page title and description', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Test Dataset GOLD')).toBeInTheDocument();
      expect(screen.getByText('Upload and clean your dataset with automated data quality improvements')).toBeInTheDocument();
    });

    test('renders upload section', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Upload Dataset')).toBeInTheDocument();
      expect(screen.getByText('Drop your dataset here or click to browse')).toBeInTheDocument();
      expect(screen.getByText('Supported formats: CSV, XLSX, XLS, Parquet (max 50MB)')).toBeInTheDocument();
      expect(screen.getAllByRole('button', { name: /select file/i })[0]).toBeInTheDocument();
    });

    test('renders back to home link', () => {
      renderWithRouter(<TestDatasetGold />);
      
      const backLink = screen.getByRole('link', { name: 'Back to Home' });
      expect(backLink).toBeInTheDocument();
      expect(backLink).toHaveAttribute('href', '/');
    });
  });

  describe('Component Structure', () => {
    test('has proper heading hierarchy', () => {
      renderWithRouter(<TestDatasetGold />);
      
      const mainHeading = screen.getByRole('heading', { name: 'Test Dataset GOLD' });
      const uploadHeading = screen.getByRole('heading', { name: 'Upload Dataset' });
      
      expect(mainHeading).toBeInTheDocument();
      expect(uploadHeading).toBeInTheDocument();
    });

    test('has required UI elements', () => {
      renderWithRouter(<TestDatasetGold />);
      
      // Check for upload button
      expect(screen.getAllByRole('button', { name: /select file/i })[0]).toBeInTheDocument();
      
      // Check for navigation link
      expect(screen.getByRole('link', { name: 'Back to Home' })).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper button roles', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getAllByRole('button', { name: /select file/i })[0]).toBeInTheDocument();
    });

    test('sets document title', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(document.title).toBe('Test Dataset GOLD - DataForgeTest');
    });

    test('has proper navigation structure', () => {
      renderWithRouter(<TestDatasetGold />);
      
      const backLink = screen.getByRole('link', { name: 'Back to Home' });
      expect(backLink).toHaveAttribute('href', '/');
    });
  });

  describe('Page Content', () => {
    test('displays page description', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Upload and clean your dataset with automated data quality improvements')).toBeInTheDocument();
    });

    test('displays supported formats', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Supported formats: CSV, XLSX, XLS, Parquet (max 50MB)')).toBeInTheDocument();
    });

    test('displays drop zone text', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Drop your dataset here or click to browse')).toBeInTheDocument();
    });
  });

  describe('Initial State', () => {
    test('starts in upload state', () => {
      renderWithRouter(<TestDatasetGold />);
      
      // Should show upload section
      expect(screen.getByText('Upload Dataset')).toBeInTheDocument();
      
      // Should not show processing states
      expect(screen.queryByText('Dataset Information')).not.toBeInTheDocument();
      expect(screen.queryByText('Cleaning Report')).not.toBeInTheDocument();
      expect(screen.queryByText('Processing...')).not.toBeInTheDocument();
      expect(screen.queryByText('Download CSV')).not.toBeInTheDocument();
    });

    test('shows upload interface elements', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText('Upload Dataset')).toBeInTheDocument();
      expect(screen.getAllByRole('button', { name: /select file/i })[0]).toBeInTheDocument();
      expect(screen.getByText('Drop your dataset here or click to browse')).toBeInTheDocument();
    });
  });

  describe('UI Elements', () => {
    test('has upload section headings', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Test Dataset GOLD');
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Upload Dataset');
    });

    test('has descriptive text content', () => {
      renderWithRouter(<TestDatasetGold />);
      
      expect(screen.getByText(/automated data quality improvements/i)).toBeInTheDocument();
      expect(screen.getByText(/max 50MB/i)).toBeInTheDocument();
    });

    test('has interactive elements', () => {
      renderWithRouter(<TestDatasetGold />);
      
      const selectButton = screen.getAllByRole('button', { name: /select file/i })[0];
      const homeLink = screen.getByRole('link', { name: /back to home/i });
      
      expect(selectButton).toBeInTheDocument();
      expect(homeLink).toBeInTheDocument();
    });
  });

  describe('Layout Structure', () => {
    test('renders without crashing', () => {
      expect(() => renderWithRouter(<TestDatasetGold />)).not.toThrow();
    });

    test('contains main content sections', () => {
      renderWithRouter(<TestDatasetGold />);
      
      // Check for main sections
      expect(screen.getByText('Test Dataset GOLD')).toBeInTheDocument();
      expect(screen.getByText('Upload Dataset')).toBeInTheDocument();
    });

    test('has consistent text content', () => {
      renderWithRouter(<TestDatasetGold />);
      
      const descriptions = [
        'Upload and clean your dataset with automated data quality improvements',
        'Drop your dataset here or click to browse',
        'Supported formats: CSV, XLSX, XLS, Parquet (max 50MB)'
      ];

      descriptions.forEach(text => {
        expect(screen.getByText(text)).toBeInTheDocument();
      });
    });
  });
});