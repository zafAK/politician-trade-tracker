import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { Stats, TradeFilters, TradePage } from "../api/types";
import { ChatPanel } from "../components/ChatPanel";
import { Filters } from "../components/Filters";
import { StatCards } from "../components/StatCards";
import { TradesTable } from "../components/TradesTable";

type DataSource = "fixture" | "stock_watcher";

export function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [tickers, setTickers] = useState<string[]>([]);
  const [page, setPage] = useState<TradePage | null>(null);
  const [filters, setFilters] = useState<TradeFilters>({
    limit: 15,
    offset: 0,
  });
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [source, setSource] = useState<DataSource>("fixture");
  const [error, setError] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    try {
      const [s, t] = await Promise.all([api.getStats(), api.getTickers()]);
      setStats(s);
      setTickers(t);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  const loadTrades = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPage(await api.getTrades(filters));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadStats();
  }, [loadStats]);

  useEffect(() => {
    void loadTrades();
  }, [loadTrades]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.sync(source);
      await Promise.all([loadStats(), loadTrades()]);
    } catch (e) {
      setError(String(e));
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="dashboard">
      <StatCards
        stats={stats}
        onSync={handleSync}
        syncing={syncing}
        source={source}
        onSourceChange={setSource}
      />
      {error && <div className="card error">{error}</div>}
      <div className="columns">
        <div className="panel">
          <div className="panel-head">
            <h2>Disclosed trades</h2>
            <Filters
              filters={filters}
              onChange={setFilters}
              tickerOptions={tickers}
            />
          </div>
          <TradesTable
            page={page}
            loading={loading}
            onPage={(offset) => setFilters((f) => ({ ...f, offset }))}
          />
        </div>
        <ChatPanel />
      </div>
    </div>
  );
}
