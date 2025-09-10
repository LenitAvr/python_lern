# app/main.py
from fastapi import FastAPI
from app.api.endpoints.search import router as search_router

app = FastAPI(title="gamedb")

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}

# include endpoints
app.include_router(search_router)
