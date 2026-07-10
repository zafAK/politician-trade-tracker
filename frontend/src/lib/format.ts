// Presentation helpers. Amounts are ranges (STOCK Act buckets), so we render them as such
// rather than pretending there's a single figure.

export function formatAmount(min: number | null, max: number | null): string {
  if (min == null && max == null) return "—";
  const fmt = (n: number) =>
    n >= 1_000_000
      ? `$${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
      : n >= 1000
        ? `$${Math.round(n / 1000)}K`
        : `$${n}`;
  if (min != null && max != null && min !== max) return `${fmt(min)}–${fmt(max)}`;
  return fmt((min ?? max) as number);
}

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
