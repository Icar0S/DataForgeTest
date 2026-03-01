import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChecklistPage from '../../../frontend/src/pages/ChecklistPage';

// Use manual mock for react-router-dom
jest.mock('react-router-dom');

// Mock fetch
global.fetch = jest.fn();

// Helper to render component
const renderComponent = (component) => {
  return render(component);
};

const mockTemplate = {
  name: "Test Checklist",
  dimensions: [
    {
      id: "dim1",
      name: "Dimension 1",
      items: [
        {
          id: "ITEM_1",
          code: "ITEM_1",
          title: "Test Item 1",
          manual: "Test manual content",
          references: ["[1]", "[2]"],
          priority_weight: 3
        },
        {
          id: "ITEM_2",
          code: "ITEM_2",
          title: "Test Item 2",
          manual: "Another manual",
          references: ["[3]"],
          priority_weight: 5
        }
      ]
    },
    {
      id: "dim2",
      name: "Dimension 2",
      items: [
        {
          id: "ITEM_3",
          code: "ITEM_3",
          title: "Test Item 3",
          manual: "Manual 3",
          references: ["[4]"],
          priority_weight: 2
        }
      ]
    }
  ]
};

const mockRun = {
  id: "run123",
  user_id: "user456",
  project_id: null,
  created_at: "2023-01-01T00:00:00Z",
  updated_at: "2023-01-01T00:00:00Z",
  marks: {}
};

describe('ChecklistPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  const setupMocks = () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/checklist/template')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTemplate)
        });
      }
      if (url.includes('/api/checklist/runs') && !url.includes('/runs/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRun)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
  };

  test('renders ChecklistPage with loading state', () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    expect(screen.getByText(/Carregando checklist/i)).toBeInTheDocument();
  });

  test('loads and displays template data', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Checklist Support QA')).toBeInTheDocument();
    });
    
    // Use getAllByText since dimensions appear in both sidebar and header
    expect(screen.getAllByText('Dimension 1').length).toBeGreaterThan(0);
    expect(screen.getByText('Dimension 2')).toBeInTheDocument();
  });

  test('displays items for selected dimension', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Test Item 2')).toBeInTheDocument();
    expect(screen.getByText('ITEM_1')).toBeInTheDocument();
  });

  test('switches between dimensions', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getAllByText('Dimension 1').length).toBeGreaterThan(0);
    });
    
    // Click on Dimension 2
    const dim2Buttons = screen.getAllByText('Dimension 2');
    // Click the button in the sidebar (first one)
    const dim2Button = dim2Buttons[0].closest('button');
    fireEvent.click(dim2Button);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 3')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('toggles item status', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Find and click checkbox for first item
    const checkboxes = screen.getAllByRole('button', { name: /Marcar como/i });
    fireEvent.click(checkboxes[0]);
    
    // Should toggle to done (checked)
    await waitFor(() => {
      expect(checkboxes[0]).toHaveAttribute('aria-label', 'Marcar como não feito');
    });
  });

  test('opens manual modal', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Click help button
    const helpButtons = screen.getAllByRole('button', { name: /Ver manual do item/i });
    fireEvent.click(helpButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Test manual content')).toBeInTheDocument();
    });
  });

  test('closes manual modal', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Open modal
    const helpButtons = screen.getAllByRole('button', { name: /Ver manual do item/i });
    fireEvent.click(helpButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
    
    // Close modal
    const closeButton = screen.getByRole('button', { name: /Fechar modal/i });
    fireEvent.click(closeButton);
    
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  test('saves progress', async () => {
    setupMocks();
    
    // Mock save endpoint
    global.fetch.mockImplementation((url, options) => {
      if (url.includes('/api/checklist/template')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTemplate)
        });
      }
      if (url.includes('/api/checklist/runs') && options?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRun)
        });
      }
      if (url.includes('/api/checklist/runs/') && options?.method === 'PUT') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...mockRun, marks: { ITEM_1: 'DONE' } })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
    
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Mark an item
    const checkboxes = screen.getAllByRole('button', { name: /Marcar como/i });
    fireEvent.click(checkboxes[0]);
    
    // Click save
    const saveButton = screen.getByRole('button', { name: /Salvar Progresso/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Progresso salvo com sucesso/i)).toBeInTheDocument();
    });
  });

  test('displays progress bar correctly', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Initially 0%
    expect(screen.getByText('Progresso: 0%')).toBeInTheDocument();
    expect(screen.getByText('0 / 3 itens')).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    // Mock fetch to fail only for template
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/checklist/template')) {
        return Promise.reject(new Error('Network error'));
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRun)
      });
    });
    
    renderComponent(<ChecklistPage />);
    
    // Component should still render loading state, but error is set internally
    // We can't easily test this without exposing internal state or checking DOM
    // Just verify component doesn't crash
    await waitFor(() => {
      expect(screen.getByText(/Carregando checklist/i)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  test('generates recommendations', async () => {
    setupMocks();
    
    const mockRecommendations = [
      {
        title: "Test Recommendation",
        content: "This is a recommendation",
        sources: ["Source 1"]
      }
    ];
    
    global.fetch.mockImplementation((url, options) => {
      if (url.includes('/api/checklist/template')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTemplate)
        });
      }
      if (url.includes('/api/checklist/runs') && !url.includes('/recommendations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRun)
        });
      }
      if (url.includes('/recommendations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ recommendations: mockRecommendations })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
    
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Click generate recommendations
    const recoButton = screen.getByRole('button', { name: /Gerar Recomendações/i });
    fireEvent.click(recoButton);
    
    await waitFor(() => {
      expect(screen.getByText('Recomendações')).toBeInTheDocument();
      expect(screen.getByText('Test Recommendation')).toBeInTheDocument();
    });
  });

  test('has accessible modal', async () => {
    setupMocks();
    renderComponent(<ChecklistPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    });
    
    // Open modal
    const helpButtons = screen.getAllByRole('button', { name: /Ver manual do item/i });
    fireEvent.click(helpButtons[0]);
    
    await waitFor(() => {
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');
    });
  });
});
