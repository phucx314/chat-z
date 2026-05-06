"use client";
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { setAccessToken } from "@/lib/api";
import API_URL from "@/lib/api-url";

interface User {
  username: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (token: string, username: string) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in by hitting the refresh token endpoint on mount
    fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
      if (data.access_token) {
        setAccessToken(data.access_token);
        setUser({ username: data.username });
      }
    })
    .catch(() => {
      // Not logged in, that's fine
    })
    .finally(() => {
      setLoading(false);
    });
  }, []);

  const login = (token: string, username: string) => {
    setAccessToken(token);
    setUser({ username });
  };

  const logout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include"
      });
    } catch (e) {
      console.error("Logout failed", e);
    }
    setAccessToken("");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
