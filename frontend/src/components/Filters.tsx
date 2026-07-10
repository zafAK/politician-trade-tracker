import type { TradeFilters } from "../api/types";

interface Props {
  filters: TradeFilters;
  onChange: (next: TradeFilters) => void;
  tickerOptions: string[];
}

export function Filters({ filters, onChange, tickerOptions }: Props) {
  // Any filter change resets pagination back to the first page.
  const set = (patch: Partial<TradeFilters>) =>
    onChange({ ...filters, ...patch, offset: 0 });

  return (
    <div className="filters">
      <input
        className="input"
        placeholder="Politician name…"
        value={filters.politician ?? ""}
        onChange={(e) => set({ politician: e.target.value })}
      />
      {/* Free-text ticker search with autocomplete over every ticker in the data. */}
      <input
        className="input"
        list="ticker-options"
        placeholder="Ticker (e.g. NVDA)"
        value={filters.ticker ?? ""}
        onChange={(e) => set({ ticker: e.target.value.toUpperCase() || undefined })}
      />
      <datalist id="ticker-options">
        {tickerOptions.map((t) => (
          <option key={t} value={t} />
        ))}
      </datalist>
      <select
        className="input"
        value={filters.transaction_type ?? ""}
        onChange={(e) =>
          set({
            transaction_type:
              (e.target.value as TradeFilters["transaction_type"]) || undefined,
          })
        }
      >
        <option value="">Buys &amp; sells</option>
        <option value="buy">Buys</option>
        <option value="sell">Sells</option>
      </select>
      {(filters.politician || filters.ticker || filters.transaction_type) && (
        <button className="btn ghost" onClick={() => onChange({ limit: filters.limit, offset: 0 })}>
          Clear
        </button>
      )}
    </div>
  );
}
