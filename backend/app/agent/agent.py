from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from ..llm.provider import (
    LLMProvider,
    assistant_tool_calls_msg,
    system_msg,
    tool_result_msg,
    user_msg,
)
from .tools import TOOL_SPECS, dispatch

MAX_ITERATIONS = 4

SYSTEM_PROMPT = (
    "You are an assistant for exploring US congressional stock-trade disclosures (STOCK Act). "
    "Answer ONLY from the provided tools — never invent trades, tickers, names, or figures. "
    "Amounts are disclosed as ranges, so describe them as ranges. If a tool returns no data, "
    "say so plainly. Prefer the most specific tool for the question and keep answers concise."
)


@dataclass
class TraceEntry:
    name: str
    arguments: dict
    result_preview: str


@dataclass
class AgentResult:
    answer: str
    traces: list[TraceEntry] = field(default_factory=list)


def _preview(result_json: str, limit: int = 240) -> str:
    return result_json if len(result_json) <= limit else result_json[:limit] + "…"


def run_agent(
    provider: LLMProvider,
    session: Session,
    message: str,
    history: list[dict] | None = None,
) -> AgentResult:
    messages: list[dict] = [system_msg(SYSTEM_PROMPT)]
    for turn in history or []:
        # Only replay plain user/assistant text turns; tool plumbing is per-request.
        if turn.get("role") in {"user", "assistant"} and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append(user_msg(message))

    traces: list[TraceEntry] = []

    for _ in range(MAX_ITERATIONS):
        response = provider.chat(messages, TOOL_SPECS)

        if not response.tool_calls:
            answer = (response.content or "").strip() or "I don't have an answer for that."
            return AgentResult(answer=answer, traces=traces)

        messages.append(assistant_tool_calls_msg(response.tool_calls))
        for call in response.tool_calls:
            result_json = dispatch(session, call.name, call.arguments)
            traces.append(
                TraceEntry(
                    name=call.name,
                    arguments=call.arguments,
                    result_preview=_preview(result_json),
                )
            )
            messages.append(tool_result_msg(call.id, call.name, result_json))

    # Exhausted the loop without a final prose turn.
    return AgentResult(
        answer="I ran several lookups but couldn't settle on an answer — try rephrasing.",
        traces=traces,
    )
