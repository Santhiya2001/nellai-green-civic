import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/**
 * Without this, any uncaught render error (e.g. rendering a non-string
 * value where JSX expects text -- see utils/errors.ts for a real case
 * that hit exactly this) unmounts the whole React tree, leaving a blank
 * white page with zero indication of what happened. Catches that instead.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled UI error:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
          <div className="card" style={{ maxWidth: 420, textAlign: "center" }}>
            <h3>Something went wrong</h3>
            <p className="muted">
              This page hit an unexpected error. Reloading usually fixes it -- if it keeps
              happening, please let us know what you were doing.
            </p>
            <button className="btn" style={{ marginTop: 12 }} onClick={() => window.location.reload()}>
              Reload page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
