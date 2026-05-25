import { PlayerSearch } from "@/components/PlayerSearch";

export default function PlayersPage() {
  return (
    <div className="space-y-7">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.28em] text-neon-400">Player search</p>
        <h1 className="mt-3 text-3xl font-bold text-white sm:text-4xl">Search the player database</h1>
        <p className="mt-3 max-w-2xl text-white/60">Open any profile to inspect the Player DNA card, radar chart and closest style matches.</p>
      </div>
      <PlayerSearch />
    </div>
  );
}
