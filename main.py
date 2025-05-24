from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI

app = FastAPI()
client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key='sk-wI6iYOpWHfhhVCPeLhXKty6gZRn8naBAJvcOY1i4Vi31HJOg')

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation = [{"role": "system", "content": "شما یک پزشک یا دستیار پزشک هستید و به طراحی یک سیستم غربالگری هوشمند سلامت کمک می کنید."}]
    try:
        while True:
            data = await websocket.receive_text()
            conversation.append({"role": "user", "content": data})
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation
            )
            answer = response.choices[0].message.content
            conversation.append({"role": "assistant", "content": answer})
            await websocket.send_text(answer)
    except WebSocketDisconnect:
        print("Client disconnected")
