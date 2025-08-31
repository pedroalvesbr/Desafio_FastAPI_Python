from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import voice_actor
from app.routes import collect

# cria as tabelas no banco (se ainda não existirem)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World - API FastAPI com SQLite rodando"}


# endpoint GET /hello
@app.get("/hello")
def say_hello(name: str = "Pedro"):
    return {"message": f"Olá, {name}!"}

# incluir o router do voice_actor.py
app.include_router(voice_actor.router)

# incluir o router do voice_actor.py
app.include_router(collect.router)