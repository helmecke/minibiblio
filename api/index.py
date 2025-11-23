from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.patrons import router as patrons_router
from api.routers.catalog import router as catalog_router
from api.routers.loans import router as loans_router
from api.routers.import_router import router as import_router
from api.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - database connections."""
    yield
    # Cleanup: dispose of the connection pool
    await engine.dispose()


app = FastAPI(
    docs_url="/api/python/docs",
    openapi_url="/api/python/openapi.json",
    lifespan=lifespan,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patrons_router, prefix="/api/python")
app.include_router(catalog_router, prefix="/api/python")
app.include_router(loans_router, prefix="/api/python")
app.include_router(import_router, prefix="/api/python")


@app.get("/api/python/healthcheck")
def healthchecker():
    return {
        "status": "success",
        "message": "Integrated FastAPI Framework with Next.js successfully!",
    }
