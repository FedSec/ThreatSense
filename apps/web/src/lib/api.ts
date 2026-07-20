/**
 * Prefer same-origin `/api` (Next.js rewrite → backend).
 * Override with an absolute NEXT_PUBLIC_API_BASE only when calling the API directly.
 */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "/api";

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

  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;

  let res: Response;
  try {
    res = await fetch(url, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      "Cannot reach API. Is the backend running? (check API / docker compose)"
    );
  }

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
