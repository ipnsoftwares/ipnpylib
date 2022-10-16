from ipnpy_api._value_objects import NodeConnection, KnownAddressRoute, LocalAddress
from ipnpy_api._core_socket_functions import _CoreDuplexSocket
from ipnpy_api.data_types import PostRequestTypes
from ipnpy_api import get_file_path
import threading
import uuid
import time
import cbor2



# Base Core API Object
class CoreAPI:
    # Erzeugt ein neues Objekt
    def __init__(self) -> None:
        # Wird als Thread ausgeführt und nimmt eintreffende Datensätze entgegen
        self.___thread = threading.Thread(target=self.___package_reader_thread, args=(), daemon=True)

        # Es wird versucht die Socket Verbindung aufzubauen
        self.___core_socket = _CoreDuplexSocket(get_file_path("none_root_sock_io.sock"))

        # Speichert alle Offenen Vorgänge ab
        self.___open_processes = dict()

        # Speichert ab ob der Thread gestartet wurde
        self.___thread_state_started = False

        # Speichert Exceptions ab, welche im Hintergrund auftreten
        self.___background_exceptions = None

        # Der Thread wird gestartet
        self.___thread.start()

        # Es wird geprüft ob der Thread gestartet wurde
        while self.___thread_state_started == False: time.sleep(1/1000)

    # Wird in verwendung mit dem with Statement verwendet
    def __enter__(self):
        return EasyIpnApi(self)

    # Wird am ende des with Statemens oder bei einem Exception aufgerufen
    def __exit__(self, exception_type, exception_value, traceback):
        # Es wird geprüft ob ein Fehler aufgetreten ist
        if self.___background_exceptions != None: raise self.___background_exceptions

        # Dem Duplex Socket wird Signalisiert dass die Verbindung beendet werden soll
        self.___core_socket.close_confirmed()

    # Gibt an ob While Schleifen Weiter laufen können
    def ___while_can_run(self) -> bool:
        return True

    # Wird als Thread ausgeführt und nimmmt eintreffende Pakete entgegen
    def ___package_reader_thread(self):
        # Wird solange ausgeführt, bis die Verbindung getrennt wurde
        try:
            while self.___while_can_run():
                # Es wird geprüft ob es sich um den Ersten Start des Threads handelt
                if self.___thread_state_started == False: self.___thread_state_started = True

                # Es wird auf ein eintreffendes Paket gewartet
                recived_data = self.___core_socket.read_wc()

                # Es wird versucht das Paket mittels CBOR einzulesen
                encoded_package = cbor2.loads(recived_data)

                # Es wird geprüft ob ein Datentyp angegeben wurde
                if ('type' in encoded_package) != True:
                    print('INVLAID_DATA')
                    return

                # Es wird geprüft um was für ein Paket es sich handelt
                if encoded_package['type'] == 'response':
                    # Es wird geprüft ob eine Prozess ID angegeben wurde
                    if ('process_id' in encoded_package) != True:
                        print('INVALID_DATA')
                        return

                    # Es wird geprüft ob es einen Offnen Vorgang gibt
                    if (encoded_package['process_id'] in self.___open_processes) != True:
                        print('UNKOWN_PROCESS')
                        return

                    # Das Paket wird an den Vorgang übergeben
                    self.___open_processes[encoded_package['process_id']](encoded_package)

                    # Der gegenseite wird Signalisiert dass das Paket empfangen wurde
                    self.___core_socket.signal_recived()
        except KeyboardInterrupt as ke:
            self.___background_exceptions = ke
            return
        except Exception as E:
            self.___background_exceptions = E
            return

    # Gibt die Aktuelle Core Version aus
    def get_api_Version(self):
        return 221000

    # Gibt die Aktuelle Version des Cores aus
    def get_core_version(self):
        return self.___core_socket.core_version

    # Wird verwendet um die Informationen auszuelesen
    def get_request(self, requestTypes:PostRequestTypes):
        # Es wird geprüft ob es sich um einen Bekannten Vorgang handelt
        if(requestTypes in [PostRequestTypes.GET_ALL_CONNECTED_NODES, PostRequestTypes.GET_ALL_KNOWN_ROUTES, PostRequestTypes.GET_ALL_LOCAL_ADDRESSES]) != True:
            raise Exception('UNKOWN_REQUEST')

        # Es wird eine neue Prozess ID erzeugt
        procId = str(uuid.uuid4())

        # Das Anfrage Paket wird gebaut
        request_package = { "type":"get", "cmd":requestTypes.value, "process_id":procId }

        # Speichert Eintreffende Antwortpakete ab
        resolved_packages = list()

        # Nimmt eintreffende Pakete entgegen
        def enterup_data(package):
            resolved_packages.append(package)

        # Der Request vorgang wird Zwischengespeichert
        self.___open_processes[procId] = enterup_data

        # Das Paket wird an die Gegenseite übermittelt
        self.___core_socket.write(request_package)

        # Speichert alle Geprüften Datensätze zwischen
        checked_data, final_frame = list(), None

        # Die Schleife wird solange ausgeführt, bis eine Antwort eingetroffen ist
        while self.___while_can_run():
            # Es wird geprüft ob ein Antwortpaket vorhanden ist
            if len(resolved_packages) > 0:
                # Der erste Eintrag aus der Warteschlange wird abgerufen
                poped_item = resolved_packages.pop(0)

                # Es wird geprüft ob die benötigten Daten felder vorhanden sind
                if('data' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('isframe' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('final' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('reman' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return

                # Es wird geprüft ob es sich um das Finale Paket handelt, wenn ja wird der Vorgang hier beendet
                if poped_item['final'] == True and poped_item['isframe'] == False and poped_item['reman'] == 0:
                    # Es wird geprüft ob bereits ein andere Eintrag vorhanden ist
                    if len(checked_data) != 0:
                        print('INVALID_DATA')
                        return

                    # Das Frame wird als Finales Frame gespeichert
                    final_frame = poped_item
                    break

                # Das Paket wird der Warteschlange hinzugefügt
                checked_data.append(poped_item['data'])

                # Es wird geprüft ob es sich um das letze Paket handelt
                if poped_item['final'] == True and poped_item['reman'] == 0: break
            else: time.sleep(1/1000)

        # Der Vorgang wird entfernt
        del self.___open_processes[procId]

        # Es wird geprüft ob es ein Finales Paket gibt, wenn nicht wird das Paket aus den Einzelnen Antworten zusammengesetzt
        if final_frame == None:
            final_byte_string = bytes()
            for item in reversed(checked_data): final_byte_string += item

            # Es wird versucht das Finale Paket einzulesen
            final_frame = cbor2.loads(final_byte_string)

        # Die Daten werden Final verarbeitet
        if requestTypes == PostRequestTypes.GET_ALL_CONNECTED_NODES:
            interval = list()
            for recv in final_frame['data']: interval.append(NodeConnection(recv['version'], recv['end_point'], recv['connected_since'], recv['io_data'], recv['session_id'], recv['enabeld_services']))
            return interval
        elif requestTypes == PostRequestTypes.GET_ALL_KNOWN_ROUTES:
            interval = list()
            for recv in final_frame['data']: interval.append(KnownAddressRoute(recv['address']))
            return interval
        elif requestTypes == PostRequestTypes.GET_ALL_LOCAL_ADDRESSES:
            interval = list()
            for recv in final_frame['data']: interval.append(LocalAddress(recv))
            return interval
        else:
            raise Exception('UNKOWN_ITNERNAL_ERROR')

    # Wird verwendet um die Informationen zu senden
    def post_request(self, requestTypes:PostRequestTypes, args=[]):
        # Es wird geprüft ob es sich um einen Bekannten Vorgang handelt
        if(requestTypes in [PostRequestTypes.GET_ALL_CONNECTED_NODES, PostRequestTypes.GET_ALL_KNOWN_ROUTES, PostRequestTypes.GET_ALL_LOCAL_ADDRESSES]) != True:
            raise Exception('UNKOWN_REQUEST')

        # Es wird eine Anfrage an den Dienst gestellt um einen neuen POST Vorgang zu Initlaisieren

        # Es wird eine neue Prozess ID erzeugt
        procId = str(uuid.uuid4())

        # Das Anfrage Paket wird gebaut
        request_package = { "type":"post", "cmd":requestTypes.value, "process_id":procId, "args":args }

        # Speichert Eintreffende Antwortpakete ab
        resolved_packages = list()

        # Nimmt eintreffende Pakete entgegen
        def enterup_data(package):
            resolved_packages.append(package)

        # Der Request vorgang wird Zwischengespeichert
        self.___open_processes[procId] = enterup_data

        # Das Paket wird an die Gegenseite übermittelt
        self.___core_socket.write(request_package)

        # Speichert alle Geprüften Datensätze zwischen
        checked_data, final_frame = list(), None

        # Die Schleife wird solange ausgeführt, bis eine Antwort eingetroffen ist
        while self.___while_can_run():
            # Es wird geprüft ob ein Antwortpaket vorhanden ist
            if len(resolved_packages) > 0:
                # Der erste Eintrag aus der Warteschlange wird abgerufen
                poped_item = resolved_packages.pop(0)

                # Es wird geprüft ob die benötigten Daten felder vorhanden sind
                if('data' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('isframe' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('final' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return
                if('reman' in poped_item) != True:
                    print('INVALD_RESPONSE')
                    return

                # Es wird geprüft ob es sich um das Finale Paket handelt, wenn ja wird der Vorgang hier beendet
                if poped_item['final'] == True and poped_item['isframe'] == False and poped_item['reman'] == 0:
                    # Es wird geprüft ob bereits ein andere Eintrag vorhanden ist
                    if len(checked_data) != 0:
                        print('INVALID_DATA')
                        return

                    # Das Frame wird als Finales Frame gespeichert
                    final_frame = poped_item
                    break

                # Das Paket wird der Warteschlange hinzugefügt
                checked_data.append(poped_item['data'])

                # Es wird geprüft ob es sich um das letze Paket handelt
                if poped_item['final'] == True and poped_item['reman'] == 0: break
            else: time.sleep(1/1000)

        # Der Vorgang wird entfernt
        del self.___open_processes[procId]

        # Es wird geprüft ob es ein Finales Paket gibt, wenn nicht wird das Paket aus den Einzelnen Antworten zusammengesetzt
        if final_frame == None:
            final_byte_string = bytes()
            for item in reversed(checked_data): final_byte_string += item

            # Es wird versucht das Finale Paket einzulesen
            final_frame = cbor2.loads(final_byte_string)

        # Die Daten werden Final verarbeitet
        if requestTypes == PostRequestTypes.GET_ALL_CONNECTED_NODES:
            interval = list()
            for recv in final_frame['data']: interval.append(NodeConnection(recv['version'], recv['end_point'], recv['connected_since'], recv['io_data'], recv['session_id'], recv['enabeld_services']))
            return interval
        elif requestTypes == PostRequestTypes.GET_ALL_KNOWN_ROUTES:
            interval = list()
            for recv in final_frame['data']: interval.append(KnownAddressRoute(recv['address']))
            return interval
        elif requestTypes == PostRequestTypes.GET_ALL_LOCAL_ADDRESSES:
            interval = list()
            for recv in final_frame['data']: interval.append(LocalAddress(recv))
            return interval
        else:
            raise Exception('UNKOWN_ITNERNAL_ERROR')


## Easy Core API Object
class EasyIpnApi:
    def __init__(self, coreAPI:CoreAPI) -> None:
        self.___core_api = coreAPI

    # Wird verwendet um die Informationen auszuelesen
    def get_request(self, requestTypes:PostRequestTypes) -> dict:
        return self.___core_api.get_request(requestTypes)

    # Gibt die Aktuelle Version des Cores aus
    def get_core_version(self):
        return self.___core_api.get_core_version()

    # Gibt die Version der API aus
    def get_api_Version(self):
        return self.___core_api.get_api_Version()

    # Gibt alle Verbundenen Nodes aus
    def get_all_connected_nodes(self) -> list:
        return self.___core_api.get_request(PostRequestTypes.GET_ALL_CONNECTED_NODES)

    # Gibt alle Verfügabren Routen aus
    def get_all_known_routes(self) -> list:
        return self.___core_api.get_request(PostRequestTypes.GET_ALL_KNOWN_ROUTES)

    # Gibt alle Lokalen Adressen aus
    def get_all_local_addresses(self) -> list:
        return self.___core_api.get_request(PostRequestTypes.GET_ALL_LOCAL_ADDRESSES)

    # Gibt alle Privaten Schlüssel oder ihre ID's aus
    def get_all_local_private_key_ids(self) -> list:
        return self.___core_api.get_request(PostRequestTypes.GET_ALL_KNOWN_ROUTES)