"""Constants."""

from typing import Any

# Note: Network configuration has been moved to config/network.py
# Note: RUN_INTERVAL, ROOM_UPDATE_INTERVAL, ROOM_RECEIVE_INTERVAL
# have been moved to config/settings.py

# Room status (internal state constants, not configuration)
ROOM_WAITING = 0
ROOM_ONGOING = 1

# Json serializable type
InfoDict = dict[str, Any]
JsonMessage = dict[str, InfoDict]
