# Multicast group address and port for room discovery
MULTICAST_GROUP = '239.255.0.0'
MULTICAST_PORT = 50000

# Port range for game hosts
HOST_PORT_RANGE = range(50001, 51000)

# Buffer size for network communication
BUFFER_SIZE = 1024

# Json serializable types
InfoDict = dict[str, str | int | list[str]]
RequestDict = dict[str, str | int]
ResponseDict = dict[str, bool | str]
JsonSerializable = InfoDict | RequestDict | ResponseDict