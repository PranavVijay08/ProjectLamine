export function AttributeBadge({ label }: { label: string }) {
  return <span className="rounded-full bg-white/10 px-2.5 py-1 text-xs text-white/75 ring-1 ring-white/10">{label}</span>;
}
