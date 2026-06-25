import i18n from "../i18n";
import { useAuthStore } from "./auth";

const BASE = "/api/v1";

export class ApiException extends Error {
  code: string;
  params: Record<string, unknown>;
  status: number;

  constructor(status: number, code: string, params: Record<string, unknown> = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.params = params;
  }

  /** Localised, human-readable message via the i18n error.* keys. */
  get localized(): string {
    const key = `error.${this.code}`;
    const translated = i18n.t(key, this.params);
    return translated === key ? this.code : translated;
  }
}

async function request<T>(path: string, options: RequestInit = {}, allowRetry = true): Promise<T> {
  const { accessToken, refresh, logout } = useAuthStore.getState();
  const headers = new Headers(options.headers);
  if (options.body) headers.set("content-type", "application/json");
  if (accessToken) headers.set("authorization", `Bearer ${accessToken}`);

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && allowRetry && accessToken) {
    if (await refresh()) return request<T>(path, options, false);
    logout();
  }

  if (!res.ok) {
    let code = "validation.failed";
    let params: Record<string, unknown> = {};
    try {
      const body = await res.json();
      const err = body?.detail?.error ?? body?.error;
      if (err?.code) {
        code = err.code;
        params = err.params ?? {};
      }
    } catch {
      /* non-JSON error body */
    }
    throw new ApiException(res.status, code, params);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
