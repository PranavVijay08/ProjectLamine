import Link from "next/link";

import type { Player } from "@/lib/types";
import { StyleLabelBadge } from "./StyleLabelBadge";

export function PlayerCard({ player }: { player: Player }) {
  return (
    <Link
      href={`/players/${player.player_id}`}
      className="group block rounded-lg border border-white/10 bg-white/[0.045] p-5 shadow-glow transition hover:-translate-y-0.5 hover:border-neon-400/35 hover:bg-white/[0.07]"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-lg font-semibold text-white group-hover:text-neon-400">{player.player_name}</p>
          <p className="mt-1 text-sm text-white/60">
            {player.position} · {player.club}
          </p>
        </div>
        <span className="rounded-md border border-white/10 px-2 py-1 text-xs text-white/60">{player.age}</span>
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        <StyleLabelBadge label={player.style_label} />
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">{player.league}</span>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">{player.nationality}</span>
      </div>
    </Link>
  );
}
