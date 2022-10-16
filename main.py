from ipnpy_api import root_parameters
from ipnpy_api._core import CoreAPI
from datetime import datetime
import sys


if __name__ == '__main__':
    # Es wird geprüft ob Parameter angegeben wurdn
    if len(sys.argv) == 1:
        print('No parameter founds')
        exit(1)

    # Der erste Parameter wird abgerufen
    first_parameter = sys.argv[1]
    if(first_parameter in root_parameters) != True:
        print('Unkown command', first_parameter)
        exit(1)

    # Die Core API wird geöffnet
    with CoreAPI() as core:
        # Die Ausgabe wird erzeugt
        if first_parameter == "list-nodes":
            for i in core.get_all_connected_nodes():
                print(f"Session: {i.session_id}")
                print(f"   Connected-Since: {datetime.fromtimestamp(int(i.connected_since) / 1000.0).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   End-Point: {i.ep_address}")
                print(f"   Enabled-Options:")
                for x in i.enabeld_services:
                    print(f"      > {x}")
                print(f"   Version: {i.version}")
                print(f"   TX-Bytes: {i.writed_bytes}")
                print(f"   RX-Bytes: {i.recived_bytes}")
        elif first_parameter == "list-address-routes":
            for i in core.get_all_known_routes(): print(f"{i.pubkeyadr}")
        elif first_parameter == "list-local-addresses":
            for i in core.get_all_local_addresses(): print(f"{i.pubkeyadr}")
        else:
            raise Exception('INTERNAL_ERROR')