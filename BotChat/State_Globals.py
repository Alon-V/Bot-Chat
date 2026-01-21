"""Shared in-process state for Launcher_UI and Chat_UI (NiceGUI app)"""

from typing import List, Tuple, Dict, Any

# =========================
# ===== Chat Storage  =====
# =========================
# History storage. Format: (msg_id, sender, text, stamp, target_id) -->
messages: List[Tuple[str, str, str, str, str]] = []

# List of connected usernames (synced by server USERS messages) -->
active_users_list: List[str] = []


# ==============================
# ===== Avatar Sync Storage ====
# ==============================
# [(Username) -> (Avatar URL)] dictionary chosen by the user (synced via server) -->
avatar_urls: Dict[str, str] = {}


# ==============================
# ===== Avatar Color Setup  ====
# ==============================
BG_COLORS = ['b6e3f4', 'c0aede', 'd1f0cc', 'ffd5dc', 'fff3c4', 'f1c27d',
             'e0f2fe', 'ede9fe', 'c7f9cc', 'ffcad4']   # Colors option fo the avatars background

# seed -> chosen background color (keeps consistent avatar bg per user/seed)
user_colors_cache: Dict[str, Any] = {}

# username -> seed string (used to keep avatar consistent after rename)
avatar_seeds: Dict[str, str] = {}
