from .local import LocalBackend
from .ray_backend import RayBackend

BACKENDS = {
    "local": LocalBackend,
    "ray": RayBackend,
}
