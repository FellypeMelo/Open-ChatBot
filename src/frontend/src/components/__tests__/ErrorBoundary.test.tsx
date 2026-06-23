import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const ProblemChild = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary', () => {
  let consoleSpy: ReturnType<typeof vi.spyOn>;

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
    const originalLocation = window.location;
    const mockReload = vi.fn();

    const mockedLocation = {
      ...originalLocation,
      reload: mockReload,
    } as unknown as Location;

    Object.defineProperty(window, 'location', {
      writable: true,
      configurable: true,
      value: mockedLocation,
    });

    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('The application encountered an unexpected error. This has been logged for the archivists.')).toBeInTheDocument();

    const reloadButton = screen.getByRole('button', { name: 'Reload Interface' });
    fireEvent.click(reloadButton);
    expect(mockReload).toHaveBeenCalled();

    Object.defineProperty(window, 'location', {
      writable: true,
      configurable: true,
      value: originalLocation,
    });
  });
});
