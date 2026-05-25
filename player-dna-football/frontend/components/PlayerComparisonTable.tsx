import type { ComparisonResponse } from "@/lib/types";

export function PlayerComparisonTable({ comparison }: { comparison: ComparisonResponse }) {
  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-pitch-900/80 shadow-glow">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 p-5">
        <div>
          <h2 className="text-lg font-semibold text-white">Comparison table</h2>
          <p className="text-sm text-white/55">
            {comparison.player.player_name} vs {comparison.other_player.player_name}
          </p>
        </div>
        <span className="rounded-full bg-neon-400/10 px-3 py-1 text-sm font-semibold text-neon-400">{comparison.similarity_score}% similar</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-white/[0.04] text-xs uppercase tracking-wide text-white/50">
            <tr>
              <th className="px-5 py-3">Attribute</th>
              <th className="px-5 py-3">{comparison.player.player_name}</th>
              <th className="px-5 py-3">{comparison.other_player.player_name}</th>
              <th className="px-5 py-3">Delta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {comparison.attribute_deltas.map((row) => (
              <tr key={row.attribute} className="text-white/75">
                <td className="px-5 py-3 font-medium text-white">{row.attribute}</td>
                <td className="px-5 py-3">{row.player_value}</td>
                <td className="px-5 py-3">{row.other_value}</td>
                <td className={row.delta >= 0 ? "px-5 py-3 text-neon-400" : "px-5 py-3 text-white/50"}>{row.delta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
