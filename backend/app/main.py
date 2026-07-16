from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.exceptions import validation_exception_handler, http_exception_handler, global_exception_handler

app = FastAPI(title="HR Tool API", version="1.0.0")

# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.routers import templates, candidates, generator
app.include_router(templates.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(generator.router, prefix="/api")
