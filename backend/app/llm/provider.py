from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolSpec:
    """A tool the model may call, described with a JSON-Schema parameter spec."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolCall:
    """A model's request to invoke a tool."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """One turn from the model: either a final answer (`content`) or tool calls (or both)."""

    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMProvider(Protocol):
    def chat(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        """Given the running transcript and available tools, return the next model turn."""
        ...


# --- Message construction helpers (keep provider-specific shapes in one place) --------

def system_msg(content: str) -> dict:
    return {"role": "system", "content": content}

def user_msg(content: str) -> dict:
    return {"role": "user", "content": content}

def assistant_tool_calls_msg(tool_calls: list[ToolCall]) -> dict:
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": tc.arguments},
            }
            for tc in tool_calls
        ],
    }


def tool_result_msg(tool_call_id: str, name: str, content: str) -> dict:
    return {"role": "tool", "tool_call_id": tool_call_id, "name": name, "content": content}
