import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ResearchForm } from '../components/ResearchForm';

describe('ResearchForm Component', () => {
  it('renders research topic input and submit button', () => {
    const handleSubmit = vi.fn();
    render(<ResearchForm onSubmit={handleSubmit} isLoading={false} />);

    expect(screen.getByLabelText(/Primary Research Question or Topic/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Start Autonomous Research/i })).toBeInTheDocument();
  });

  it('validates minimum topic length', () => {
    const handleSubmit = vi.fn();
    render(<ResearchForm onSubmit={handleSubmit} isLoading={false} />);

    const textarea = screen.getByLabelText(/Primary Research Question or Topic/i);
    fireEvent.change(textarea, { target: { value: 'ab' } });

    const submitBtn = screen.getByRole('button', { name: /Start Autonomous Research/i });
    fireEvent.click(submitBtn);

    expect(screen.getByText(/Please enter a research topic of at least 3 characters/i)).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid research parameters', () => {
    const handleSubmit = vi.fn();
    render(<ResearchForm onSubmit={handleSubmit} isLoading={false} />);

    const textarea = screen.getByLabelText(/Primary Research Question or Topic/i);
    fireEvent.change(textarea, { target: { value: 'Generative AI Developer Productivity' } });

    const submitBtn = screen.getByRole('button', { name: /Start Autonomous Research/i });
    fireEvent.click(submitBtn);

    expect(handleSubmit).toHaveBeenCalledWith({
      topic: 'Generative AI Developer Productivity',
      scope: undefined,
      depth: 'standard',
      max_sources: 4,
    });
  });
});
