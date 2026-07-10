"""Agent tests — the full tool-calling loop, end to end, with the deterministic MockProvider.

These pass with zero API keys and no network, which is the payoff of the provider seam: the
agent's control flow (pick tool -> run it -> answer from result) is fully testable.
"""
import json

from app.agent.agent import run_agent
from app.agent.tools import dispatch
from app.llm.mock_provider import MockProvider


def test_agent_ranks_traders_of_ticker(seeded_session):
    result = run_agent(MockProvider(), seeded_session, "Who traded NVDA the most?")
    assert "Pelosi" in result.answer
    assert [t.name for t in result.traces] == ["top_traders_of_ticker"]
    assert result.traces[0].arguments == {"ticker": "NVDA"}


def test_agent_ticker_summary(seeded_session):
    result = run_agent(MockProvider(), seeded_session, "Tell me about NVDA")
    assert "NVDA" in result.answer
    assert result.traces[0].name == "ticker_summary"


def test_agent_politician_summary(seeded_session):
    result = run_agent(MockProvider(), seeded_session, "What has Nancy Pelosi been trading?")
    assert "Pelosi" in result.answer
    assert result.traces[0].name == "politician_summary"


def test_agent_recent_trades(seeded_session):
    result = run_agent(MockProvider(), seeded_session, "Show me the latest trades")
    assert result.traces[0].name == "recent_trades"
    assert result.answer  # non-empty


def test_agent_answer_is_grounded_in_a_tool_call(seeded_session):
    """Every answer must be backed by at least one tool call (the auditability guarantee)."""
    result = run_agent(MockProvider(), seeded_session, "What are the most traded stocks?")
    assert len(result.traces) >= 1


def test_dispatch_coerces_stringified_int_args(seeded_session):
    """Smaller models emit `{"limit": "3"}` (string). dispatch must coerce it, not crash."""
    out = json.loads(dispatch(seeded_session, "recent_trades", {"limit": "3"}))
    assert "error" not in out
    assert len(out["trades"]) == 3


def test_dispatch_unknown_tool_returns_error(seeded_session):
    out = json.loads(dispatch(seeded_session, "no_such_tool", {}))
    assert "error" in out


def test_dispatch_bad_arguments_returns_error(seeded_session):
    # top_traders_of_ticker requires `ticker`; omitting it should be reported, not raised.
    out = json.loads(dispatch(seeded_session, "top_traders_of_ticker", {}))
    assert "error" in out
