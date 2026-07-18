import { apiFetch, clearToken, getToken } from "./api";

export async function requireAuth(): Promise<string> {
  const token = getToken();
  if (!token) {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Not authenticated");
  }
  return token;
}

export async function fetchMe() {
  return apiFetch("/auth/me");
}

export function logout() {
  clearToken();
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}
