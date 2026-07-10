import type { Stats } from "../api/types";
import { formatDate } from "../lib/format";

type DataSource = "fixture" | "stock_watcher";

interface Props {
  stats: Stats | null;
  onSync: () => void;
  syncing: boolean;
  source: DataSource;
  onSourceChange: (source: DataSource) => void;
}

export function StatCards({ stats, onSync, syncing, source, onSourceChange }: Props) {
  return (
    <section className="stat-cards">
      <div className="card stat">
        <span className="stat-value">{stats?.total_trades ?? "—"}</span>
        <span className="stat-label">Trades tracked</span>
      </div>
      <div className="card stat">
        <span className="stat-value">{stats?.total_politicians ?? "—"}</span>
        <span className="stat-label">Members of Congress</span>
      </div>
      <div className="card stat">
        <span className="stat-value">{stats?.top_tickers?.[0]?.ticker ?? "—"}</span>
        <span className="stat-label">Most-traded ticker</span>
      </div>
      <div className="card stat sync-card">
        <div className="source-toggle" role="group" aria-label="Data source">
          <button
            className={`toggle-opt ${source === "fixture" ? "active" : ""}`}
            onClick={() => onSourceChange("fixture")}
            disabled={syncing}
          >
            Sample
          </button>
          <button
            className={`toggle-opt ${source === "stock_watcher" ? "active" : ""}`}
            onClick={() => onSourceChange("stock_watcher")}
            disabled={syncing}
          >
            Live Senate
          </button>
        </div>
        <span className="stat-sub">Last synced {formatDate(stats?.last_synced_at ?? null)}</span>
        <button className="btn" onClick={onSync} disabled={syncing}>
          {syncing
            ? "Syncing…"
            : source === "stock_watcher"
              ? "Fetch live data"
              : "Sync sample"}
        </button>
      </div>
    </section>
  );
}
