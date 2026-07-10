"""GroqProvider — the real LLM: Llama 3.3 70B via Groq's OpenAI-compatible API.
"""
import json
from typing import Any

from groq import Groq

from ..config import settings
from .provider import LLMResponse, ToolCall, ToolSpec


class GroqProvider:
    name = "groq"

    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    def chat(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=self._to_wire(messages),
                tools=[self._tool_to_wire(t) for t in tools],
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as exc:  # A provider hiccup shouldn't 500 the request
            print(f"[groq] request failed: {exc}")
            return LLMResponse(
                content="The language model had trouble with that request. Please try rephrasing."
            )
        message = completion.choices[0].message

        tool_calls: list[ToolCall] = []
        for tc in message.tool_calls or []:
            tool_calls.append(
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=_parse_args(tc.function.arguments),
                )
            )
        return LLMResponse(content=message.content, tool_calls=tool_calls)

    # --- wire-format translation ----------------------------------------------

    @staticmethod
    def _tool_to_wire(tool: ToolSpec) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    @staticmethod
    def _to_wire(messages: list[dict]) -> list[dict]:
        wire: list[dict] = []
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                converted = dict(msg)
                converted["tool_calls"] = [
                    {
                        **tc,
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": _dump_args(tc["function"]["arguments"]),
                        },
                    }
                    for tc in msg["tool_calls"]
                ]
                wire.append(converted)
            else:
                wire.append(msg)
        return wire


def _parse_args(raw: str | dict) -> dict:
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}


def _dump_args(raw: str | dict) -> str:
    return raw if isinstance(raw, str) else json.dumps(raw)
