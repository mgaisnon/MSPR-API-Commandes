from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="PayeTonKawa - API Commandes")
Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/commandes")
async def get_commandes():
    return {"message": "Commandes API is running"}