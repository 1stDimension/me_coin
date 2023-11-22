from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import os
import uvicorn
import ipaddress
from contextlib import asynccontextmanager

PORT = int(os.environ.get("ME_COIN_PORT",8000))
HOST = ipaddress.ip_address(os.environ.get("ME_COIN_HOST","127.0.0.1"))
PROTOCOL =os.environ.get("ME_COIN_PROTOCOL","http")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print ("I'm worker") 
    yield
    print("stuff")
    print ("I'm done worker") 

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get():
    return {"msg": "This is a worker"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        await websocket.send_text(f"Message text was: {data}")

if __name__ == "__main__":
    uvicorn.run(app, host=str(HOST), port=PORT)  