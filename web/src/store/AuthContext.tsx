import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (fullName: string, email: string, phone: string, password: string) => Promise<User>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

export function homePathForRoles(roles: string[]): string {
  if (roles.includes("ADMIN") || roles.includes("SUPER_ADMIN")) return "/admin";
  if (roles.includes("AUTHORITY")) return "/authority";
  return "/citizen";
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadMe(): Promise<User> {
    const { data } = await apiClient.get<User>("/auth/me");
    setUser(data);
    return data;
  }

  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      loadMe()
        .catch(() => setUser(null))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(email: string, password: string): Promise<User> {
    const { data } = await apiClient.post("/auth/login", { email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return loadMe();
  }

  async function register(full_name: string, email: string, phone: string, password: string): Promise<User> {
    await apiClient.post("/auth/register", { full_name, email, phone: phone || null, password });
    return login(email, password);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }

  function hasRole(...roles: string[]) {
    if (!user) return false;
    return user.roles.some((r) => roles.includes(r));
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
