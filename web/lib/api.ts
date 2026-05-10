const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// === Chat ===
export async function sendMessage(
  message: string,
  sessionId?: string,
  tone?: string,
  context?: Record<string, unknown>
) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, tone, context }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function sendMessageWithFile(
  file: File,
  message: string,
  sessionId?: string,
  tone?: string
) {
  const params = new URLSearchParams({ message });
  if (sessionId) params.set("session_id", sessionId);
  if (tone) params.set("tone", tone);
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/chat/image?${params}`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// === History ===
export async function getSessions() {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error("Failed to fetch sessions");
  return res.json();
}

export async function getHistory(sessionId: string) {
  const res = await fetch(`${API_BASE}/history/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export async function clearHistory(sessionId: string) {
  const res = await fetch(`${API_BASE}/history/${sessionId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to clear history");
  return res.json();
}

// === RAG ===
export async function getRAGDocuments() {
  const res = await fetch(`${API_BASE}/rag/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function uploadToRAG(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/rag/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function deleteRAGDocument(docId: string) {
  const res = await fetch(`${API_BASE}/rag/${docId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete");
  return res.json();
}

// === Finance ===
export async function calculateFoodCost(costOfGoods: number, revenue: number) {
  const res = await fetch(`${API_BASE}/finance/food-cost`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cost_of_goods: costOfGoods, revenue }),
  });
  if (!res.ok) throw new Error("Calculation failed");
  return res.json();
}

export async function calculateMenuPrice(costPerPortion: number, targetFoodCostPct: number) {
  const res = await fetch(`${API_BASE}/finance/menu-price`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cost_per_portion: costPerPortion, target_food_cost_pct: targetFoodCostPct }),
  });
  if (!res.ok) throw new Error("Calculation failed");
  return res.json();
}

// === Waste ===
export async function addWaste(item: string, qty: number, unit: string, costPerUnit: number, reason: string) {
  const res = await fetch(`${API_BASE}/waste/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item, qty, unit, cost_per_unit: costPerUnit, reason }),
  });
  if (!res.ok) throw new Error("Failed to log waste");
  return res.json();
}

export async function getWasteSummary() {
  const res = await fetch(`${API_BASE}/waste/summary`);
  if (!res.ok) throw new Error("Failed to fetch waste");
  return res.json();
}

export async function getWasteWeekly() {
  const res = await fetch(`${API_BASE}/waste/weekly`);
  if (!res.ok) throw new Error("Failed to fetch waste");
  return res.json();
}

// === Settings ===
export async function getApiKeys() {
  const res = await fetch(`${API_BASE}/settings/api-keys`);
  if (!res.ok) throw new Error("Failed to get keys");
  return res.json();
}

export async function addApiKey(provider: string, key: string) {
  const res = await fetch(`${API_BASE}/settings/api-keys/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, key }),
  });
  if (!res.ok) throw new Error("Failed to add key");
  return res.json();
}

export async function toggleApiKey(provider: string, index: number) {
  const res = await fetch(`${API_BASE}/settings/api-keys/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, index }),
  });
  if (!res.ok) throw new Error("Failed to toggle");
  return res.json();
}

export async function deleteApiKey(provider: string, index: number) {
  const res = await fetch(`${API_BASE}/settings/api-keys/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, index }),
  });
  if (!res.ok) throw new Error("Failed to delete");
  return res.json();
}
