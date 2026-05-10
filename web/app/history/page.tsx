"use client";

import { useState, useEffect } from "react";
import { getSessions, getHistory, clearHistory } from "@/lib/api";

interface Session { session_id: string; message_count: number; last_message: string; first_message: string; }
interface Message { role: string; content: string; }

export default function HistoryPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchSessions(); }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try { const data = await getSessions(); setSessions(data.sessions || []); } catch { /* empty */ }
    setLoading(false);
  };

  const openSession = async (sid: string) => {
    setSelected(sid);
    const data = await getHistory(sid);
    setMessages(data.messages || []);
  };

  const deleteSession = async (sid: string) => {
    await clearHistory(sid);
    setSessions((prev) => prev.filter((s) => s.session_id !== sid));
    if (selected === sid) { setSelected(null); setMessages([]); }
  };

  return (
    <div className="flex h-full">
      {/* Session list */}
      <div className="w-80 glass-strong border-r border-border overflow-y-auto">
        <div className="p-5 border-b border-border">
          <h2 className="text-lg font-semibold text-warm">📜 Chat History</h2>
          <p className="text-[11px] text-muted mt-1">{sessions.length} sessions</p>
        </div>
        {loading ? (
          <p className="p-5 text-muted text-sm">Loading...</p>
        ) : sessions.length === 0 ? (
          <p className="p-5 text-muted text-sm">No chat history yet.</p>
        ) : (
          <div className="divide-y divide-border">
            {sessions.map((s) => (
              <div key={s.session_id} onClick={() => openSession(s.session_id)}
                className={`p-4 cursor-pointer hover:bg-white/5 transition-colors ${selected === s.session_id ? "bg-white/5" : ""}`}>
                <p className="text-sm text-white truncate">{s.first_message}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-[10px] text-muted">{s.message_count} messages</span>
                  <button onClick={(e) => { e.stopPropagation(); deleteSession(s.session_id); }}
                    className="text-[10px] text-terracotta/70 hover:text-terracotta">🗑️ Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {!selected ? (
          <div className="text-center text-muted mt-20">
            <p className="text-4xl mb-4">📜</p>
            <p>Select a session to view conversation</p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm text-muted">Session: {selected.slice(0, 8)}...</h3>
              <button onClick={() => { setSelected(null); setMessages([]); }}
                className="text-xs text-muted hover:text-white">← Back</button>
            </div>
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[75%] rounded-japandi px-4 py-3 text-sm ${
                  msg.role === "user" ? "bg-accent/20 text-white border border-accent/20" : "glass text-gray-200"
                }`}>
                  <span className="text-[9px] text-muted block mb-1">{msg.role === "user" ? "👤 You" : "🤖 Assistant"}</span>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
