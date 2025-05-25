import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import uvicorn
from io import BytesIO
from PyPDF2 import PdfReader
import traceback

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در تولید محدودش کنید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key
api_key = os.getenv("YOUR_GAPGPT_API_KEY")
if not api_key:
    raise ValueError("لطفا متغیر محیطی YOUR_GAPGPT_API_KEY را تنظیم کنید.")

# OpenAI Client
client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=api_key)

# بارگذاری فایل‌های استاتیک (در صورتی که نیاز به نمایش فایل‌ها باشد)
app.mount("/static", StaticFiles(directory="Front"), name="static")

# چت با مدل
@app.post("/chat")
async def chat_endpoint(request: Request, file: UploadFile = File(None)):
    # دریافت محتوای پیام کاربر
    data = await request.json()
    conversation = data.get("conversation")
    model = data.get("model", "gpt-4o")

    # اگر فایل ارسال شده باشد
    if file:
        try:
            file_content = await file.read()
            if file.filename.endswith('.pdf'):
                # استخراج متن از PDF
                text = extract_text_from_pdf(file_content)
            else:
                # فرض می‌کنیم که فایل متنی است
                text = file_content.decode('utf-8')
            
            # اضافه کردن محتوای فایل به مکالمه
            conversation.append({"role": "user", "content": text})
        except Exception as e:
            return {"error": f"خطا در پردازش فایل: {str(e)}"}

    # اگر conversation موجود نباشد، یک مقدار پیش‌فرض قرار می‌دهیم
    if not conversation or not isinstance(conversation, list):
        conversation = [
            {"role": "system", "content": "شما یک فرد خبره هستید و در حال کار با یک دستیار هوشمند می باشید."}
        ]

    # ارسال مکالمه به مدل OpenAI و دریافت پاسخ
    try:
        response = client.chat.completions.create(
            model=model,
            messages=conversation
        )
        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        # اضافه کردن لاگ خطا
        error_details = traceback.format_exc()  # نمایش جزئیات دقیق خطا
        return {"error": f"مشکلی در ارتباط با مدل {model} پیش آمد: {str(e)}\nDetails: {error_details}"}

# استخراج متن از فایل PDF
def extract_text_from_pdf(file_content: bytes) -> str:
    """استخراج متن از فایل PDF"""
    try:
        pdf_reader = PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise ValueError(f"خطا در پردازش فایل PDF: {str(e)}")

# روت اصلی
@app.get("/")
async def root():
    return {"message": "سلام! سرویس در حال اجرا است."}

# اجرای برنامه
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
