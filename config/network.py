"""Network-related configuration."""

# Multicast group address and port for room discovery
MULTICAST_GROUP = '239.255.0.0'
MULTICAST_PORT = 50000

# Port range for game hosts
HOST_PORT_RANGE = range(50001, 51000)

# Buffer size for network communication
BUFFER_SIZE = 1024

# Timeout for socket operations in seconds
SOCKET_TIMEOUT = 5.0

# Capacity of players in a room
ROOM_CAPACITY = 10
