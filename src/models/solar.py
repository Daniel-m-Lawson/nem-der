from dataclasses import dataclass
from datetime import datetime


@dataclass
class RooftopPVRecord:
    settlementdate: datetime
    regionid: str
    power_mw: float


@dataclass
class RooftopPVSeries:
    records: list[RooftopPVRecord]

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def peak_mw(self) -> float:
        """Return the maximum recorded rooftop PV output in MW."""
        return max(r.power_mw for r in self.records) if self.records else 0.0

    def to_lists(self) -> tuple[list[datetime], list[float]]:
        """Return (timestamps, power_mw_values) lists suitable for plotting."""
        return (
            [r.settlementdate for r in self.records],
            [r.power_mw for r in self.records],
        )
