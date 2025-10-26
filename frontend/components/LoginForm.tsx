"use client";

import { FormEvent, useState } from "react";
import { authenticate } from "../lib/api";

type FormState = {
  username: string;
  password: string;
};

type LoginFormProps = {
  heading: string;
  endpoint: "/auth/login" | "/auth/admin/login";
  successStorageKey?: string;
};

export default function LoginForm({ heading, endpoint, successStorageKey }: LoginFormProps) {
  const [form, setForm] = useState<FormState>({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<unknown>();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await authenticate(endpoint, form);
      setResponse(result);
      if (successStorageKey && typeof window !== "undefined") {
        const token = (result as { token?: { access_token?: string } })?.token?.access_token;
        if (typeof token === "string") {
          window.localStorage.setItem(successStorageKey, token);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>{heading}</h2>
      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Username
          <input
            name="username"
            type="text"
            autoComplete="username"
            value={form.username}
            onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
            required
          />
        </label>

        <label>
          Password
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            required
          />
        </label>

        {error ? <p role="alert">⚠️ {error}</p> : null}

        <button type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      {response ? (
        <pre style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }}>{JSON.stringify(response, null, 2)}</pre>
      ) : null}
    </section>
  );
}
