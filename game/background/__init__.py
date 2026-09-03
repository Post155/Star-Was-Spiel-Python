from .manager import BackgroundManager
from .systems import StarSystem

__all__ = ["BackgroundManager", "StarSystem"]

SYSTEM_ENTRY_DELAY_MS = 5000   # 5 Sekunden
SYSTEM_EXIT_DELAY_MS  = 5000    # 5 Sekunden vor Wechsel

PLANET_FORCE_SINGLE_PASS = True