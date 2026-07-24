import { Component, type ErrorInfo, type ReactNode } from 'react'
import Icon from './Icon'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[100dvh] w-full bg-background flex flex-col items-center justify-center p-md text-center">
          <Icon name="report_problem" size="xl" className="text-error mb-4" />
          <h1 className="font-heading-lg text-heading-lg text-primary mb-2">Something went wrong</h1>
          <p className="font-body-md text-on-surface-variant max-w-md mb-6">
            The application encountered an unexpected error. This has been logged for the archivists.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-lg py-xs bg-primary text-background rounded font-medium hover:bg-on-surface transition-colors"
          >
            Reload Interface
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
