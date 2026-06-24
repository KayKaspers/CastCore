import { create } from "zustand";

import { setLanguage } from "../i18n";

const BASE = "/api/v1";

export interface AuthUser {
  id: string;
  username: string;
  email: string | null;
  language: string;
  roles: string[];
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<void>;
  refresh: () => Promise<boolean>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

const LS = {
  access: "castcore.access",
  refresh: "castcore.refresh",
  user: "castcore.user",
};

function loadUser(): AuthUser | null {
  const raw = localStorage.getItem(LS.user);
  return raw ? (JSON.parse(raw) as AuthUser) : null;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: localStorage.getItem(LS.access),
  refreshToken: localStorage.getItem(LS.refresh),
  user: loadUser(),

  login: async (username, password) => {
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body?.detail?.error?.code ?? "auth.invalid_credentials");
    }
    const data = await res.json();
    localStorage.setItem(LS.access, data.access_token);
    localStorage.setItem(LS.refresh, data.refresh_token);
    localStorage.setItem(LS.user, JSON.stringify(data.user));
    if (data.user?.language) setLanguage(data.user.language);
    set({ accessToken: data.access_token, refreshToken: data.refresh_token, user: data.user });
  },

  refresh: async () => {
    const rt = get().refreshToken;
    if (!rt) return false;
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem(LS.access, data.access_token);
    localStorage.setItem(LS.refresh, data.refresh_token);
    set({ accessToken: data.access_token, refreshToken: data.refresh_token });
    return true;
  },

  logout: () => {
    localStorage.removeItem(LS.access);
    localStorage.removeItem(LS.refresh);
    localStorage.removeItem(LS.user);
    set({ accessToken: null, refreshToken: null, user: null });
  },

  hasRole: (...roles) => {
    const u = get().user;
    if (!u) return false;
    if (u.roles.includes("admin")) return true;
    return roles.some((r) => u.roles.includes(r));
  },
}));
