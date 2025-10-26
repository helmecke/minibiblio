"use client";

import { useEffect, useState } from "react";

type DashboardState = {
  token?: string;
  error?: string | null;
};

export default function LibrarianDashboard() {
  const [state, setState] = useState<DashboardState>({ token: undefined, error: null });

  useEffect(() => {
    const savedToken = window.localStorage.getItem("minibiblio.librarian.token");
    if (!savedToken) {
      setState({ token: undefined, error: "Sign in via the librarian login to access this dashboard." });
      return;
    }

    const validate = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/auth/admin/health`, {
          headers: {
            authorization: `Bearer ${savedToken}`
          }
        });

        if (!response.ok) {
          throw new Error("Librarian token expired. Please sign in again.");
        }

        setState({ token: savedToken, error: null });
      } catch (error) {
        setState({
          token: undefined,
          error: error instanceof Error ? error.message : "Unable to verify librarian session."
        });
      }
    };

    validate().catch(() => undefined);
  }, []);

  return (
    <section className="card">
      <h2>Librarian Dashboard</h2>
      {state.error ? (
        <p role="alert">⚠️ {state.error}</p>
      ) : (
        <p>Use this space to surface inventory insights, pending approvals, or system metrics for librarians.</p>
      )}
    </section>
  );
}
