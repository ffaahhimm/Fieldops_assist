"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login, user, isLoading } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // If already logged in, redirect immediately
  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/");
    }
  }, [isLoading, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username.trim(), password);
      router.replace("/");
    } catch {
      setError("Invalid username or password. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-white">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-100 border-t-teal-800" />
      </div>
    );
  }

  return (
    <div
      className="flex min-h-screen items-center justify-center"
      style={{ background: "#ffffff", fontFamily: "'Inter', system-ui, sans-serif" }}
    >
      <div
        className="w-full max-w-sm rounded-2xl p-8"
        style={{ background: "#ffffff", border: "1px solid #e2e8f0", boxShadow: "0 20px 60px rgba(15,92,91,0.08)" }}
      >
        {/* Logo */}
        <div className="mb-8 text-center">
          <div
            className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl text-white text-lg font-bold"
            style={{ background: "#0f5c5b", boxShadow: "0 4px 12px rgba(15,92,91,0.2)" }}
          >
            F
          </div>
          <h1 className="text-xl font-bold" style={{ color: "#111827" }}>FieldOps Assist</h1>
          <p className="mt-1 text-sm" style={{ color: "#6b7280" }}>IT &amp; Security Field Service</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-semibold" style={{ color: "#374151" }}>
              Username
            </label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={submitting}
              className="w-full rounded-lg px-3 py-2.5 text-sm transition"
              style={{ border: "1px solid #d1d5db", outline: "none", background: "#f9fafb" }}
              onFocus={(e) => {
                (e.currentTarget as HTMLInputElement).style.borderColor = "#54cfa0";
                (e.currentTarget as HTMLInputElement).style.background = "#fff";
              }}
              onBlur={(e) => {
                (e.currentTarget as HTMLInputElement).style.borderColor = "#d1d5db";
                (e.currentTarget as HTMLInputElement).style.background = "#f9fafb";
              }}
              placeholder="e.g. admin"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold" style={{ color: "#374151" }}>
              Password
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={submitting}
              className="w-full rounded-lg px-3 py-2.5 text-sm transition"
              style={{ border: "1px solid #d1d5db", outline: "none", background: "#f9fafb" }}
              onFocus={(e) => {
                (e.currentTarget as HTMLInputElement).style.borderColor = "#54cfa0";
                (e.currentTarget as HTMLInputElement).style.background = "#fff";
              }}
              onBlur={(e) => {
                (e.currentTarget as HTMLInputElement).style.borderColor = "#d1d5db";
                (e.currentTarget as HTMLInputElement).style.background = "#f9fafb";
              }}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div
              className="rounded-lg px-3 py-2.5 text-sm"
              style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}
            >
              {error}
            </div>
          )}

          <button
            id="login-submit"
            type="submit"
            disabled={submitting || !username || !password}
            className="mt-2 w-full rounded-xl py-2.5 text-sm font-semibold text-white transition"
            style={{
              background: submitting ? "#94a3b8" : "#0f5c5b",
              boxShadow: "0 4px 12px rgba(15,92,91,0.2)",
              cursor: submitting ? "not-allowed" : "pointer",
            }}
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {/* Demo credentials hint */}
        <div
          className="mt-6 rounded-lg p-3 text-xs"
          style={{ background: "#effaf5", border: "1px solid #b7ead2", color: "#0f5c5b" }}
        >
          <p className="font-semibold mb-1">Demo credentials</p>
          <p>Username: <code className="font-mono">admin</code> &nbsp; Password: <code className="font-mono">Admin@1234</code></p>
          <p className="mt-0.5">Username: <code className="font-mono">dispatcher</code> &nbsp; Password: <code className="font-mono">Dispatch@1234</code></p>
        </div>
      </div>
    </div>
  );
}
