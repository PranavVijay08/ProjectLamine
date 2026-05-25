"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { RadarChartCard } from "@/components/RadarChartCard";
import { StyleLabelBadge } from "@/components/StyleLabelBadge";
import { attributeLabels, numericFeatures } from "@/lib/player-metrics";
import { getPlayer } from "@/lib/api";
import type { Player } from "@/lib/types";

export default function PlayerProfilePage() {
  const params = useParams<{ id: string }>();
  const playerId = Number(params.id);
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getPlayer(playerId)
      .then(setPlayer)
      .finally(() => setLoading(false));
  }, [playerId]);

  if (loading) return <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-white/60">Loading player profile...</div>;
  if (!player) return <div className="rounded-lg border border-white/10 bg-white/[0.045] p-8 text-white/60">Player not found.</div>;

  const keyStats = numericFeatures.slice(0, 10);

  return (
    <div className="space-y-7">
      <section className="rounded-lg border border-white/10 bg-pitch-900/80 p-6 shadow-glow">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-neon-400">Player profile</p>
            <h1 className="mt-3 text-4xl font-bold text-white">{player.player_name}</h1>
            <p className="mt-2 text-white/60">
              {player.position} · {player.club} · {player.league}
            </p>
          </div>
          <Link href={`/players/${player.player_id}/similar`} className="rounded-lg bg-neon-400 px-5 py-3 text-sm font-bold text-pitch-950 hover:bg-neon-500">
            View similar players
          </Link>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <StyleLabelBadge label={player.style_label} />
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm text-white/70">{player.age} years old</span>
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm text-white/70">{player.nationality}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm text-white/70">{player.preferred_foot} foot</span>
          <span className="rounded-full bg-white/10 px-3 py-1 text-sm text-white/70">{player.minutes} minutes</span>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <RadarChartCard player={player} />
        <section className="rounded-lg border border-white/10 bg-white/[0.045] p-5">
          <h2 className="text-lg font-semibold text-white">Player DNA card</h2>
          <p className="mt-2 text-sm leading-6 text-white/60">
            {player.player_name} is labelled as a {player.style_label.toLowerCase()} based on the mock statistical profile across chance creation, progression, pressure and duel metrics.
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {keyStats.map((feature) => (
              <div key={feature} className="rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs text-white/45">{attributeLabels[feature]}</p>
                <p className="mt-1 text-xl font-semibold text-white">{player[feature]}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
