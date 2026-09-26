"""Regression test for issue #1: the CO2 config, which holds the API key,
must never reach stdout, stderr, or a log record.

`configure_main` is exercised directly on a bare instance rather than through
`GridSignalAgent(...)`, because the constructor's `default_config` literal has
an unrelated pre-existing bug (`true` instead of `True`) that raises
`NameError` on every construction; see the dispatch report for issue #1.
"""
import logging
import types

from derhost.compat.import_hook import install_volttron_compatibility

install_volttron_compatibility()

import grid_signals_agent.agent as agent_module  # noqa: E402 (must follow the compat install)

MARKER = "TESTKEY-DO-NOT-USE-9f3a7c21"


def _make_agent():
    """Build a GridSignalAgent instance with configure_main's dependencies
    seeded directly, bypassing the broken __init__."""
    agent = object.__new__(agent_module.GridSignalAgent)
    agent.default_config = {
        "run_dayahead_schedule": "0 0 * * *",
        "run_realtime_schedule": "0 * * * *",
    }
    agent.localtz = "UTC"
    agent.signal_type = None
    agent.price_type = None
    agent.publish_topic = None
    agent.price_signals = None
    agent.grid_service_signals = None
    agent.co2_config = None
    agent.run_dayahead_schedule = "0 * * * *"
    agent.run_realtime_schedule = "0 * * * *"
    agent.core = types.SimpleNamespace(identity="test-agent", schedule=lambda *a, **k: None)
    return agent


def _co2_contents(marker: str) -> dict:
    return {
        "type_of_grid_service_signals": {
            "co2": {
                "real-time": False,
                "method": "API",
                "API_information": {"API_key": marker, "zone": "US-TEST"},
            }
        }
    }


def test_co2_config_load_never_prints_or_logs_the_key(capsys, caplog):
    agent = _make_agent()
    with caplog.at_level(logging.DEBUG):
        agent.configure_main("config", "NEW", _co2_contents(MARKER))

    captured = capsys.readouterr()
    assert MARKER not in captured.out
    assert MARKER not in captured.err
    for record in caplog.records:
        assert MARKER not in record.getMessage()
