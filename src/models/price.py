from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceRecord:
    settlementdate: datetime
    regionid: str
    rrp: float


@dataclass
class PriceSeries:
    records: list[PriceRecord]

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def filter_negative(self) -> "PriceSeries":
        """Return a new PriceSeries containing only intervals with negative RRP."""
        return PriceSeries([r for r in self.records if r.rrp < 0])

    def filter_below(self, threshold: float) -> "PriceSeries":
        """Return a new PriceSeries containing only intervals with RRP below threshold."""
        return PriceSeries([r for r in self.records if r.rrp < threshold])

    def to_lists(self) -> tuple[list[datetime], list[float]]:
        """Return (timestamps, rrp_values) lists suitable for plotting."""
        return (
            [r.settlementdate for r in self.records],
            [r.rrp for r in self.records],
        )
