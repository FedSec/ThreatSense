import * as SecureStore from "expo-secure-store";

export const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE || "http://localhost:8000";

const TOKEN_KEY = "ts_token";

export async function getToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return null;
  }
}

export async function setToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  const token = await getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
      if (Array.isArray(detail)) {
        detail = detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}
