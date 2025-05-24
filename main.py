import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from fastapi import FastAPI
from chat_api import router as chat_router
import uvicorn

app = FastAPI()

app.include_router(chat_router, prefix="/chatapi")

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

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    conversation = [
        {"role": "system", "content": "شما یک پزشک یا دستیار پزشک هستید و به طراحی یک سیستم غربالگری هوشمند سلامت کمک می‌کنید."},
        {"role": "user", "content": message}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation
    )
    answer = response.choices[0].message.content
    return {"answer": answer}

@app.get("/")
async def root():
    return {"message": "سلام! سرویس سلامت در حال اجرا است."}

if __name__ == "__main__":
    port = 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
