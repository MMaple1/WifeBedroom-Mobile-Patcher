"""wbp.profiles - what each target engine reads, in one place.

Everything that differs between ModRoom V3.3, Deeproom 4.0.3 and Wife's Bedroom v1.5 and is decided per pack
(naming, which packs the engine can list, how partner descriptors are written) lives here, so a fix for one
engine cannot leak into another. The facts come from the games' own code; see
core/ENGINE_ARCHITECTURE_REPORT.md (sections 8-11).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class EngineProfile:
    arch: str                       # key used across the patcher: "modroom33" | "deeproom" | "v15"
    label: str
    modern_names_ok: bool           # reads custom_*_0.png and _alt_N.png natively
    needs: Optional[Dict[str, List[Tuple[str, Tuple[str, ...]]]]] = field(default=None, hash=False)
    # needs: kind -> [(label, accepted file names)]. A pack missing one is not listed by the engine's own scan and
    # drawing the missing sprite ends the game, so the build skips it. None = the engine copes with partial packs.
    partner_descriptor: str = ""    # file written for a partner pack ("" = the authored file is kept)


# ModRoom's own scan (check_custom_futa / check_custom_wife), with the names the patched checks also accept.
# One table, shared with the converters (wbp/wbconv.py is a verbatim copy of their core/wbconv.py).
from wbp.wbconv import MODROOM_NEEDS  # noqa: E402

PROFILES = {
    "modroom33": EngineProfile("modroom33", "ModRoom V3.3", modern_names_ok=True, needs=MODROOM_NEEDS, partner_descriptor="custom_data.wife"),
    "deeproom": EngineProfile("deeproom", "Deeproom 4.0.3", modern_names_ok=True),
    "v15": EngineProfile("v15", "Wife's Bedroom v1.5", modern_names_ok=False, partner_descriptor="custom_data.spouse"),
}


def get_profile(arch: str) -> EngineProfile:
    """Profile for an architecture key; unknown keys behave like Deeproom (the default template)."""
    return PROFILES.get(arch, PROFILES["deeproom"])
