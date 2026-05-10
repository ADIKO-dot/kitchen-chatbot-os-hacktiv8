"use client";

import { useRef, useState } from "react";

interface FileUploadProps {
  onUpload: (file: File, caption: string) => void;
  disabled?: boolean;
}

export default function FileUpload({ onUpload, disabled }: FileUploadProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (file: File) => {
    const caption = prompt("Add a message with this file (optional):") || "";
    onUpload(file, caption);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <>
      <input ref={fileRef} type="file" className="hidden" onChange={handleChange} accept="image/*,.pdf,.xlsx,.csv,.doc,.docx" />
      <button
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        disabled={disabled}
        className={`p-2.5 rounded-japandi border text-sm transition-colors ${
          dragOver ? "border-accent bg-accent/10" : "border-border hover:border-accent/40 text-muted hover:text-accent"
        } disabled:opacity-40`}
        title="Upload file"
      >
        📎
      </button>
    </>
  );
}
