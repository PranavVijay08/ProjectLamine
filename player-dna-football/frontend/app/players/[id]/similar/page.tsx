"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { PlayerComparisonTable } from "@/components/PlayerComparisonTable";
import { RadarChartCard } from "@/components/RadarChartCard";
import { SimilarityCard } from "@/components/SimilarityCard";
import { StyleLabelBadge } from "@/components/StyleLabelBadge";
import { comparePlayers, getPlayer, getSimilarPlayers } from "@/lib/api";
import type { ComparisonResponse, Player, SimilarFilters, SimilarPlayer } from "@/lib/types";

export default function SimilarPlayersPage() {
  const params = useParams<{ id: string }>();
  const playerId = Number(params.id);
  const [player, setPlayer] = useState<Player | null>(null);
  const [similar, setSimilar] = useState<SimilarPlayer[]>([]);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [filters, setFilters] = useState<SimilarFilters>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([getPlayer(playerId), getSimilarPlayers(playerId, filters)])
      .then(([selectedPlayer, similarPlayers]) => {
        setPlayer(selectedPlayer);
        setSimilar(similarPlayers);
        if (similarPlayers[0]) {
          return comparePlayers(playerId, similarPlayers[0].player.player_id).then(setComparison);
        }
        setComparison(null);
        return null;
      })
      .finally(() => setLoading(false));
  }, [playerId, filters]);

  if (loading && !player) return <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-white/60">Calculating similar players...</div>;
  if (!player) return <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-white/60">Player not found.</div>;

  return (
    <div className="space-y-7">
      <section className="rounded-lg border border-white/10 bg-pitch-900/80 p-6 shadow-glow">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-neon-400">Similarity results</p>
            <h1 className="mt-3 text-4xl font-bold text-white">{player.player_name}</h1>
            <p className="mt-2 text-white/60">
              {player.position} · {player.club} · {player.league}
            </p>
          </div>
          <StyleLabelBadge label={player.style_label} />
        </div>
      </section>

      <section className="rounded-lg border border-white/10 bg-white/[0.045] p-5">
        <div className="grid gap-3 md:grid-cols-4">
          <FilterInput label="Max age" value={filters.max_age ?? ""} onChange={(value) => setFilters((current) => ({ ...current, max_age: value }))} />
          <FilterInput label="League" value={filters.league ?? ""} onChange={(value) => setFilters((current) => ({ ...current, league: value }))} />
          <FilterInput label="Position" value={filters.position ?? ""} onChange={(value) => setFilters((current) => ({ ...current, position: value }))} />
          <FilterInput label="Nationality" value={filters.nationality ?? ""} onChange={(value) => setFilters((current) => ({ ...current, nationality: value }))} />
        </div>
      </section>

      {comparison ? (
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <RadarChartCard player={comparison.player} comparisonPlayer={comparison.other_player} />
          <PlayerComparisonTable comparison={comparison} />
        </div>
      ) : null}

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Top 10 similar players</h2>
          <span className="text-sm text-white/50">{similar.length} matches</span>
        </div>
        {loading ? <div className="rounded-lg border border-white/10 bg-white/[0.045] p-5 text-white/60">Refreshing results...</div> : null}
        <div className="grid gap-4 xl:grid-cols-2">
          {similar.map((result) => (
            <SimilarityCard key={result.player.player_id} result={result} />
          ))}
        </div>
        {!loading && similar.length === 0 ? <div className="rounded-lg border border-white/10 bg-white/[0.045] p-6 text-white/60">No players match the selected filters.</div> : null}
      </section>
    </div>
  );
}

function FilterInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-medium uppercase tracking-wide text-white/45">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 w-full rounded-lg border border-white/10 bg-black/25 px-3 py-2 text-sm text-white outline-none focus:border-neon-400/60"
      />
    </label>
  );
}
