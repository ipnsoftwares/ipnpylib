from ipnpy_api._core import CoreAPI



with CoreAPI() as core:
    # Die API und die Core Version wird angezeigt
    print('IPN-Core version:', core.get_core_version())
    print('IPN-API version:', core.get_api_Version())

    # Es werden alle Verfügabren Nodes abgerufen
    print(core.get_all_connected_nodes())

    # Es werden alle bekannten Routen abgerufen
    print(core.get_all_known_routes())

    # Es werden alle Lokalen Adressen abgerufen
    print(core.get_all_local_addresses())