"use client";

import "./globals.css";
import Link from "next/link";
import { usePathname } from "next/navigation";

function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 glass-strong hidden md:flex flex-col border-r border-border">
      <div className="p-5 border-b border-border">
        <h1 className="text-lg font-semibold text-warm tracking-tight">🍳 KitchenOS-AI</h1>
        <p className="text-[10px] text-muted mt-0.5">Japandi Kitchen Intelligence</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        <NavLink href="/" icon="💬" label="Chat" active={pathname === "/"} />
        <NavLink href="/history" icon="📜" label="History" active={pathname === "/history"} />
        <NavLink href="/knowledge" icon="📚" label="Knowledge Base" active={pathname === "/knowledge"} />
        <NavLink href="/finance" icon="💰" label="Finance & Costing" active={pathname === "/finance"} />
        <NavLink href="/settings" icon="⚙️" label="Settings" active={pathname === "/settings"} />
      </nav>

      <div className="p-4 border-t border-border">
        <p className="text-[9px] text-muted/60">Gemini 2.5 Flash • Groq • RAG</p>
        <p className="text-[9px] text-muted/60">v0.2.0</p>
      </div>
    </aside>
  );
}

function NavLink({ href, icon, label, active }: { href: string; icon: string; label: string; active: boolean }) {
  return (
    <Link href={href}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-japandi text-sm transition-colors ${
        active ? "text-white bg-white/5 border border-border" : "text-muted hover:text-white hover:bg-white/5"
      }`}>
      <span>{icon}</span><span>{label}</span>
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-bg">
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
