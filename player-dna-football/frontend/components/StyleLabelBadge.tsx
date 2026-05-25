export function StyleLabelBadge({ label }: { label: string }) {
  return (
    <span className="inline-flex rounded-full border border-neon-400/35 bg-neon-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-neon-400">
      {label}
    </span>
  );
}
