import re

import pytest

from scrapli.driver.core.juniper_junos.base_driver import PRIVS


@pytest.mark.parametrize(
    "priv_pattern",
    [
        ("exec", "boxen> "),
        ("configuration", "boxen# "),
        ("exec", "box_en> "),
        ("exec", "rancid@router2.xyz6> "),
        ("exec", "{master}\nusername@MX-960-PE1>"),
        ("exec", "{backup}\nusername@MX-480-PE2>"),
        ("exec", "{primary:node0}\nusername@SRX-4600-FW1>"),
        ("configuration", "rancid@router2.xyz6# "),
        ("configuration", "{master}[edit]\nusername@MX-960-PE1#"),
        ("configuration", "{backup}[edit]\nusername@MX-480-PE2#"),
        ("configuration", "{primary:node0}[edit]\nusername@SRX-4600-FW1#"),
        ("shell", "asdfklsdjlf\n%"),
        ("shell", "[vrf:foo] regress@EVOvFOOBAR_RE0-re0:~$"),
        ("root_shell", "root@%"),
        ("root_shell", "root@vMX1_RE:/var/home/regress #"),
        ("root_shell", "[vrf:foo] root@EVOvFOOBAR_RE0-re0:~#"),
    ],
    ids=[
        "exec",
        "configuration",
        "exec_underscore",
        "exec_w_period",
        "exec-mx-master-re",
        "exec-mx-backup-re",
        "exec-srx-primary-node",
        "configuration_w_period",
        "configuration-mx-master-re",
        "configuration-mx-backup-re",
        "configuration-srx-primary-node",
        "shell",
        "shell-re0",
        "root",
        "root-re",
        "root-re-vrf",
    ],
)
def test_prompt_patterns(priv_pattern, sync_junos_driver):
    priv_level_name = priv_pattern[0]
    prompt = priv_pattern[1]
    prompt_pattern = PRIVS.get(priv_level_name).pattern
    match = re.search(pattern=prompt_pattern, string=prompt, flags=re.M | re.I)
    assert match

    current_priv_guesses = sync_junos_driver._determine_current_priv(current_prompt=prompt)
    if priv_level_name == "configuration":
        # config, config exclusive, and config private are same prompt so cant tell them apart and
        # thus we return a list of possible priv levels
        assert len(current_priv_guesses) == 3
    else:
        assert len(current_priv_guesses) == 1
