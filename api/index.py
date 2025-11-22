from fastapi import FastAPI

app = FastAPI(docs_url="/api/python/docs", openapi_url="/api/python/openapi.json")


@app.get("/api/python/healthcheck")
def healthchecker():
    return {
        "status": "success",
        "message": "Integrated FastAPI Framework with Next.js successfully!",
    }
