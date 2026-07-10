import type { TradePage } from "../api/types";
import { formatAmount, formatDate } from "../lib/format";

interface Props {
  page: TradePage | null;
  loading: boolean;
  onPage: (offset: number) => void;
}

export function TradesTable({ page, loading, onPage }: Props) {
  if (loading && !page) return <div className="card empty">Loading trades…</div>;
  if (!page || page.items.length === 0)
    return <div className="card empty">No trades match these filters.</div>;

  const { items, total, limit, offset } = page;
  const from = offset + 1;
  const to = Math.min(offset + limit, total);

  return (
    <div className="card">
      <table className="trades-table">
        <thead>
          <tr>
            <th>Politician</th>
            <th>Ticker</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Traded</th>
          </tr>
        </thead>
        <tbody>
          {items.map((t) => (
            <tr key={t.id}>
              <td>{t.politician_name}</td>
              <td className="mono">{t.ticker ?? "—"}</td>
              <td>
                <span className={`pill ${t.transaction_type}`}>{t.transaction_type}</span>
              </td>
              <td className="mono">{formatAmount(t.min_amount, t.max_amount)}</td>
              <td>{formatDate(t.transaction_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pager">
        <span>
          {from}–{to} of {total}
        </span>
        <div className="pager-buttons">
          <button
            className="btn ghost"
            disabled={offset === 0}
            onClick={() => onPage(Math.max(0, offset - limit))}
          >
            Prev
          </button>
          <button
            className="btn ghost"
            disabled={to >= total}
            onClick={() => onPage(offset + limit)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
