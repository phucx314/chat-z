"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import API_URL from "@/lib/api-url";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.push("/");
    }
  }, [user, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    if (username.length < 5 || username.length > 20) {
      return setError("Username must be between 5 and 20 characters");
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return setError("Username can only contain letters, numbers, and underscores");
    }
    
    if (password.length < 8) {
      return setError("Password must be at least 8 characters");
    }

    if (password !== confirmPassword) {
      return setError("Passwords do not match");
    }

    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "omit",
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Registration failed" }));
        throw new Error(err.detail || "Registration failed");
      }

      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: any) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  if (loading || user) return null;

  return (
    <div className="flex items-center justify-center min-h-[100dvh] bg-[#0e1117]">
      <form onSubmit={handleSubmit} className="bg-[#13151c] border border-[#1e2230] rounded-2xl p-8 w-full max-w-md shadow-2xl flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-extrabold text-[#e4e6f0]">Create Account</h1>
          <p className="text-[#545872] text-sm mt-1">Join Chat-Z today</p>
        </div>

        {error && (
          <div className="bg-[#e05678]/10 text-[#e05678] border border-[#e05678]/20 p-3 rounded-xl text-sm text-center">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-[#25a56a]/10 text-[#25a56a] border border-[#25a56a]/20 p-3 rounded-xl text-sm text-center">
            Registration successful! Redirecting to login...
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
            placeholder="Choose a username"
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
            placeholder="Create a strong password"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">Confirm Password</label>
          <input
            type="password"
            required
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-4 py-3 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors placeholder:text-[#545872]"
            placeholder="Confirm your password"
          />
        </div>

        <button
          type="submit"
          disabled={submitting || success}
          className="mt-2 w-full px-6 py-3.5 rounded-xl text-sm font-bold text-white bg-[#4f6ef7] hover:bg-[#3d5ce5] disabled:opacity-60 transition-colors shadow-lg shadow-[#4f6ef7]/20"
        >
          {submitting ? "Registering..." : "Create Account"}
        </button>

        <div className="text-center text-sm text-[#545872] mt-2">
          Already have an account? <Link href="/login" className="text-[#4f6ef7] hover:underline font-bold">Sign In</Link>
        </div>
      </form>
    </div>
  );
}
