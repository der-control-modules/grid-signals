# Grid Signals

Utilities for generating and retrieving the grid signals used by the DER Control Modules —
principally electricity **price signals** (time-of-use profiles and real-time market prices).

This repository was extracted from the
[`der-management`](https://github.com/der-control-modules/der-management) repository
(`der_agents/grid_signals`).

## Requirements

* python >= 3.8
* Real-time price script (`Comed.py`): `numpy`, `pandas`, `matplotlib`, `pytz`
* TOU price generator (`tou.py`): standard library only

```shell
pip install numpy pandas matplotlib pytz
```

## Contents

| Path                        | Description                                                                                              |
|-----------------------------|----------------------------------------------------------------------------------------------------------|
| `config.json`               | Reference catalog of the signal types this module targets (see [Signal catalog](#signal-catalog)). Descriptive only — not loaded by the code. |
| `prices/TOU/tou.py`         | `PriceProfileGenerator` — builds 24-hour time-of-use price profiles from a JSON definition.              |
| `prices/TOU/tou.json`       | Example TOU price definition consumed by `tou.py`.                                                       |
| `prices/real_time/Comed.py` | Standalone script that pulls ComEd real-time prices from their public API and analyzes them.             |

## Time-of-use price profiles (`prices/TOU`)

`PriceProfileGenerator` reads a JSON file of price tiers and produces a list of 24 hourly
prices ($/kWh). Three profile types are supported:

| Type       | JSON keys                                                                              | Behavior                                                             |
|------------|----------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `standard` | `peak_prices`, `off_peak_prices`                                                       | Peak price during peak hours, otherwise off-peak.                   |
| `critical` | `critical_peak_prices`, `peak_prices`, `off_peak_prices`                               | Critical-peak overrides peak, which overrides off-peak.             |
| `seasonal` | `summer_peak_prices`, `summer_off_peak_prices`, `winter_peak_prices`, `winter_off_peak_prices` | Uses summer tiers for months 6–8, winter tiers otherwise.  |

Each price tier is a list of `[start_hour, end_hour, price]` entries. Intervals are
**half-open** — `start_hour <= hour < end_hour` — and the tiers for a given profile must
together cover **all 24 hours** (0–23); an uncovered hour raises `StopIteration`.

### Usage

As a library:

```python
from tou import PriceProfileGenerator

generator = PriceProfileGenerator("prices/TOU/tou.json")

# Standard / critical profiles:
profile = generator.generate_profile("standard")

# Seasonal profile requires the month (1–12):
summer_profile = generator.generate_profile("seasonal", month=7)

# profile is a list of 24 hourly prices in $/kWh
```

Or run it interactively, which prompts for the profile type (and month, if seasonal) and
prints the resulting 24-hour profile:

```shell
python prices/TOU/tou.py
```

### Example definition (`tou.json`)

```json
{
  "standard": {
    "peak_prices": [[0, 6, 0.15], [18, 24, 0.20]],
    "off_peak_prices": [[6, 18, 0.10]]
  }
}
```

> Note: the `critical` block in the bundled `tou.json` does not cover hours 0–5, so
> `generate_profile("critical")` will fail until those hours are added. Extend the tiers
> to cover the full day before using it.

## Real-time prices (`prices/real_time/Comed.py`)

`Comed.py` is an exploratory analysis script (not an importable module) that:

1. Fetches 5-minute real-time prices from the ComEd hourly-pricing API for a
   **hard-coded date range** (currently the 2021 calendar year).
2. Resamples them to hourly averages and writes them to CSV in the current working
   directory (e.g. `price_comed_2021.csv`).
3. Computes daily variance/standard deviation, identifies the highest-variance days, and
   plots the results with matplotlib.

Because the URL and date range are hard-coded and the script executes on import, edit the
range in the source and run it directly:

```shell
python prices/real_time/Comed.py
```

API reference: <https://hourlypricing.comed.com/hp-api/>

## Signal catalog

`config.json` documents the broader set of grid signals this module is intended to cover:

- **Price signals** — real-time prices (e.g. ComEd, PJM), time-of-use (standard, seasonal,
  critical peak / CPP), and prices sourced from CSV/database/custom uploads.
- **Grid service signals** — direct signals (peak/emergency demand response, renewable
  integration), CO2 signals, and OpenADR-style event signals.

It is a descriptive catalog rather than runtime configuration.
