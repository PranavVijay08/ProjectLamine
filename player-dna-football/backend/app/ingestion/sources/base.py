from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRunResult:
    source_name: str
    raw_paths: list[Path]
    processed_paths: list[Path]
    notes: list[str]
    metadata: dict[str, Any] | None = None
