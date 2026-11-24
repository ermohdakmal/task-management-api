from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers.auth import router as auth_router
from app.api.routers.tasks import router as task_router
from app.core.config import get_settings
from app.core.exceptions import AppException

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(include_url=False)},
    )


app.include_router(auth_router)
app.include_router(task_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
