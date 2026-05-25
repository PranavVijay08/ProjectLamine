import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Project Lamine | Player DNA",
  description: "Football player similarity and scouting dashboard"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <div className="min-h-screen pitch-grid">
          <header className="border-b border-white/10 bg-pitch-950/80 backdrop-blur">
            <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
              <Link href="/" className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-neon-400/40 bg-neon-400/10 font-bold text-neon-400">
                  PL
                </span>
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.28em] text-neon-400">Project Lamine</p>
                  <p className="text-xs text-white/55">Player DNA</p>
                </div>
              </Link>
              <Link href="/players" className="rounded-full border border-white/10 px-4 py-2 text-sm text-white/80 hover:border-neon-400/50 hover:text-white">
                Search players
              </Link>
            </nav>
          </header>
          <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
