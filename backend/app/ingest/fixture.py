import json
from pathlib import Path

_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "trades.sample.json"


class FixtureSource:
    name = "fixture"

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _FIXTURE_PATH

    def fetch(self) -> list[dict]:
        return json.loads(self._path.read_text())
