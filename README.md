# NEM DER Impact Analyser

**South Australia has the highest rooftop solar penetration on Earth. That's doing strange things to the electricity market — and the data tells a striking story.**

In 2023, SA's spot price went negative on 23% of all dispatch intervals. Not occasionally. Not as a curiosity. Nearly one in four five-minute windows, generators were paying the grid to take their power. Meanwhile, evening prices routinely spiked above $500/MWh — sometimes into the thousands — as solar dropped off and demand stayed high.

This is the duck curve playing out in real market data, and it's getting more pronounced every year as rooftop solar keeps growing.

I built this tool to make that story visible. It's aimed at anyone working in Australian energy tech — VPP operators, energy traders, or engineers trying to understand what DER penetration actually means for market dynamics.

---

## What I built

An interactive Streamlit app that pulls historical NEM data via [NEMOSIS](https://github.com/UNSW-CEEM/NEMOSIS) (UNSW CEEM's open-source data tool) and lets you explore three analyses across any date range from 2022 onwards:

**1. Negative Price Frequency**
How often is the SA spot price negative, and is it getting more common? Spoiler: yes.

**2. Price Volatility Heatmap**
A heatmap of price volatility by hour-of-day and month. The duck curve is immediately visible — a trough of cheap/negative prices from roughly 10am–3pm and a sharp volatility spike from 4–8pm as solar drops off.

**3. DER Curtailment Events**
How often is rooftop solar output being constrained, and how much generation is being left on the table?

<!-- SCREENSHOT: App sidebar + Analysis 1 (negative price frequency line chart) -->
> *Screenshot: negative price frequency trend for SA1, 2022–2024*

<!-- SCREENSHOT: Volatility heatmap showing duck curve -->
> *Screenshot: price volatility heatmap — the duck curve in $/MWh std dev by hour and month*

<!-- SCREENSHOT: Curtailment bar chart -->
> *Screenshot: DER curtailment events by month*

---

## The technical side

The stack is deliberately simple. The interesting engineering is in the data layer, not the UI.

```
src/
├── models/          # Custom typed dataclasses — no pandas outside data_loader.py
│   ├── price.py     # PriceRecord, PriceSeries
│   ├── scada.py     # ScadaRecord, ScadaSeries
│   └── solar.py     # RooftopPVRecord, RooftopPVSeries
├── data_loader.py   # NEMOSIS interface — the only file that touches pandas
└── analysis/
    ├── negative_prices.py
    ├── volatility.py
    └── curtailment.py
app.py               # Streamlit entry point — thin, just layout
```

One design decision worth explaining: NEMOSIS returns pandas DataFrames, and I convert them to typed domain objects immediately at the boundary. Everything downstream — the analysis modules, the Streamlit app — works with `PriceSeries`, `RooftopPVSeries`, etc. This keeps the analytical code clean and makes it easy to reason about what data is flowing where without inspecting DataFrame column names.

The data itself comes from AEMO's NEMWeb via NEMOSIS. I'm using three tables:

| Table | What it contains |
|---|---|
| `DISPATCHPRICE` | Spot price (RRP) per region per 5-minute interval |
| `DISPATCH_UNIT_SCADA` | Actual output of each registered generator |
| `ROOFTOP_PV_ACTUAL` | AEMO's estimated rooftop solar generation |

One gotcha worth knowing: `DISPATCH_UNIT_SCADA` has no region column. You have to join it against `DUDETAILSUMMARY` (a static generator registry) to filter by region. AEMO's data model isn't always intuitive.

---

## What the data actually shows

The duck curve isn't just a theoretical shape — in SA it's a market-moving force.

On a typical summer weekday in 2023–2024, rooftop solar peaks around 1,300 MW between 11am and 1pm. During those hours, the spot price regularly goes negative. Generators with must-run constraints — wind farms, some large solar — bid negatively to avoid being curtailed. The market clears at a negative price and someone takes the loss.

Then at 5pm, solar drops. Demand doesn't. The interconnector to Victoria is limited (a single Heywood link), so SA can't easily import. Price spikes.

The gap between the midday trough and the evening peak is the opportunity that VPP operators are trying to arbitrage — charge batteries during negative price periods, discharge into the evening spike. The data shows both sides of that trade clearly.

---

## Running it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

NEMOSIS will download and cache data from NEMWeb on first run. Keep your date window to 1–2 years during development — full NEM history is ~54 GB.

---

## Data source

All market data is sourced from AEMO's NEMWeb via [NEMOSIS](https://github.com/UNSW-CEEM/NEMOSIS), maintained by the [UNSW Centre for Energy and Environmental Markets](https://www.ceem.unsw.edu.au/). NEMOSIS is open source and the underlying AEMO data is publicly available.

---

## About

Built by Dan — software engineer at AEMO with a background in mechatronics and econometrics. This is part of a portfolio of energy market tools. Next up: a VPP dispatch optimiser.

If you're working on something interesting in Australian energy tech, I'd like to hear about it.
