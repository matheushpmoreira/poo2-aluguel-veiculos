"""Backend package for the vehicle rental vehicle_rental_system."""

from matheushpmoreira.vehicle_rental_system.backend.errors import BackendError, BadRequestError, ConflictError, NotFoundError, UnauthorizedError

__all__ = [
    "BackendError",
    "BadRequestError",
    "ConflictError",
    "NotFoundError",
    "UnauthorizedError",
]
