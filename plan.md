# NEM DER Impact Analyser — Project Plan

## Project Goal

Build an interactive Streamlit app that lets a user explore how growing DER penetration
(rooftop solar, batteries) is changing price dynamics in the NEM — region by region, over
time. The story it tells: *DER is reshaping the market in ways that create both problems
and opportunities for VPP operators and energy traders.*

**Target audience for this portfolio piece:** Software engineers and hiring managers at
Australian energy tech startups (Gridcog, Amber Electric, Evergen, Wattwatchers) and
energy trading desks (Origin, AGL, EnergyAustralia).

**Start with South Australia only.** SA has the highest rooftop solar penetration in the
world, the most negative pricing events, and the most dramatic duck curve. Every analysis
will be visually striking immediately. Multi-region support can be added later.

---

## Repo Structure

```
nem-der-analyser/
├── data/
│   └── cache/              # local NEMOSIS cache (gitignored)
├── src/
│   ├── data_loader.py      # NEMOSIS interface — only file that uses pandas
│   ├── models/             # custom typed dataclasses
│   │   ├── __init__.py
│   │   ├── price.py        # PriceRecord, PriceSeries
│   │   ├── scada.py        # ScadaRecord, ScadaSeries
│   │   ├── solar.py        # RooftopPVRecord, RooftopPVSeries
│   │   └── result.py       # AnalysisResult (shared return type)
│   └── analysis/
│       ├── negative_prices.py
│       ├── volatility.py
│       └── curtailment.py
├── app.py                  # Streamlit entry point
├── notebooks/              # exploratory work, not production code
├── plan.md                 # this file
├── context.md              # NEM/DER domain knowledge for Claude Code
├── README.md
├── pyproject.toml          # dependency management via uv
└── requirements.txt        # kept for Streamlit Cloud compatibility
```

---

## Phases

### Phase 1 — Data Foundation (Week 1–2) [x]

**Goal:** Get NEMOSIS pulling clean data reliably. Everything else depends on this.

Tasks:
- [x] Install NEMOSIS and dependencies (uv, pyproject.toml)
- [x] Pull `DISPATCHPRICE` table for SA — validated in notebook
- [x] Pull `ROOFTOP_PV_ACTUAL` table for SA — validated in notebook
- [x] Explore raw data in a notebook — confirmed shapes and column names
- [x] Build `src/data_loader.py` — NEMOSIS interface returning custom domain types
- [x] Build `src/models/` — typed dataclass layer (PriceSeries, ScadaSeries, RooftopPVSeries)

**Deliverable:** `data_loader.py` + `src/models/` importable by any analysis module.

**Key decisions made:**
- No second cache layer on top of NEMOSIS — NEMOSIS caches natively; revisit if reads are slow
- `data_loader.py` is the only file that imports pandas — everything else uses custom types
- Iterate over DataFrame columns with `zip`, not `itertuples` (Pylance types itertuples as Never)
- Start region: SA only
- Date range for dev/testing: 2023–2024 (post-5-minute-settlement, manageable size)

---

### Phase 2 — Core Analysis (Week 2–4) [ ]

**Goal:** Build three self-contained analysis modules. Each should accept custom
domain types from `data_loader.py` and return an `AnalysisResult(figure, insight, data)`.

#### Analysis 1 — Negative Price Frequency (`src/analysis/negative_prices.py`) [ ]
- Calculate frequency of negative dispatch prices per month/quarter
- Correlate with rooftop solar capacity growth over time
- Output: line chart showing negative price frequency trend over time
- Key insight: Are negative prices becoming more frequent as DER grows?

#### Analysis 2 — Price Volatility Heatmap (`src/analysis/volatility.py`) [ ]
- Calculate price volatility (std dev or IQR) by hour-of-day and season
- Output: heatmap showing the duck curve — price crash midday, spike in evening
- Key insight: When is the grid most stressed, and how is that changing?

#### Analysis 3 — DER Curtailment Events (`src/analysis/curtailment.py`) [ ]
- Identify dispatch intervals where DER output was constrained below available capacity
- Plot frequency and magnitude of curtailment events over time
- Output: bar chart of curtailment events by month
- Key insight: How much DER flexibility is being left on the table?

**Note on Analysis 3:** This requires understanding which DUIDs are DER units —
refer to CONTEXT.md for how to identify these in the AEMO data.

---

### Phase 3 — Streamlit App (Week 4–6) [ ]

**Goal:** Wire the three analyses into a clean interactive interface.

App layout:
```
Sidebar:
  - Region selector (SA only for v1, others grayed out)
  - Date range slider (min: 2020-01-01, max: today)
  - Analysis selector (tabs or radio buttons)

Main panel:
  - Chart output (Plotly, full width)
  - Plain-English interpretation (2–3 sentences below each chart)
  - Data source attribution (AEMO via NEMOSIS)
```

Streamlit components needed (keep it simple):
- `st.sidebar` for controls
- `st.plotly_chart` for figures
- `st.tabs` for switching between analyses
- `st.spinner` while data loads
- `st.cache_data` to avoid re-running analysis on every interaction

Entry point: `app.py` — keep this file thin, just imports and layout.
All logic lives in `src/`.

---

### Phase 4 — Polish & Publish (Week 6–8) [ ]

#### README [x]
Written as a blog post — leads with the problem, explains the three analyses,
has placeholder slots for screenshots. Update numbers and swap in real screenshots
once the app is running.

#### Deploy to Streamlit Cloud [ ]
- Free tier at streamlit.io/cloud
- Connect GitHub repo, set entry point to `app.py`
- Streamlit Cloud uses `requirements.txt` (not pyproject.toml) — keep both in sync

#### LinkedIn Post [ ]
- Announce the project with 2–3 of the most striking charts
- Frame it around the insight, not the tech ("Negative prices in SA have increased X%
  since 2020 — here's what the data shows")
- Tags: #energytech #DER #NEM #Python #opendata

#### UNSW-CEEM Contribution [ ]
- By this point you'll have found a bug, gap, or improvement in NEMOSIS or Nempy
- Open a PR — even small contributions get your name into that community

---

## Weekly Time Budget (4 hrs/week average)

| Week | Focus                                  | Status |
|------|----------------------------------------|--------|
| 1    | NEMOSIS setup + data exploration       | [x]    |
| 2    | Data pipeline + Analysis 1             | [ ]    |
| 3    | Analysis 2                             | [ ]    |
| 4    | Analysis 3                             | [ ]    |
| 5    | Streamlit basics + wire in Analysis 1  | [ ]    |
| 6    | Wire in Analysis 2 & 3                 | [ ]    |
| 7    | Polish UI + README                     | [ ]    |
| 8    | Deploy + LinkedIn post + CEEM PR       | [ ]    |

---

## Decisions Log

_Update this as you make architectural or scope decisions during the build._

| Date | Decision | Reason |
|------|----------|--------|
| 2026-03-15 | Custom dataclass layer (`src/models/`) instead of passing DataFrames | Clean typed interface; pandas stays isolated to data_loader.py |
| 2026-03-15 | Use `zip` over columns instead of `itertuples` for DataFrame conversion | `itertuples` types as `Never` in Pylance, causing false errors |
| 2026-03-15 | uv + pyproject.toml for dependency management | Faster installs, cleaner lockfile; keep requirements.txt for Streamlit Cloud |
| 2026-03-15 | No second Parquet cache on top of NEMOSIS | NEMOSIS caches natively (feather); premature optimisation |
| 2026-03-15 | Dev date range 2023–2024 (not 2022–2024) | One year is sufficient; smaller and faster to work with |
| 2026-03-15 | `AnalysisResult(figure, insight, data)` as shared return type | Uniform interface from analysis modules to Streamlit |

---

## Known Risks

- **NEMOSIS data volume:** Some tables are large (~54 GB for full history). Use a
  restricted date window during development and only expand for final analysis.
- **5-minute settlement change:** NEM moved from 30-min to 5-min settlement in
  October 2021. Be careful when comparing pre/post periods — price data has
  different granularity either side of this date.
- **Streamlit learning curve:** Budget an extra 3–4 hours in Week 5 just playing
  with Streamlit before wiring in real data.