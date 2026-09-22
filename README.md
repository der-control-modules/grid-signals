# Grid Signals

A VOLTTRON agent that generates and publishes **grid service signals** for the DER Control
Modules. It currently produces:

- **Price signals** — time-of-use (TOU) price profiles, with helpers for ComEd and PJM
  market prices.
- **CO2 signals** — carbon intensity and power-generation breakdown (current and 24-hour
  forecast) from the [Electricity Maps](https://www.electricitymaps.com/) API.

This repository was extracted from the
[`der-management`](https://github.com/der-control-modules/der-management) repository
(`der_agents/grid_signals`).

## Requirements

* python >= 3.10
* volttron >= 10.0
* `pandas`, `numpy`, `python-dateutil`, `requests`

## Repository structure

| Path                                | Description                                                                                   |
|-------------------------------------|-----------------------------------------------------------------------------------------------|
| `grid_signals_agent/agent.py`       | `GridSignalAgent` — the VOLTTRON agent that schedules and publishes price and CO2 signals.    |
| `price_signal/tou.py`               | `PriceProfileGenerator` — builds a 24-hour TOU price profile from interval/pricing config.    |
| `price_signal/comed.py`             | `ComEdPricing` — fetches 5-minute / day-ahead prices from the ComEd hourly-pricing API.       |
| `price_signal/pjm.py`               | `get_pjm_prices()` — fetches real-time and day-ahead prices from the PJM API.                  |
| `price_signal/*_test.py`            | Tests for the price-signal helpers.                                                           |
| `co2_signal/co2_api.py`             | `ElectricityMapsAPI` — current and 24-hour carbon intensity and power breakdown.              |
| `co2_signal/zone_names.json`        | Reference list of Electricity Maps zone identifiers.                                          |
| `config`, `config_example`          | Example agent configurations.                                                                 |
| `config.json`                       | Descriptive catalog of the signal types this module targets (not runtime config).            |
| `data/`                             | Sample price/load data files.                                                                 |
| `setup.py`                          | Package/installation metadata.                                                                |
| `prices/`                           | Legacy standalone price scripts, superseded by `price_signal/` (kept for reference).          |

## Configuration

The agent is configured through the VOLTTRON configuration store. Configuration is nested
under `type_of_grid_service_signals`, with a `price` block and/or a `co2` block.

| Parameter                | Description                                                                             |
|--------------------------|-----------------------------------------------------------------------------------------|
| `campus`                 | Campus identifier used to build the publish topics.                                     |
| `run_dayahead_schedule`  | Cron expression for the day-ahead run (price profile + 24-hour CO2 forecast).           |
| `run_realtime_schedule`  | Cron expression for the real-time CO2 run (only used when `co2.real-time` is true).      |

### Price block (`type_of_grid_service_signals.price`)

| Parameter               | Description                                                                    |
|-------------------------|--------------------------------------------------------------------------------|
| `type_of_price_signal`  | Currently `TOU`.                                                               |
| `type_of_tou_pricing`   | TOU variant, e.g. `standard`.                                                  |
| `TOU_pricing.interval`  | Hour ranges per tier (`off-peak`, `mid-peak`, `on-peak`), as `[start, end)` pairs. |
| `TOU_pricing.pricing`   | Price ($/kWh) for each tier.                                                   |

### CO2 block (`type_of_grid_service_signals.co2`)

| Parameter                      | Description                                                            |
|--------------------------------|------------------------------------------------------------------------|
| `real-time`                    | If true, also publishes real-time CO2 on `run_realtime_schedule`.      |
| `method`                       | `API`.                                                                 |
| `API_information.API_key`      | Electricity Maps API token. **Do not commit a real key** (see below).  |
| `API_information.zone`         | Electricity Maps zone id (e.g. `US-NW-PACW`); see `co2_signal/zone_names.json`. |

### Example

```json
{
  "campus": "PNNL",
  "run_dayahead_schedule": "0 0 * * *",
  "run_realtime_schedule": "0 * * * *",
  "type_of_grid_service_signals": {
    "price": {
      "type_of_price_signal": "TOU",
      "type_of_tou_pricing": "standard",
      "TOU_pricing": {
        "interval": {"off-peak": [[0, 7], [21, 23]], "mid-peak": [[7, 10], [18, 21]], "on-peak": [[10, 18]]},
        "pricing": {"off-peak": 0.04675, "mid-peak": 0.09083, "on-peak": 0.15925}
      }
    },
    "co2": {
      "real-time": true,
      "method": "API",
      "API_information": {"API_key": "<your_electricity_maps_api_key>", "zone": "US-NW-PACW"}
    }
  }
}
```

> **Security:** keep API keys out of version control. Load them from an environment
> variable or a local, git-ignored config file rather than committing them.

## Behavior and published topics

On configuration the agent schedules its runs and publishes to topics derived from `campus`:

| Signal                     | Trigger                              | Topic                                                                    |
|----------------------------|--------------------------------------|--------------------------------------------------------------------------|
| TOU price (per hour)       | `run_dayahead_schedule`              | `devices/<campus>/grid_information/price/all` (point `tou`, cents)       |
| 24-hour CO2 forecast       | `run_dayahead_schedule`              | `record/<campus>/grid_information/co2/forecast/{carbonIntensity,powerConsumptionBreakdown}` |
| Real-time CO2              | `run_realtime_schedule` (if enabled) | `record/<campus>/grid_information/co2/real_time/{carbonIntensity,powerConsumptionBreakdown}` |

The price run builds a 24-hour profile, rotates it so it starts at the current hour, and
publishes one message per upcoming hour. The CO2 forecast run fetches the last 24 hours of
Electricity Maps data and shifts the timestamps forward 24 hours as a naive forecast.

## Installation

Before installing, VOLTTRON should be installed and running with its virtual environment
active. See the [VOLTTRON platform](https://github.com/eclipse-volttron/volttron-core).

```shell
vctl install grid-signals --tag grid-signals --start
```

## References

- ComEd hourly pricing API: <https://hourlypricing.comed.com/hp-api/>
- PJM data API: <https://www.pjm.com/markets-and-operations/etools/data-miner-2>
- Electricity Maps API: <https://docs.electricitymaps.com/>
