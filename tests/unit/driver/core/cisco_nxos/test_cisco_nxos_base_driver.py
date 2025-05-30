import re

import pytest

from scrapli.driver.core.cisco_nxos.base_driver import PRIVS
from scrapli.exceptions import ScrapliValueError


@pytest.mark.parametrize(
    "priv_pattern",
    [
        ("exec", "switch>"),
        ("privilege_exec", "switch# "),
        ("configuration", "switch(config)# "),
        ("configuration", "switch(config-if)# "),
        ("configuration", "switch(config-subif)# "),
        ("configuration", "switch(config-vpc-domain)# "),
        ("configuration", "switch(config-router)# "),
        ("configuration", "switch(config-tacacs+)# "),
        ("configuration", "switch(conf-tm-dest)# "),
        ("privilege_exec", "swi_tch# "),
        ("tclsh", "switch-tcl# "),
        ("tclsh", "> "),
        ("privilege_exec", "switch(maint-mode)# "),
        ("configuration", "switch(maint-mode)(config)# "),
        ("configuration", "switch(maint-mode)(config-if)# "),
        ("configuration", "switch(maint-mode)(config-subif)# "),
        ("configuration", "switch(maint-mode)(config-router)# "),
        ("configuration", "switch(maint-mode)(config-tacacs+)# "),
        ("configuration", "switch(maint-mode)(conf-tm-dest)# "),
        ("tclsh", "switch(maint-mode-tcl)# "),
        ("configuration", "switch(maint-mode)(config-tcl)# "),
    ],
    ids=[
        "exec",
        "privilege_exec",
        "configuration",
        "configuration_interface",
        "configuration_subinterface",
        "configuration_vpc_domain",
        "configuration_routing_protocol",
        "configuration_tacacs",
        "configuration_telemetry_destinations",
        "underscore_privilege_exec",
        "tclsh_privilege_exec",
        "tclsh_command_mode",
        "maint_mode_privilege_exec",
        "maint_mode_configuration",
        "maint_mode_configuration_interface",
        "maint_mode_configuration_subinterface",
        "maint_mode_configuration_routing_protocol",
        "maint_mode_configuration_tacacs",
        "maint_mode_configuration_telemetry_destinations",
        "maint_mode_tclsh_privilege_exec",
        "maint_mode_tclsh_configuration",
    ],
)
def test_prompt_patterns(priv_pattern, sync_nxos_driver):
    priv_level_name = priv_pattern[0]
    prompt = priv_pattern[1]
    prompt_pattern = PRIVS.get(priv_level_name).pattern
    match = re.search(pattern=prompt_pattern, string=prompt, flags=re.M | re.I)
    assert match

    current_priv_guesses = sync_nxos_driver._determine_current_priv(current_prompt=prompt)
    assert len(current_priv_guesses) == 1


def test_create_configuration_session(sync_nxos_driver):
    assert "tacocat" not in sync_nxos_driver.privilege_levels
    sync_nxos_driver._create_configuration_session(session_name="tacocat")

    sync_nxos_driver.privilege_levels["tacocat"].name = "tacocat"
    sync_nxos_driver.privilege_levels["tacocat"].previous_priv = "privilege_exec"
    sync_nxos_driver.privilege_levels["tacocat"].escalate = "configure session tacocat"
    sync_nxos_driver.privilege_levels["tacocat"].pattern = (
        r"^[a-z0-9.\-_@/:]{1,32}\(config\-s[a-z0-9.\-@/:]{0,32}\)#\s?$"
    )

    with pytest.raises(ScrapliValueError):
        sync_nxos_driver._create_configuration_session(session_name="tacocat")
