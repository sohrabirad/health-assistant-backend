import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import uvicorn

app = FastAPI()

# فعال کردن CORS برای همه دامنه‌ها (برای توسعه راحت)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در تولید محدودش کن
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("YOUR_GAPGPT_API_KEY")
if not api_key:
    raise ValueError("لطفا متغیر محیطی YOUR_GAPGPT_API_KEY را تنظیم کنید.")

client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=api_key)

@app.get("/")
async def root():
    return {"message": "سلام! سرویس سلامت در حال اجرا است."}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation = [{"role": "system", "content": "شما یک پزشک یا دستیار پزشک هستید و به طراحی یک سیستم غربالگری هوشمند سلامت کمک می‌کنید."}]
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
