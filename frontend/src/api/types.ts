interface Trade{
    id: number;
    politician_id: number;
    politician_name: string;
    ticker: string | null;
    asset_description: string | null;
    transaction_type: "buy" | "sell" | "exchange";
    transaction_date: string | null;
    min_amount: number | null;
    max_amount: number | null;
    source: string | null;
    synced_at: string | null;
}

export interface TradePage {
    items: Trade[];
    total: number;
    limit: number;
    offset: number;
  }
  
  export interface TickerCount {
    ticker: string;
    trade_count: number;
  }
  
  export interface Stats {
    total_trades: number;
    total_politicians: number;
    last_synced_at: string | null;
    top_tickers: TickerCount[];
  }
  
  export interface TradeFilters {
    politician?: string;
    ticker?: string;
    transaction_type?: "buy" | "sell" | "exchange";
    limit?: number;
    offset?: number;
  }
  
  export interface ToolCallTrace {
    name: string;
    arguments: Record<string, unknown>;
    result_preview: string;
  }
  
  export interface ChatResponse {
    answer: string;
    tool_calls: ToolCallTrace[];
  }
  