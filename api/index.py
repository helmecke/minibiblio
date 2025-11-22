from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.patrons import router as patrons_router

app = FastAPI(docs_url="/api/python/docs", openapi_url="/api/python/openapi.json")

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


@app.get("/api/python/healthcheck")
def healthchecker():
    return {
        "status": "success",
        "message": "Integrated FastAPI Framework with Next.js successfully!",
    }
