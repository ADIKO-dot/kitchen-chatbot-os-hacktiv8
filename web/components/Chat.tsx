"use client";

import { useState, useRef, useEffect } from "react";
import { sendMessage, sendMessageWithFile, uploadToRAG } from "@/lib/api";
import FileUpload from "./FileUpload";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: Date;
}

type Tone = "friendly" | "formal" | "casual";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tone, setTone] = useState<Tone>("friendly");
  const [sessionId, setSessionId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [ragUploading, setRagUploading] = useState(false);
  const ragFileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Restore chat from sessionStorage on mount, then sync with backend
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("chat_messages");
      const savedSid = sessionStorage.getItem("chat_session_id");
      const savedTone = sessionStorage.getItem("chat_tone") as Tone | null;
      if (saved) setMessages(JSON.parse(saved).map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) })));
      if (savedSid) {
        setSessionId(savedSid);
        // Sync with backend in case response arrived while away
        fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/history/${savedSid}`)
          .then(r => r.json())
          .then(data => {
            if (data.messages && data.messages.length > 0) {
              const localCount = saved ? JSON.parse(saved).length : 0;
              if (data.messages.length > localCount) {
                // Backend has newer messages — rebuild from backend
                const rebuilt: Message[] = data.messages.map((m: { role: string; content: string }, i: number) => ({
                  id: `restored-${i}`,
                  role: m.role as "user" | "assistant",
                  content: m.content,
                  timestamp: new Date(),
                }));
                setMessages(rebuilt);
                sessionStorage.setItem("chat_messages", JSON.stringify(rebuilt));
              }
            }
          })
          .catch(() => {});
      } else {
        setSessionId(crypto.randomUUID());
      }
      if (savedTone) setTone(savedTone);
    } catch { setSessionId(crypto.randomUUID()); }
  }, []);

  // Save session metadata to sessionStorage
  useEffect(() => {
    if (sessionId) sessionStorage.setItem("chat_session_id", sessionId);
  }, [sessionId]);
  useEffect(() => { sessionStorage.setItem("chat_tone", tone); }, [tone]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const addMessage = (role: "user" | "assistant", content: string, agent?: string) => {
    setMessages((prev) => {
      const updated = [...prev, { id: crypto.randomUUID(), role, content, agent, timestamp: new Date() }];
      sessionStorage.setItem("chat_messages", JSON.stringify(updated));
      return updated;
    });
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;
    addMessage("user", text);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const data = await sendMessage(text, sessionId, tone);
      if (data.session_id) setSessionId(data.session_id);
      const response = typeof data.response === "object" ? data.response.message || JSON.stringify(data.response) : data.response;
      addMessage("assistant", response, data.agent);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(msg);
      addMessage("assistant", `❌ ${msg}`);
    } finally { setLoading(false); }
  };

  const handleFileUpload = async (file: File, caption: string) => {
    addMessage("user", `📎 ${file.name}${caption ? `: ${caption}` : ""}`);
    setLoading(true);
    setError(null);
    try {
      const data = await sendMessageWithFile(file, caption, sessionId, tone);
      if (data.session_id) setSessionId(data.session_id);
      const response = typeof data.response === "object" ? data.response.message || JSON.stringify(data.response) : data.response;
      addMessage("assistant", response, data.agent);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally { setLoading(false); }
  };

  const handleRAGUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    setRagUploading(true);
    try {
      const result = await uploadToRAG(file);
      addMessage("assistant", `📚 "${result.filename}" added to Knowledge Base — ${result.chunks} chunks`, "rag");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally { setRagUploading(false); }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(crypto.randomUUID());
    setError(null);
    sessionStorage.removeItem("chat_messages");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 py-3 glass border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-muted uppercase tracking-wider">Tone</span>
          {(["friendly", "formal", "casual"] as Tone[]).map((t) => (
            <button key={t} onClick={() => setTone(t)}
              className={`px-2.5 py-1 text-[11px] rounded-japandi transition-colors ${
                tone === t ? "bg-accent/20 text-accent" : "text-muted hover:text-white hover:bg-white/5"
              }`}>
              {t === "friendly" ? "😊 Friendly" : t === "formal" ? "👔 Formal" : "😎 Casual"}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input ref={ragFileRef} type="file" className="hidden" onChange={handleRAGUpload} accept=".pdf,.docx,.txt,.csv,.xlsx" />
          <button onClick={() => ragFileRef.current?.click()} disabled={ragUploading}
            className="px-3 py-1 text-[11px] text-muted hover:text-accent border border-border rounded-japandi hover:border-accent/40 disabled:opacity-40">
            {ragUploading ? "⏳..." : "📚 Upload RAG"}
          </button>
          <button onClick={handleNewChat}
            className="px-3 py-1 text-[11px] text-muted hover:text-white border border-border rounded-japandi hover:border-white/20">
            + New
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="px-5 py-2 bg-terracotta/10 border-b border-terracotta/30 text-terracotta text-xs flex justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="hover:text-white">✕</button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.length === 0 && (
          <div className="text-center mt-20">
            <p className="text-4xl mb-4">🍳</p>
            <p className="text-lg font-medium text-warm">KitchenOS-AI</p>
            <p className="text-sm text-muted mt-2">Your intelligent kitchen assistant</p>
            <div className="mt-8 grid grid-cols-2 gap-3 max-w-md mx-auto">
              {[
                { icon: "🍚", text: "Resep nasi goreng spesial" },
                { icon: "📋", text: "SOP keamanan pangan" },
                { icon: "💡", text: "Rekomendasikan menu hari ini" },
                { icon: "💰", text: "Hitung food cost COGS 5jt revenue 15jt" },
              ].map((q) => (
                <button key={q.text} onClick={() => setInput(q.text)}
                  className="p-3 glass rounded-japandi text-left text-xs text-muted hover:text-white hover:border-accent/30 transition-colors">
                  <span className="block mb-1">{q.icon}</span>{q.text}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {/* AI Avatar */}
            {msg.role === "assistant" && (
              <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent/80 to-accent/30 flex items-center justify-center shadow-lg shadow-accent/10">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white">
                  <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
                  <path d="M18 14a6 6 0 0 0-12 0v4a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4z"/>
                  <circle cx="9" cy="7" r="0.5" fill="currentColor"/>
                  <circle cx="15" cy="7" r="0.5" fill="currentColor"/>
                </svg>
              </div>
            )}
            <div className={`max-w-[70%] rounded-japandi px-4 py-3 text-sm ${
              msg.role === "user"
                ? "bg-accent/20 text-white border border-accent/20"
                : "glass text-gray-200"
            }`}>
              {msg.agent && <span className="text-[10px] text-accent block mb-1">🤖 {msg.agent}</span>}
              <div className="prose-chat">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
              <span className="text-[9px] text-muted/60 mt-2 block">{msg.timestamp.toLocaleTimeString()}</span>
            </div>
            {/* User Avatar */}
            {msg.role === "user" && (
              <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-warm/80 to-terracotta/40 flex items-center justify-center shadow-lg shadow-warm/10">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
                </svg>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent/80 to-accent/30 flex items-center justify-center animate-pulse shadow-lg shadow-accent/10">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white">
                <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
                <path d="M18 14a6 6 0 0 0-12 0v4a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4z"/>
              </svg>
            </div>
            <div className="glass rounded-japandi px-4 py-3 text-sm text-muted animate-pulse">⏳ Thinking...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 glass border-t border-border">
        <div className="flex items-center gap-3 max-w-4xl mx-auto">
          <FileUpload onUpload={handleFileUpload} disabled={loading} />
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Ask KitchenOS-AI anything..."
            className="flex-1 bg-bg/50 border border-border rounded-japandi px-4 py-2.5 text-sm text-white placeholder-muted/50"
            disabled={loading} />
          <button onClick={handleSend} disabled={loading || !input.trim()}
            className="px-5 py-2.5 bg-accent text-white rounded-japandi text-sm font-medium disabled:opacity-40 hover:bg-accent-hover transition-colors">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
