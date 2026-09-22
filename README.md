# Grid Signals

Utilities for generating and retrieving grid signals used by the DER Control Modules,
including electricity price signals and grid service signals.

This repository was extracted from the
[`der-management`](https://github.com/der-control-modules/der-management) repository
(`der_agents/grid_signals`).

## Contents

| Path                       | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `config.json`              | Reference catalog of the supported signal types (real-time prices, TOU pricing, CO2, direct grid-service signals). |
| `prices/TOU/tou.py`        | `PriceProfileGenerator` — builds 24-hour time-of-use price profiles (standard, seasonal, critical peak) from a JSON definition. |
| `prices/TOU/tou.json`      | Example TOU price definition consumed by `tou.py`.                                              |
| `prices/real_time/Comed.py`| Retrieves real-time locational prices from the ComEd hourly-pricing API.                        |

## Signal types

The `config.json` catalog describes the categories of signals this module targets:

- **Price signals** — real-time prices (e.g. ComEd, PJM), time-of-use (standard, seasonal,
  critical peak / CPP), and prices sourced from CSV/database/custom uploads.
- **Grid service signals** — direct signals (peak/emergency demand response, renewable
  integration), CO2 signals, and OpenADR-style event signals.
