from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScadaRecord:
    settlementdate: datetime
    duid: str
    scadavalue: float


@dataclass
class ScadaSeries:
    records: list[ScadaRecord]

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def filter_duid(self, duid: str) -> "ScadaSeries":
        """Return a new ScadaSeries for a single DUID."""
        return ScadaSeries([r for r in self.records if r.duid == duid])

    def duids(self) -> list[str]:
        """Return the unique DUIDs present in this series."""
        seen = set()
        result = []
        for r in self.records:
            if r.duid not in seen:
                seen.add(r.duid)
                result.append(r.duid)
        return result

    def to_lists(self) -> tuple[list[datetime], list[float]]:
        """Return (timestamps, scadavalues) lists. Assumes a single DUID."""
        return (
            [r.settlementdate for r in self.records],
            [r.scadavalue for r in self.records],
        )
