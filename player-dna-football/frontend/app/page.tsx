import Link from "next/link";

const highlights = [
  { label: "150", text: "mock player profiles" },
  { label: "19", text: "style attributes" },
  { label: "10", text: "closest DNA matches" }
];

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="py-8">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-neon-400">Football scouting dashboard</p>
          <h1 className="mt-5 max-w-4xl text-4xl font-bold tracking-tight text-white sm:text-6xl">Find players with the same footballing DNA.</h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-white/65">
            Project Lamine compares players by scaled playing-style attributes, then explains why each match looks similar on the pitch.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/players" className="rounded-lg bg-neon-400 px-5 py-3 text-sm font-bold text-pitch-950 hover:bg-neon-500">
              Search players
            </Link>
            <a href="http://localhost:8000/docs" className="rounded-lg border border-white/10 px-5 py-3 text-sm font-semibold text-white/80 hover:border-neon-400/50">
              API docs
            </a>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-pitch-900/80 p-5 shadow-glow">
          <div className="rounded-lg border border-neon-400/20 bg-black/25 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-white/45">Featured DNA</p>
                <h2 className="mt-2 text-2xl font-bold text-white">Direct ball-carrying winger</h2>
              </div>
              <span className="rounded-full bg-neon-400/10 px-3 py-1 text-sm font-semibold text-neon-400">94%</span>
            </div>
            <div className="mt-8 space-y-4">
              {["Progressive carries", "Successful dribbles", "Carries into box"].map((metric, index) => (
                <div key={metric}>
                  <div className="mb-2 flex justify-between text-sm text-white/65">
                    <span>{metric}</span>
                    <span>{92 - index * 7}</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-2 rounded-full bg-neon-400" style={{ width: `${92 - index * 7}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {highlights.map((item) => (
          <div key={item.text} className="rounded-lg border border-white/10 bg-white/[0.045] p-5">
            <p className="text-3xl font-bold text-neon-400">{item.label}</p>
            <p className="mt-1 text-sm text-white/60">{item.text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
