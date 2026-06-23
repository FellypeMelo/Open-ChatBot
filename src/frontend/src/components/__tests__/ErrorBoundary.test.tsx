import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const ProblemChild = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary', () => {
  let consoleSpy: any;

  beforeEach(() => {
    consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  it('should render children if no error is thrown', () => {
    render(
      <ErrorBoundary>
        <div>Normal Content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Normal Content')).toBeInTheDocument();
  });

  it('should catch error and render fallback UI with reload button', () => {
    const { location } = window;
    delete (window as any).location;
    window.location = { reload: vi.fn() } as any;

    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('The application encountered an unexpected error. This has been logged for the archivists.')).toBeInTheDocument();

    const reloadButton = screen.getByRole('button', { name: 'Reload Interface' });
    fireEvent.click(reloadButton);
    expect(window.location.reload).toHaveBeenCalled();

    window.location = location; // restore
  });
});
