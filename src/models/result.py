from dataclasses import dataclass
from typing import Any


@dataclass
class AnalysisResult:
    """Shared return type for all analysis modules."""
    figure: Any          # plotly.graph_objects.Figure
    insight: str         # 2-3 sentence plain-English interpretation
    data: Any            # the underlying custom data object (PriceSeries, etc.)
