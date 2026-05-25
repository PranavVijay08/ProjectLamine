"use client";

import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip } from "recharts";

import { attributeLabels, radarCaps, radarFeatures } from "@/lib/player-metrics";
import type { Player } from "@/lib/types";

type RadarChartCardProps = {
  player: Player;
  comparisonPlayer?: Player;
};

export function RadarChartCard({ player, comparisonPlayer }: RadarChartCardProps) {
  const data = radarFeatures.map((feature) => ({
    attribute: attributeLabels[feature],
    player: normalize(Number(player[feature]), radarCaps[feature]),
    comparison: comparisonPlayer ? normalize(Number(comparisonPlayer[feature]), radarCaps[feature]) : undefined,
    rawPlayer: Number(player[feature]),
    rawComparison: comparisonPlayer ? Number(comparisonPlayer[feature]) : undefined
  }));

  return (
    <div className="rounded-lg border border-white/10 bg-pitch-900/80 p-5 shadow-glow">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Radar profile</h2>
          <p className="text-sm text-white/55">Normalized attacking, progression and defensive activity</p>
        </div>
      </div>
      <div className="h-[330px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="rgba(255,255,255,0.14)" />
            <PolarAngleAxis dataKey="attribute" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#071312", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8 }}
              formatter={(value: number, name: string) => [`${Math.round(value)} / 100`, name === "player" ? player.player_name : comparisonPlayer?.player_name]}
            />
            <Radar name="player" dataKey="player" stroke="#40f6a3" fill="#40f6a3" fillOpacity={0.26} />
            {comparisonPlayer ? <Radar name="comparison" dataKey="comparison" stroke="#86a8ff" fill="#86a8ff" fillOpacity={0.16} /> : null}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function normalize(value: number, cap: number) {
  return Math.max(0, Math.min(100, (value / cap) * 100));
}
