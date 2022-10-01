from ipnpy_api import root_parameters, get_file_path
from ipnpy_api.cmdline import CommandlineAPI
from texttable import Texttable
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

    # Die Commandline API wird vorbereitet
    cmdline = CommandlineAPI(get_file_path('none_root.sock'))

    # Die Ausgabe wird erzeugt
    if first_parameter == "list-nodes":
        t = Texttable()
        t.add_rows([['Node address', 'Version', 'End point', 'Connected since'], *[i._tlist for i in cmdline.get_all_node_connections()]])
        print(t.draw())
    elif first_parameter == "list-address-routes":
        t = Texttable()
        t.add_rows([['Address', 'Route known since',], *[i._tlist for i in cmdline.get_all_known_routes()]])
        print(t.draw())
    else:
        raise Exception('INTERNAL_ERROR')