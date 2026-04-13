import socket


def get_node_metadata():
    metadata = {}

    # Hostname
    metadata["hostname"] = socket.gethostname()

    # Private IP
    try:
        metadata["local_ip"] = socket.gethostbyname(socket.gethostname())
    except Exception:
        metadata["local_ip"] = None

    # Public IP (best-effort)
    try:
        import urllib.request
        metadata["public_ip"] = urllib.request.urlopen(
            "https://api.ipify.org"
        ).read().decode("utf-8")
    except Exception:
        metadata["public_ip"] = None

    return metadata
