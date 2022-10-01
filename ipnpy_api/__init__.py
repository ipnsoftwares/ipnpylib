import platform, tempfile


# Gibt den Aktuellen Temporären Pfad aus
def get_file_path(fname) -> str:
    return str(f"{tempfile.gettempdir()}/ipn/{fname}" if platform.system() == "Darwin" else '/temp')


# Speichert alle Parameter ab
root_parameters = [
    'list-nodes',
    'list-address-routes'
]