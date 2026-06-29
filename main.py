from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json

from algoritmos.idaestrela import ida_estrela 
from algoritmos.dfs_semheuristica import dfs_interface

# APLICAÇÃO: usando WebSockets com o FastAPI para fazer a comunicação dos algoritmos com o front
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.websocket('/cavalo')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        config = json.loads(data)

        algoritmo = config.get('algoritmo')
        bruto_path = config.get('inicio')
        tempo_max = config.get('max')
        caminho = [(passo['x'], passo['y']) for passo in bruto_path]

        if algoritmo == "ida*":
            resultado, gerados, expandidos, tempo = ida_estrela(caminho, tempo_max)

        elif algoritmo == "dfs":
            resultado, gerados, expandidos, tempo = dfs_interface(caminho, tempo_max)

        # Lista que será enviada para a interface 
        caminho_json = []

        # Monta o JSON e envia um movimento pot vez
        for coordenada in resultado:
            caminho_json.append({"x": coordenada[0], "y": coordenada[1]})

            payload = {
                "status": "rodando",
                "algoritmo": algoritmo,
                "caminho": list(caminho_json),
                "ger": gerados,
                "exp": expandidos,
                "tempo": tempo
            }

            await websocket.send_json(payload)
            #await asyncio.sleep(0.2)

        await websocket.send_json({"status": "fim"})
    
    except Exception as e:
        print(e)

# INICIANDO!!!!!
@app.get("/")
async def get_index():
    return FileResponse("static/index.html")