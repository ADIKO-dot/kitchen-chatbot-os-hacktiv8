"use client";

import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface KeyEntry {
  index: number;
  masked: string;
  enabled: boolean;
  failures: number;
}

export default function SettingsPage() {
  const [geminiKeys, setGeminiKeys] = useState<KeyEntry[]>([]);
  const [groqKeys, setGroqKeys] = useState<KeyEntry[]>([]);
  const [newGemini, setNewGemini] = useState("");
  const [newGroq, setNewGroq] = useState("");

  const fetchKeys = async () => {
    try {
      const res = await fetch(`${API_BASE}/settings/api-keys`);
      const data = await res.json();
      setGeminiKeys(data.gemini || []);
      setGroqKeys(data.groq || []);
    } catch { /* empty */ }
  };

  useEffect(() => { fetchKeys(); }, []);

  const addKey = async (provider: string, key: string) => {
    if (!key.trim()) return;
    await fetch(`${API_BASE}/settings/api-keys/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, key: key.trim() }),
    });
    if (provider === "gemini") setNewGemini("");
    else setNewGroq("");
    fetchKeys();
  };

  const toggleKey = async (provider: string, index: number) => {
    await fetch(`${API_BASE}/settings/api-keys/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, index }),
    });
    fetchKeys();
  };

  const deleteKey = async (provider: string, index: number) => {
    await fetch(`${API_BASE}/settings/api-keys/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, index }),
    });
    fetchKeys();
  };

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold text-warm mb-1">⚙️ Settings</h1>
        <p className="text-sm text-muted mb-8">Manage API keys for LLM providers. Keys are stored in memory only.</p>

        {/* Gemini Keys */}
        <KeySection
          title="Gemini API Keys"
          subtitle="Google Gemini 2.5 Flash"
          keys={geminiKeys}
          newKey={newGemini}
          setNewKey={setNewGemini}
          onAdd={(key) => addKey("gemini", key)}
          onToggle={(idx) => toggleKey("gemini", idx)}
          onDelete={(idx) => deleteKey("gemini", idx)}
          placeholder="AIzaSy..."
        />

        {/* Groq Keys */}
        <KeySection
          title="Groq API Keys"
          subtitle="Groq (Llama 3.3 70B)"
          keys={groqKeys}
          newKey={newGroq}
          setNewKey={setNewGroq}
          onAdd={(key) => addKey("groq", key)}
          onToggle={(idx) => toggleKey("groq", idx)}
          onDelete={(idx) => deleteKey("groq", idx)}
          placeholder="gsk_..."
        />

        <div className="glass rounded-japandi p-4 mt-8">
          <p className="text-[11px] text-muted">
            💡 Keys yang aktif (hijau) akan digunakan secara bergantian (rotation). Jika satu key kena rate limit, sistem otomatis pindah ke key berikutnya.
          </p>
        </div>
      </div>
    </div>
  );
}

function KeySection({
  title, subtitle, keys, newKey, setNewKey, onAdd, onToggle, onDelete, placeholder,
}: {
  title: string; subtitle: string; keys: KeyEntry[];
  newKey: string; setNewKey: (v: string) => void;
  onAdd: (key: string) => void; onToggle: (idx: number) => void; onDelete: (idx: number) => void;
  placeholder: string;
}) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold text-white">{title}</h2>
          <p className="text-[10px] text-muted">{subtitle}</p>
        </div>
        <span className="text-[10px] text-accent">{keys.filter((k) => k.enabled).length} active</span>
      </div>

      {/* Key table */}
      {keys.length > 0 && (
        <div className="glass rounded-japandi overflow-hidden mb-3">
          <div className="grid grid-cols-[auto_1fr_auto] gap-0 text-[10px] text-muted uppercase tracking-wider px-4 py-2 border-b border-border">
            <span className="w-16">Active</span>
            <span>Value</span>
            <span className="w-16 text-right">Actions</span>
          </div>
          {keys.map((k) => (
            <div key={k.index} className="grid grid-cols-[auto_1fr_auto] gap-0 items-center px-4 py-3 border-b border-border last:border-0">
              {/* Toggle */}
              <div className="w-16">
                <button onClick={() => onToggle(k.index)}
                  className={`w-10 h-5 rounded-full relative transition-colors ${k.enabled ? "bg-accent" : "bg-border"}`}>
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${k.enabled ? "left-5" : "left-0.5"}`} />
                </button>
              </div>
              {/* Masked value — no select/copy */}
              <div className="select-none pointer-events-none">
                <span className="text-sm text-muted font-mono tracking-wider">
                  {k.masked}
                </span>
                {k.failures > 0 && (
                  <span className="ml-2 text-[9px] text-terracotta">({k.failures} failures)</span>
                )}
              </div>
              {/* Delete */}
              <div className="w-16 text-right">
                <button onClick={() => onDelete(k.index)}
                  className="text-xs text-terracotta/60 hover:text-terracotta p-1">
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add new key */}
      <div className="flex gap-2">
        <input
          type="password"
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAdd(newKey)}
          placeholder={placeholder}
          className="flex-1 bg-bg/50 border border-border rounded-japandi px-3 py-2 text-sm text-white placeholder-muted/40 font-mono"
        />
        <button
          onClick={() => onAdd(newKey)}
          disabled={!newKey.trim()}
          className="px-4 py-2 bg-accent text-white rounded-japandi text-sm font-medium hover:bg-accent-hover disabled:opacity-30"
        >
          + Add
        </button>
      </div>
    </div>
  );
}
