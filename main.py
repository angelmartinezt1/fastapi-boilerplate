from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Usuario(BaseModel):
    nombre: str
    email: str

@app.get("/")
async def root():
    return {"message": "Hola mundo!"}

@app.post("/usuarios")
async def crear_usuario(usuario: Usuario):
    return {"usuario": usuario}       