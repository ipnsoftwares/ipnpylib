from ipnpy_api._value_objects import *
import cbor2, socket, time
import threading



# Stellt alle Funktionen für das Senden und Empfangen auf Socket Ebende bereit -- Layer 3
class _CoreDuplexSocket:
    # Erzeugt ein neues Objekt
    def __init__(self, path) -> None:
        # Create a UDS socket
        self.__output_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Die ausgehende Verbindung wird aufgebaut
        try: self.__output_socket.connect(path)
        except Exception as E: print(E); return

        # Der Gegenseite wird mitgeteilt ob es sich um einen neuen Vorgang handelt
        try: self.__output_socket.sendall(cbor2.dumps({ "ver":221000, "lang":"py", "mode":"register_new_socket", "type":"out" }))
        except Exception as E: print(E); return

        # Es wird gewartet dass das HelloPackage empfangen wurde
        try: core_hello_package = cbor2.loads(self.__output_socket.recv(8192))
        except Exception as E: print(E); return

        # Speichert die Core Version ab
        self.__core_version = core_hello_package['version']

        # Die Zweite Socket Verbindung wird geöffnet, diese Verbindung wird verwendet um Eingehende Daten Entgegen zu nehmen
        self.___input_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Die Eingehende Verbindung wird versucht zu öffnen
        try: self.___input_socket.connect(path)
        except Exception as E: print(E); return

        # Die Eingehende Verbindung wird der ausgehenden Verbindung hinzugefügt
        try: self.___input_socket.sendall(cbor2.dumps({ "ver":221000, "lang":"py", "mode":"register_new_socket", "type":"in", "pid":core_hello_package['pid'], "isid":core_hello_package['isid'] }))
        except Exception as E: print(E); return

        # Auf der Eingehenden Verbindung wird auf die bestätigung gewartet
        try: inresolv = self.___input_socket.recv(1)
        except Exception as E: print(E); return
        if inresolv != b'd':
            self.___input_socket.close()
            self.__output_socket.close()
            return

        # Die Verbindung ist einsatzbereit
        return

    # Wird verwendet um ein Paket an die gegenseite zu übermitteln
    def write(self, data) -> None:
        # Die Daten werden an den Ausgehenden Socket übergeben
        self.__output_socket.sendall(cbor2.dumps({ "data":data }))

        # Es wird auf eine Bestätigung gewartet
        if self.__output_socket.recv(1) != b"d": raise Exception('INTERNAL_PIPE_ERROR')

        # Die Zeit die es gebraucht hat um die Daten zu übertragen wird zurückgegeben
        return True, 0

    # Wird verwendet um Eintreffende Daten entgegen zu nehemen, jedoch ohne eine bestätigung zu versenden
    def read_wc(self):
        # Es wird auf das Eintreffende Datenpaket der Gegenseite gewartet
        recived_data = self.___input_socket.recv(8192)

        # Die Empfangenen Daten werden zurückgegeben
        return recived_data

    # Signalisiert der Gegenseite dass das Paket erfolreich Empfangen wurde
    def signal_recived(self):
        # Der Gegenseite wird der Empfang der Daten bestätigt
        self.___input_socket.send(b"d")

    # Wird verwendet um den Socket Ordentlich zu schließen
    def close_confirmed(self):
        return

    @property
    def core_version(self):
        return self.__core_version