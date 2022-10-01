from ipnpy_api._value_objects import NodeConnection, KnownAddressRoute
from ipnpy_api._core_socket_functions import _CoreSingleSocket



class CommandlineAPI:
    def __init__(self, path) -> None:
        self.__path = path

    # Wird verwendet um alle Verbindungen Anzuzeigen
    def get_all_node_connections(self) -> list:
        # Es wird ein neuer Socket erstellt
        msocket = _CoreSingleSocket(self.__path)

        # Es wird eine Anfrage an die Core Software gestellt
        msocket._write({ "type":"start_request", "request":"get_all_node_peers" })

        # Es wird auf die Antwort der Gegenseite gewartet
        response = msocket._read()

        # Es wird auf die Einzelnen Einträge gewartet
        interval = list()
        for i in range(response['total']):
            recv = msocket._read()
            if recv['item'] != i: raise Exception('INTERNAL_ERROR', i , recv['item'])
            interval.append(NodeConnection(recv['value']['version'], recv['value']['node_key'], recv['value']['end_point'], recv['value']['connected_since']))

        # Es wird geprüft ob alle Daten empfangen wurden
        if response['total'] != len(interval):
            raise Exception('INTERNAL_ERROR')

        # Die Empfangen Daten werden zurückgegenen
        return interval

    # Wird verwendet um alle Verbindungen Anzuzeigen
    def get_all_known_routes(self) -> list:
        # Es wird ein neuer Socket erstellt
        msocket = _CoreSingleSocket(self.__path)

        # Es wird eine Anfrage an die Core Software gestellt
        msocket._write({ "type":"start_request", "request":"get_all_known_routes" })

        # Es wird auf die Antwort der Gegenseite gewartet
        response = msocket._read()

        # Es wird auf die Einzelnen Einträge gewartet
        interval = list()
        for i in range(response['total']):
            recv = msocket._read()
            if recv['item'] != i: raise Exception('INTERNAL_ERROR',i, recv['item'])
            interval.append(KnownAddressRoute(recv['value']['address'], recv['value']['route_known_since']))

        # Es wird geprüft ob alle Daten empfangen wurden
        if response['total'] != len(interval):
            raise Exception('INTERNAL_ERROR')

        # Die Empfangen Daten werden zurückgegenen
        return interval