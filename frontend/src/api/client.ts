// the single place the frontend talks to the backend.

import type {
    ChatResponse,
    Stats,
    TradeFilters,
    TradePage,
  } from "./types";
  
  const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`API ${res.status}: ${body}`);
    }
    return res.json() as Promise<T>;
  }
  
  function toQuery(filters: TradeFilters): string {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== "") params.set(key, String(value));
    });
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }
  
  export const api = {
    getStats: () => request<Stats>("/stats"),
    getTickers: () => request<string[]>("/tickers"),
    getTrades: (filters: TradeFilters = {}) =>
      request<TradePage>(`/trades${toQuery(filters)}`),
    sync: (source?: string) =>
      request<{ inserted: number; updated: number; total_in_db: number }>(
        `/admin/sync${source ? `?source=${source}` : ""}`,
        { method: "POST" },
      ),
    chat: (message: string, history: { role: string; content: string }[] = []) =>
      request<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ message, history }),
      }),
  };
  