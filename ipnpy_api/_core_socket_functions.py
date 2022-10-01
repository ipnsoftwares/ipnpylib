from ipnpy_api._value_objects import *
import cbor2, socket, time
import threading



# Stellt alle Grundlegenden Funktionen für das senden sowie Empfangen bereit
class _CoreSingleSocket:
    # Konstruktor
    def __init__(self, path) -> None:
        # Create a UDS socket
        self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__thread = threading.Thread(target=self.___package_reader, args=(), daemon=True)
        self.__finallyConnection = False
        self.__cache = list()

        # Die Verbindung wird hergestellt
        try: self.__sock.connect(path)
        except Exception as E: print(E); return

        # Es wird gewartet dass das HelloPackage empfangen wurde
        try: core_hello_package = cbor2.loads(self.__sock.recv(8192))
        except Exception as E: print(E); return

        # Speichert die Aktuelle SessionId sowie die Aktuelle Version der gegenseite ab
        vatr = { "ver":10000000, "lang":"py", "pid":core_hello_package['pid'] }

        # Speichert die Aktuelle ProzessID ab
        self.__cpid = core_hello_package['pid']

        # Der Reader Thread wird gestartet
        self.__thread.start()

        # Das Paket wird an die Gegenseite gesendet
        try: self.__sock.send(cbor2.dumps(vatr))
        except Exception as E: print(E); return

    # Wird als Thread ausgeführt und nimmt eintreffende Pakete entgegen
    def ___package_reader(self):
        # Es wird geprüft ob der Vorgang bereits Initalisiert wurde
        if self.__finallyConnection == False:
            # Es wird auf die fertigstellungsantwort des Cores gewartet
            try: frecp = self.__sock.recv(1)
            except Exception as E: print(E); return
            if frecp != b'd':
                self.__sock.close()
                raise Exception('INTERNAL_ERROR')
            self.__finallyConnection = True

        # Die Schleife wird solange ausgeführt bis Daten eingetroffen sind
        while True:
            try:
                # Es wird auf eintreffende Pakete gewartet
                lastr = self.__sock.recv(8192)
                if len(lastr) == 0: return
                recd = cbor2.loads(lastr)

                # Es wird geprüft ob es ein Paket für diese Sitzung gibt
                del recd['pid']
                self.__cache.append(recd)

                # Es wird bestätigt dass das Paket empfangen wurde
                self.__sock.send(cbor2.dumps({ "type":"response" }))
            except Exception as E:
                print(E)

    # Wird verwendet um einen Datensatz zu versenden
    def _write(self, data):
        # Es wird geprüft ob die Verbindung erfolgreich fertigestellt wurde
        while self.__finallyConnection == False: time.sleep(1/1000)

        # Das Paket wird an die gegenseite gesendet
        try: state = self.__sock.send(cbor2.dumps({ "pid":self.__cpid, **data }))
        except Exception as E: raise E
        return state

    # Wird verwendet um eine Sitzung zu löschen
    def _delete_session(self, session_id):
        if(session_id in self.__open_sessions) == True:
            del self.__open_sessions[session_id]

    # Wird verwendet um zu bestätigen dass das letzt Paket empfangen wurde, danach wird die Verbindung geschlossen
    def _finally_and_close(self):
        # Es wird bestätigt dass das Paket empfangen wurde
        self.__sock.send(cbor2.dumps({ "type":"response" }))

    # Gibt eingetorffene Pakete aus
    def _read(self):
        while len(self.__cache) == 0: time.sleep(1/1000)
        return self.__cache.pop(0)