class NodeConnection:
    def __init__(self, version, end_point, connected_since, io_data, session_id, enabeld_services) -> None:
        self.connected_since = connected_since
        self.__version = version
        self.__io_data = io_data
        self.enabeld_services = enabeld_services
        self.ep_address = end_point['addr']
        self.ep_type = end_point['type']
        self.session_id = session_id

    @property
    def version(self):
        stringed = f"{self.__version}"
        splited = [stringed[i:i+2] for i in range(0, len(stringed), 2)]
        return f"{splited[0]}.{splited[1]}.{splited[2]}"

    @property
    def recived_bytes(self):
        return self.__io_data['recive_bytes']

    @property
    def writed_bytes(self):
        return self.__io_data['send_bytes']


class KnownAddressRoute:
    def __init__(self, pubkeyadr) -> None:
        self.pubkeyadr = pubkeyadr


class LocalAddress:
    def __init__(self, pubkeyadr) -> None:
        self.pubkeyadr = pubkeyadr