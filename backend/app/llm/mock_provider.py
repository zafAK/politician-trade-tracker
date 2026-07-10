from __future__ import annotations

import json
import re

from .provider import LLMResponse, ToolCall, ToolSpec

# Uppercase tokens that look like tickers but aren't, so we don't mis-detect them.
_TICKER_STOPWORDS = {"US", "USA", "I", "A", "CEO", "ETF", "IPO", "SEC", "PTR"}
# Leading question words that are Capitalized but aren't member names.
_NAME_STOPWORDS = {
    "Who", "What", "Which", "Show", "List", "Tell", "How", "When", "Give", "Find",
    "Does", "Did", "Has", "Have", "Are", "Is", "The", "Any", "Recent", "Latest",
}


class MockProvider:
    name = "mock"

    def chat(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        last = messages[-1] if messages else {}
        if last.get("role") == "tool":
            # A tool has run — turn its JSON result into a readable answer.
            return LLMResponse(content=self._answer_from_tool(last))
        # Otherwise decide which tool to call from the latest user question.
        user_text = self._latest_user_text(messages)
        return LLMResponse(tool_calls=[self._pick_tool(user_text)])

    # --- deciding a tool ------------------------------------------------------

    def _latest_user_text(self, messages: list[dict]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content") or ""
        return ""

    def _extract_ticker(self, text: str) -> str | None:
        for tok in re.findall(r"\b[A-Z]{1,5}\b", text):
            if tok not in _TICKER_STOPWORDS:
                return tok
        return None

    def _extract_name(self, text: str) -> str | None:
        matches = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z.]+)*", text)
        for m in matches:
            first = m.split()[0]
            if first not in _NAME_STOPWORDS:
                return m
        return None

    def _pick_tool(self, text: str) -> ToolCall:
        lower = text.lower()
        ticker = self._extract_ticker(text)
        wants_ranking = any(w in lower for w in ("top", "most", "who", "rank", "biggest"))

        if ticker and wants_ranking:
            return self._call("top_traders_of_ticker", {"ticker": ticker})
        if ticker:
            return self._call("ticker_summary", {"ticker": ticker})
        if any(w in lower for w in ("recent", "latest", "new", "lately")):
            return self._call("recent_trades", {"limit": 10})
        if wants_ranking and any(w in lower for w in ("ticker", "stock", "traded", "popular")):
            return self._call("top_tickers", {"limit": 10})
        name = self._extract_name(text)
        if name:
            return self._call("politician_summary", {"name": name})
        return self._call("recent_trades", {"limit": 10})

    _counter = 0

    def _call(self, name: str, args: dict) -> ToolCall:
        MockProvider._counter += 1
        return ToolCall(id=f"mock-{MockProvider._counter}", name=name, arguments=args)

    # --- writing an answer from a tool result ---------------------------------

    def _answer_from_tool(self, tool_msg: dict) -> str:
        name = tool_msg.get("name", "")
        data = json.loads(tool_msg.get("content") or "{}")
        if "error" in data:
            return f"I couldn't complete that: {data['error']}"

        if name == "ticker_summary":
            traders = ", ".join(
                f"{t['politician']} ({t['trade_count']})" for t in data.get("top_traders", [])
            )
            return (
                f"{data['ticker']} has {data['total_trades']} disclosed trades "
                f"({data['buys']} buys, {data['sells']} sells). "
                f"Most active: {traders or 'n/a'}."
            )
        if name == "top_traders_of_ticker":
            traders = data.get("traders", [])
            if not traders:
                return f"No disclosed trades found for {data.get('ticker')}."
            lead = ", ".join(f"{t['politician']} ({t['trade_count']})" for t in traders[:5])
            return f"Top traders of {data['ticker']}: {lead}."
        if name == "top_tickers":
            items = data.get("top_tickers", [])
            lead = ", ".join(f"{t['ticker']} ({t['trade_count']})" for t in items[:8])
            return f"Most-traded tickers overall: {lead}."
        if name == "politician_summary":
            if data.get("total_trades", 0) == 0:
                return data.get("note", "No trades found for that member.")
            tickers = ", ".join(
                f"{t['ticker']} ({t['trade_count']})" for t in data.get("most_traded_tickers", [])
            )
            return (
                f"{data['politician']} has {data['total_trades']} disclosed trades "
                f"({data['buys']} buys, {data['sells']} sells). "
                f"Most-traded: {tickers or 'n/a'}."
            )
        if name == "recent_trades":
            trades = data.get("trades", [])
            if not trades:
                return "There are no trades in the database yet — try running a sync."
            lead = "; ".join(
                f"{t['politician']} {t['type']} {t['ticker'] or t['asset']} on {t['date']}"
                for t in trades[:5]
            )
            return f"Most recent disclosed trades: {lead}."
        if name == "search_trades":
            return f"Found {data.get('total_matches', 0)} matching trades."
        return "Here's what I found: " + json.dumps(data)[:300]
