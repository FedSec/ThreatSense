export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  const authToken =
    token ??
    (typeof window !== "undefined" ? localStorage.getItem("ts_token") : null);
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
      if (Array.isArray(detail)) {
        detail = detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ts_token");
}

export function clearToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("ts_token");
  }
}
