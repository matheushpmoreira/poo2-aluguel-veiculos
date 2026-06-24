from http import HTTPStatus


class AppError(ValueError):
    status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    @property
    def status_code(self) -> int:
        return self.status.value

    @property
    def reason(self) -> str:
        return self.status.phrase

    def __str__(self) -> str:
        return f"{self.status_code} {self.reason}: {self.message}"


class BadRequestError(AppError):
    status = HTTPStatus.BAD_REQUEST


class UnauthorizedError(AppError):
    status = HTTPStatus.UNAUTHORIZED


class NotFoundError(AppError):
    status = HTTPStatus.NOT_FOUND


class ConflictError(AppError):
    status = HTTPStatus.CONFLICT


class UnprocessableEntityError(AppError):
    status = HTTPStatus.UNPROCESSABLE_ENTITY
