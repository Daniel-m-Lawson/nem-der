# NEM DER Context — For Claude Code

This file gives Claude Code the domain knowledge needed to work on the NEM DER Impact
Analyser without requiring constant re-explanation. Read this before starting any session.

---

## What This Project Is

A Streamlit portfolio app analysing how Distributed Energy Resources (DER) are affecting
spot price dynamics in the Australian National Electricity Market (NEM). Built by a
software engineer at AEMO (Australian Energy Market Operator) with a mechatronics and
econometrics background. The goal is public visibility in the Australian energy tech
startup ecosystem.

---

## The NEM (National Electricity Market)

- The NEM is the electricity grid connecting QLD, NSW, VIC, SA, and TAS (WA is separate)
- It is one of the world's longest interconnected power systems (~5,000 km)
- Operated by AEMO (Australian Energy Market Operator)
- Spot price is set every **5 minutes** (changed from 30-min in October 2021 — important
  for data handling)
- Price cap: $15,500/MWh. Price floor: -$1,000/MWh (negative prices are real and common)
- Regions: NSW1, VIC1, QLD1, SA1, TAS1 — these are the region identifiers used in data

## Key Market Concepts

**Dispatch:** Every 5 minutes, AEMO runs an optimisation to match supply and demand.
Generators submit price/volume bids, AEMO dispatches the cheapest units first (merit order).

**Regional Reference Price (RRP):** The spot price for each region, set at the marginal
cost of the last unit dispatched. This is what we mean by "spot price" throughout.

**Negative Prices:** Occur when there is excess supply (e.g. midday solar flood). Generators
with must-run constraints (wind, some solar) bid negatively to avoid being curtailed.
SA has the most negative pricing events in the NEM due to very high rooftop solar
penetration.

**The Duck Curve:** The shape of net demand (total demand minus solar generation) over a
day. It looks like a duck — a deep trough midday (solar peaks) and a steep ramp in the
evening (solar drops, demand stays high). This creates both very low/negative prices
midday and very high prices in the evening peak.

**FCAS (Frequency Control Ancillary Services):** Services that keep grid frequency at
50Hz. Separate market from energy — batteries are major providers. Not the focus of this
project but worth knowing.

---

## DER (Distributed Energy Resources)

DER refers to small-scale energy resources connected at the distribution level (not the
transmission grid). In the NEM context this primarily means:

- **Rooftop solar (D-PV):** Residential and small commercial solar. Australia has the
  highest per-capita rooftop solar in the world. SA leads nationally.
- **Residential batteries:** e.g. Tesla Powerwall, SolarEdge. Increasingly common,
  especially in SA.
- **VPPs (Virtual Power Plants):** Aggregations of residential batteries dispatched as
  a single market participant. Tesla's SA VPP is the most well-known example.
- **EVs:** Emerging DER asset, not yet significant in NEM data.

**Key tension:** Most rooftop solar is not a registered NEM participant — it shows up as
a reduction in demand (called "underlying demand") rather than as explicit generation.
This makes it harder to analyse directly from dispatch data.

**DER curtailment:** Under the AS/NZS 4777.2 standard, inverters can be instructed to
reduce output during grid stress events (overvoltage, overfrequency). This is tracked
in AEMO data.

---

## Data Tools Used in This Project

### NEMOSIS
- **Repo:** https://github.com/UNSW-CEEM/NEMOSIS
- **Purpose:** Python package for downloading historical AEMO data from NEMWeb
- **Maintained by:** UNSW Centre for Energy and Environmental Markets (CEEM)
- **Key function:** `dynamic_data_compiler(start_time, end_time, table, cache_dir)`
- Returns a pandas DataFrame

**Key tables used in this project:**

| Table | Description | Key columns | Notes |
|-------|-------------|-------------|-------|
| `DISPATCHPRICE` | Spot price per region per 5-min interval | `SETTLEMENTDATE`, `REGIONID`, `RRP` | |
| `DISPATCH_UNIT_SCADA` | Actual output of each registered generator | `SETTLEMENTDATE`, `DUID`, `SCADAVALUE` | No `REGIONID` — join with `DUDETAILSUMMARY` to filter by region |
| `DUDETAILSUMMARY` | Static generator metadata | `DUID`, `DISPATCHTYPE`, `REGIONID`, `STARTDATE`, `LASTCHANGED` | Use `nemosis.static_table()` not `dynamic_data_compiler` |
| `ROOFTOP_PV_ACTUAL` | AEMO's estimated rooftop PV generation | `INTERVAL_DATETIME`, `REGIONID`, `POWER`, `TYPE` | Timestamp column is `INTERVAL_DATETIME` (not `SETTLEMENTDATE`). Filter `TYPE == 'MEASUREMENT'` to exclude satellite estimates |

**Date format for NEMOSIS:** `'YYYY/MM/DD HH:MM:SS'`

**Cache:** NEMOSIS downloads CSVs from NEMWeb and caches them locally. Use Parquet
format for faster subsequent reads. Do not commit the cache to git — add `data/cache/`
to `.gitignore`.

**Important note on data volume:** Full history is ~54 GB. Always use a restricted
date window during development. 2022–2024 is sufficient for meaningful DER analysis
and captures the post-5-minute-settlement period consistently.

### Nempy
- **Repo:** https://github.com/UNSW-CEEM/nempy
- **Purpose:** Models the NEM dispatch procedure — can simulate spot prices from
  generator bids. More complex than NEMOSIS. Not used in v1 of this project but
  relevant for the VPP dispatch optimiser (Project 3 in the career plan).

### OpenNEM
- **Repo:** https://github.com/opennem
- **Purpose:** Open data platform for NEM visualisation. Good reference for what
  good NEM data visualisation looks like.

---

## Identifying DER in AEMO Data

Rooftop solar does **not** appear as a DUID in dispatch data — it reduces regional
demand instead. To analyse rooftop solar impact, use:

1. **Demand residual method:** Compare `TOTALDEMAND` (metered demand including rooftop)
   vs `DEMANDFORECAST` or underlying demand estimates. The gap is approximately rooftop
   solar contribution.

2. **AEMO's ROOFTOP_PV tables:** AEMO publishes estimated rooftop PV generation in
   the `ROOFTOP_PV_ACTUAL` table (available via NEMOSIS). Use this as the direct
   rooftop solar signal.

3. **Registered DER participants:** Large battery systems (e.g. Tesla SA VPP) are
   registered as DUIDs and appear in `DISPATCH_UNIT_SCADA`. Filter `DUDETAILSUMMARY`
   for `FUEL_SOURCE_DESCRIPTOR = 'Battery Storage'` to find them.

---

## SA-Specific Context

South Australia (region ID: `SA1`) is the focus of this project because:

- Highest rooftop solar penetration per capita in the world
- Frequently hits negative spot prices (sometimes for hours at a time)
- Home to Tesla's large-scale VPP (Neoen's Hornsdale Power Reserve)
- Weakly interconnected to VIC via a single Heywood interconnector — prices
  decouple from the rest of the NEM regularly
- Best region to demonstrate DER market impact visually

---

## The 5-Minute Settlement Change

On **1 October 2021**, the NEM moved from 30-minute to 5-minute price settlement.
Before this date, prices were averaged over 6 dispatch intervals for settlement purposes.
After this date, each 5-minute dispatch price is also the settlement price.

**Implication for this project:** When comparing pre/post October 2021 data, be aware
that price volatility metrics are not directly comparable. The post-2021 data will
show higher apparent volatility. Either:
- Restrict analysis to post-October 2021 only (recommended for simplicity), or
- Explicitly resample pre-2021 data to 30-minute intervals before comparing

---

## Developer Notes

- All timestamps in NEM data are **Australian Eastern Standard Time (AEST, UTC+10)**,
  non-daylight-saving. Do not convert to local time — keep everything in AEST.
- `SETTLEMENTDATE` in dispatch tables refers to the **end** of the dispatch interval,
  not the start. `ROOFTOP_PV_ACTUAL` uses `INTERVAL_DATETIME` instead of `SETTLEMENTDATE`.
- Region IDs in data always include the trailing `1`: `NSW1`, `VIC1`, `QLD1`, `SA1`, `TAS1`
- NEMOSIS `dynamic_data_compiler` requires start/end times as strings in the format
  `'YYYY/MM/DD HH:MM:SS'`
- `data_loader.py` is the only file that imports pandas. It converts NEMOSIS DataFrames
  to custom domain types immediately using `zip` over columns (not `itertuples` — Pylance
  types itertuples return as `Never`, causing false errors throughout the codebase).