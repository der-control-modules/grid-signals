"""Regression test for issue #4: the default config used a JSON-style
lowercase `true`, which is not a Python literal, so constructing the agent
with no config file raised `NameError` on every path.
"""
from derhost.compat.import_hook import install_volttron_compatibility

install_volttron_compatibility()

import grid_signals_agent.agent as agent_module  # noqa: E402 (must follow the compat install)


def test_agent_constructs_with_default_config(tmp_path):
    missing_config = tmp_path / "does-not-exist.json"

    agent = agent_module.GridSignalAgent(config_path=str(missing_config))

    co2_config = agent.default_config["type_of_grid_service_signals"]["co2"]
    assert co2_config["real-time"] is True
