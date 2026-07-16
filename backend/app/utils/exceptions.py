from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Bắt lỗi 422 (lỗi schema hoặc missing field)"""
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "ERR_VALIDATION",
            "message": "Dữ liệu đầu vào không hợp lệ",
            "details": exc.errors()
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Bắt lỗi HTTPException chung (404, 400...)"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"ERR_{exc.status_code}",
            "message": exc.detail
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Bắt lỗi 500, tránh leak traceback ra API"""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "ERR_500",
            "message": "Đã xảy ra lỗi hệ thống nội bộ. Vui lòng thử lại sau."
        }
    )
