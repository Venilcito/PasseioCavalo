from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json

from algoritmos.idaestrela import ida_estrela 
from algoritmos.dfs_semheuristica import dfs_interface

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.websocket('/ws/cavalo')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        config = json.loads(data)

        algoritmo = config.get('algoritmo')
        bruto_path = config.get('inicio')
        caminho = [(passo['x'], passo['y']) for passo in bruto_path]

        if(algoritmo == "a*"):
            INICIAL = caminho
            resultado, gerados, expandidos, iteracoes = ida_estrela(INICIAL)

            for coordenada in resultado:
                #await asyncio.sleep(0.01)

                caminho.append({"x": coordenada[0], "y": coordenada[1]})

                payload = {
                    "status": "rodando",
                    "algoritmo": algoritmo,
                    "caminho": caminho,
                    "ger": gerados,
                    "exp": expandidos,
                    "iter": iteracoes
                }

                await websocket.send_json(payload)

        elif algoritmo == "dfs":
            INICIAL = caminho

            resultado, gerados, expandidos, iteracoes = dfs_interface(INICIAL)

            caminho_json = [{
                "x": resultado[0][0],
                "y": resultado[0][1]
            }]

            for coordenada in resultado[1:]:
                # await asyncio.sleep(0.01)

                caminho_json.append({
                    "x": coordenada[0],
                    "y": coordenada[1]
                })

                payload = {
                    "status": "rodando",
                    "algoritmo": algoritmo,
                    "caminho": caminho_json,
                    "ger": gerados,
                    "exp": expandidos,
                    "iter": iteracoes
                }

                await websocket.send_json(payload)

        await websocket.send_json({"status": "fim"})
    
    except Exception as e:
        print(e)

# INICIANDO!!!!!
@app.get("/")
async def get_index():
    return FileResponse("static/index.html")