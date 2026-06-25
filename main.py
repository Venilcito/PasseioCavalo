from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.websocket('/ws/cavalo')
async def websocket_endpoint(websocket: WebSocket):
    # aqui é onde ele pega os resultado do algoritmo e monta um JSON pra mandar pro front
    # por enquanto é so um for que faz o cavalo andar por ai 5 vezes

    await websocket.accept()
    try:
        data = await websocket.receive_text()
        config = json.loads(data)

        algoritmo = config.get('algoritmo')
        startX = config['inicio']['x']
        startY = config['inicio']['y']

        atualX, atualY = startX, startY
        caminho = [{"x": atualX, "y": atualY}]

        for step in range(10):
            # await asyncio.sleep(0.8)
            await asyncio.sleep(0.01)

            atualX = (atualX+1) % 8
            atualY = (atualY+2) % 8

            caminho.append({"x": atualX, "y": atualY})

            payload = {
                "status": "rodando",
                "algoritmo": algoritmo,
                "caminho": caminho,
                "passo": step + 1
            }

            await websocket.send_json(payload)
        
        await websocket.send_json({"status": "fim"})
    
    except Exception as e:
        print(e)

# INICIANDO!!!!!
@app.get("/")
async def get_index():
    return FileResponse("static/index.html")