from fastapi import FastAPI
import time

app = FastAPI(title="Herbbie Minimal", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Herbbie minimal version is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": time.time(),
        "version": "minimal",
        "message": "Herbbie minimal application is running"
    }
