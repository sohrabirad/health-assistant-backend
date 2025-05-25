import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import uvicorn

app = FastAPI()

# فعال‌سازی CORS برای دسترسی از همه دامنه‌ها (در توسعه)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در تولید محدودش کن
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# سرو کردن فایل‌های استاتیک (فرانت‌اند)
app.mount("/static", StaticFiles(directory="Front"), name="static")

# مقداردهی به کلاینت OpenAI
api_key = os.getenv("YOUR_GAPGPT_API_KEY")
if not api_key:
    raise ValueError("لطفا متغیر محیطی YOUR_GAPGPT_API_KEY را تنظیم کنید.")

client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=api_key)

# مسیر اصلی چت با مدل انتخابی
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    model = data.get("model", "gpt-4o")  # مدل پیش‌فرض

    conversation = [
        {"role": "system", "content": "شما یک پزشک یا دستیار پزشک هستید و به طراحی یک سیستم غربالگری هوشمند سلامت کمک می‌کنید."},
        {"role": "user", "content": message}
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=conversation
        )
        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        return {"error": f"مشکلی در ارتباط با مدل {model} پیش آمد: {str(e)}"}

# مسیر تست سلامت API
@app.get("/")
async def root():
    return {"message": "سلام! سرویس سلامت در حال اجرا است."}

# اجرای مستقیم با Uvicorn
if __name__ == "__main__":
    port = 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
