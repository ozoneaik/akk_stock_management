export class ApiClientError extends Error {}

export async function apiFetch<T>(input: string, init?: RequestInit): Promise<T> {
  const res = await fetch(input, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiClientError(data?.error ?? "เกิดข้อผิดพลาดที่ไม่คาดคิดในระบบ");
  }
  return data as T;
}
