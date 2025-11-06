# backend/api.py
from fastapi import FastAPI
from backend.audio_manager import iniciar_execucao, pausar_execucao, repetir_memoria

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "mensagem": "API Clarivox rodando!"}

@app.post("/escutar")
def escutar():
    iniciar_execucao()
    return {"status": "gravando"}

@app.post("/pausar")
def pausar():
    pausar_execucao()
    return {"status": "pausado"}

@app.post("/repetir")
def repetir():
    repetir_memoria()
    return {"status": "repetindo"}
