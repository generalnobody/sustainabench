import socket
import os

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

# If initialized, this function will return (rank, local_rank) of the current process in MPI (or other similar processes if implemented in this function)
def get_mpi_ranks() -> tuple[int | None, int | None]: 
    rank_str = ( # Should cover most MPI rank env variables.
        os.getenv("OMPI_COMM_WORLD_RANK")
        or os.getenv("PMI_RANK")
        or os.getenv("SLURM_PROCID")
    )

    local_rank_str = ( # Should cover most MPI local rank env variables.
        os.getenv("OMPI_COMM_WORLD_LOCAL_RANK")
        or os.getenv("MPI_LOCALRANKID")
        or os.getenv("PMI_LOCAL_RANK")
        or os.getenv("SLURM_LOCALID")
    )

    rank = local_rank = None
    if rank_str:
        rank = int(rank_str)
    if local_rank_str:
        local_rank = int(local_rank_str)

    return (rank, local_rank)
