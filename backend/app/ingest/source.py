from typing import Protocol


class TradeSource(Protocol):
    #: A short identifier stored on each row (e.g. "fixture", "house", "senate").
    name: str

    def fetch(self) -> list[dict]:
        """Return raw disclosure records as dicts, in whatever shape the source provides."""
        ...