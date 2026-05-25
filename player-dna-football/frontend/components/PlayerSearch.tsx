"use client";

import { useEffect, useMemo, useState } from "react";

import { getPlayers } from "@/lib/api";
import type { Player } from "@/lib/types";
import { PlayerCard } from "./PlayerCard";

export function PlayerSearch() {
  const [query, setQuery] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    const timer = setTimeout(() => {
      getPlayers(query)
        .then((results) => {
          if (active) setPlayers(results);
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }, 160);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [query]);

  const featured = useMemo(() => players.slice(0, query ? 18 : 24), [players, query]);

  return (
    <section className="space-y-6">
      <div className="rounded-lg border border-white/10 bg-pitch-900/80 p-4 shadow-glow">
        <label htmlFor="player-search" className="text-sm font-medium text-white/70">
          Search by player, club or league
        </label>
        <input
          id="player-search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Try Lamine Yamal, Arsenal, Serie A..."
          className="mt-3 w-full rounded-lg border border-white/10 bg-black/25 px-4 py-3 text-base text-white outline-none transition placeholder:text-white/35 focus:border-neon-400/60"
        />
      </div>

      {loading ? (
        <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-center text-white/60">Loading player database...</div>
      ) : featured.length === 0 ? (
        <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-center text-white/60">No players match that search.</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {featured.map((player) => (
            <PlayerCard key={player.player_id} player={player} />
          ))}
        </div>
      )}
    </section>
  );
}
