"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import API_URL from "@/lib/api-url";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const { login, user, loading } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.push("/");
    }
  }, [user, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "omit", // Cookies are returned by server, so omit is fine for sending, but fetch automatically stores Set-Cookie if the domain allows. Wait, since it's cross-origin, we MUST use "include" to allow Set-Cookie from server!
      });

      // Fix for cross-origin Set-Cookie
      // Wait, to receive Set-Cookie on cross-origin, credentials must be 'include'
    } catch (err) {
        // We will retry with include below
    }
  };

  const handleRealSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include", // Required to receive HttpOnly cookie
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Login failed" }));
        throw new Error(err.detail || "Login failed");
      }

      const data = await res.json();
      login(data.access_token, data.username);
      router.push("/");
    } catch (err: any) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  if (loading || user) return null; // Wait for redirect or loading

  return (
    <div className="flex items-center justify-center min-h-[100dvh] bg-[#0e1117]">
      <form onSubmit={handleRealSubmit} className="bg-[#13151c] border border-[#1e2230] rounded-2xl p-8 w-full max-w-md shadow-2xl flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-extrabold text-[#e4e6f0]">Welcome Back</h1>
          <p className="text-[#545872] text-sm mt-1">Sign in to continue to Chat-Z</p>
        </div>

        {error && (
          <div className="bg-[#e05678]/10 text-[#e05678] border border-[#e05678]/20 p-3 rounded-xl text-sm text-center">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">Username</label>
          <input
            type="text"
            required
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-4 py-3 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors placeholder:text-[#545872]"
            placeholder="Enter your username"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-4 py-3 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors placeholder:text-[#545872]"
            placeholder="Enter your password"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 w-full px-6 py-3.5 rounded-xl text-sm font-bold text-white bg-[#4f6ef7] hover:bg-[#3d5ce5] disabled:opacity-60 transition-colors shadow-lg shadow-[#4f6ef7]/20"
        >
          {submitting ? "Signing in..." : "Sign In"}
        </button>

        <div className="text-center text-sm text-[#545872] mt-2">
          Don't have an account? <Link href="/register" className="text-[#4f6ef7] hover:underline font-bold">Register</Link>
        </div>
      </form>
    </div>
  );
}
