import enum


# Gibt die Möglichen Daten an welche ausgelesen werden können
class PostRequestTypes(enum.Enum):
    GET_ALL_CONNECTED_NODES = 'get_all_connected_nodes'
    GET_ALL_KNOWN_ROUTES = 'get_all_known_routes'
    GET_ALL_LOCAL_ADDRESSES = 'get_all_local_addresses'