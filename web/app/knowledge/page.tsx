"use client";

import { useState, useEffect, useRef } from "react";
import { getRAGDocuments, uploadToRAG, deleteRAGDocument } from "@/lib/api";

interface Doc { id: string; text: string; metadata: Record<string, string>; }

export default function KnowledgePage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    setLoading(true);
    try { const data = await getRAGDocuments(); setDocs(data.documents || []); setCount(data.count || 0); } catch { /* empty */ }
    setLoading(false);
  };

  useEffect(() => { fetchDocs(); }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    setUploading(true); setMsg(null);
    try {
      const result = await uploadToRAG(file);
      setMsg(`✅ "${result.filename}" — ${result.chunks} chunks, ${result.total_chars} chars`);
      fetchDocs();
    } catch (err: unknown) { setMsg(`❌ ${err instanceof Error ? err.message : "Failed"}`); }
    setUploading(false);
  };

  const handleDelete = async (docId: string) => {
    if (!confirm(`Delete "${docId}"?`)) return;
    await deleteRAGDocument(docId);
    setDocs((prev) => prev.filter((d) => d.id !== docId));
    setCount((c) => c - 1);
  };

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-warm">📚 Knowledge Base</h1>
            <p className="text-sm text-muted mt-1">{count} documents in vector store (ChromaDB)</p>
          </div>
          <div>
            <input ref={fileRef} type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.txt,.csv,.xlsx" />
            <button onClick={() => fileRef.current?.click()} disabled={uploading}
              className="px-4 py-2 bg-accent text-white rounded-japandi text-sm font-medium hover:bg-accent-hover disabled:opacity-40">
              {uploading ? "⏳ Uploading..." : "📤 Upload File"}
            </button>
          </div>
        </div>

        {/* Status */}
        {msg && (
          <div className={`p-3 rounded-japandi mb-4 text-sm ${msg.startsWith("✅") ? "bg-accent/10 text-accent border border-accent/20" : "bg-terracotta/10 text-terracotta border border-terracotta/20"}`}>
            {msg}
          </div>
        )}

        {/* Info */}
        <div className="glass rounded-japandi p-4 mb-6">
          <p className="text-xs text-muted">Supported: <span className="text-warm">PDF, DOCX, TXT, CSV, XLSX</span></p>
          <p className="text-[10px] text-muted/60 mt-1">Files are split with RecursiveCharacterTextSplitter and embedded for semantic search.</p>
        </div>

        {/* Documents */}
        {loading ? (
          <p className="text-muted">Loading...</p>
        ) : docs.length === 0 ? (
          <div className="text-center py-16 text-muted">
            <p className="text-4xl mb-4">📭</p>
            <p>Knowledge base is empty.</p>
            <p className="text-xs mt-2">Upload files or run <code className="bg-surface-solid px-1.5 py-0.5 rounded text-warm">python seed_knowledge.py</code></p>
          </div>
        ) : (
          <div className="space-y-2">
            {docs.map((doc) => (
              <div key={doc.id} className="glass rounded-japandi p-4 hover:border-accent/30 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium text-white">{doc.id}</span>
                      {doc.metadata?.source && (
                        <span className="text-[9px] px-2 py-0.5 bg-accent/15 text-accent rounded-full">{doc.metadata.source}</span>
                      )}
                      {doc.metadata?.category && (
                        <span className="text-[9px] px-2 py-0.5 bg-warm/15 text-warm rounded-full">{doc.metadata.category}</span>
                      )}
                    </div>
                    <p className="text-[11px] text-muted mt-2 line-clamp-2 leading-relaxed">{doc.text}</p>
                  </div>
                  <button onClick={() => handleDelete(doc.id)}
                    className="ml-4 text-[10px] text-terracotta/60 hover:text-terracotta shrink-0">🗑️</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
