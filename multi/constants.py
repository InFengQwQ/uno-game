# Note: Network configuration has been moved to config/network.py
# Note: RUN_INTERVAL, ROOM_UPDATE_INTERVAL, ROOM_RECEIVE_INTERVAL
# have been moved to config/settings.py

# Room status (internal state constants, not configuration)
ROOM_WAITING = 0
ROOM_ONGOING = 1

# Json serializable types
InfoDict = dict[str, str | int | list[str]]
RequestDict = dict[str, str | int]
ResponseDict = dict[str, bool | str]
ActionDict = dict[str, str | int]
JsonSerializable = InfoDict | RequestDict | ResponseDict | ActionDict