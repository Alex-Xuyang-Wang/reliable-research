from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any


@dataclass(frozen=True)
class AtomicClaim:
    """One factual claim extracted from a research report."""

    claim_id: str
    claim: str
    citations: list[str]
    source_sentence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimExtractionResult:
    """Machine-readable output of atomic claim extraction for one report."""

    report_id: str
    claims: list[AtomicClaim]

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "claims": [claim.to_dict() for claim in self.claims],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
