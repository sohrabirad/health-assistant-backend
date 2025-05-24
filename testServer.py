import asyncio
import websockets

async def test_ws():
    uri = "wss://health-assistant-backend-production.up.railway.app/ws/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send("سلام")
        response = await websocket.recv()
        print("پاسخ:", response)

asyncio.run(test_ws())
