class NodeConnection:
    def __init__(self, version, node_key, end_point, connected_since) -> None:
        self.__connected_since = connected_since
        self.__version = version
        self.__node_key = node_key
        self.__ep = end_point

    @property
    def _tlist(self):
        return [self.__node_key, self.__version, self.__ep, self.__connected_since]



class KnownAddressRoute:
    def __init__(self, pubkeyadr, route_known_since) -> None:
        self.__route_known_since = route_known_since
        self.__pubkeyadr = pubkeyadr

    @property
    def _tlist(self):
        return [self.__pubkeyadr, self.__route_known_since]