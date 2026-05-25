import Link from "next/link";

import type { SimilarPlayer } from "@/lib/types";
import { AttributeBadge } from "./AttributeBadge";
import { StyleLabelBadge } from "./StyleLabelBadge";

export function SimilarityCard({ result }: { result: SimilarPlayer }) {
  const player = result.player;
  return (
    <article className="rounded-lg border border-white/10 bg-white/[0.045] p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href={`/players/${player.player_id}`} className="text-lg font-semibold text-white hover:text-neon-400">
            {player.player_name}
          </Link>
          <p className="mt-1 text-sm text-white/60">
            {player.position} · {player.club} · {player.league}
          </p>
        </div>
        <div className="rounded-lg border border-neon-400/35 bg-neon-400/10 px-3 py-2 text-right">
          <p className="text-xl font-bold text-neon-400">{result.similarity_score}%</p>
          <p className="text-[11px] uppercase tracking-wide text-white/50">match</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <StyleLabelBadge label={player.style_label} />
        {result.matching_attributes.map((attribute) => (
          <AttributeBadge key={attribute} label={attribute} />
        ))}
      </div>
      <p className="mt-4 text-sm leading-6 text-white/68">{result.explanation}</p>
    </article>
  );
}
