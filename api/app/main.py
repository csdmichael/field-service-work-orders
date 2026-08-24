"""Service layer for the generated project."""
from fastapi import FastAPI

app = FastAPI(title="Field Service Work Orders API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
