from typing import TypeVar, Generic

T = TypeVar("T")


class CustomResponse(Generic[T]):
    @staticmethod
    def success_response(message, data=T, statusCode=200) -> dict:
        return {
            "status": True,
            "statusCode": statusCode,
            "error": None,
            "message": message,
            "data": data
        }

    @staticmethod
    def error_response(message, error,data: T = None, statusCode=400) -> dict:
        return {
            "success": False,
            "statusCode": statusCode,
            "message": message,
            "error": error,
            "data": data
        }
