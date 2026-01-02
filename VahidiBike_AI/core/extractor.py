import json
import base64
import mimetypes
from google import genai
from google.genai import types
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)

def extract_bike_data(image_path, voice_path=None):
    MODEL_ID = "gemini-2.5-flash" 
    print(f"🚀 آنالیز تصویر: {image_path}")

    try:
        # تشخیص خودکار نوع فایل (JPEG یا WEBP)
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg" # پیش‌فرض

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        contents = [
            types.Part.from_bytes(data=base64.b64decode(image_data), mime_type=mime_type),
            """
            تو متخصص سئو و دوچرخه هستی. خروجی JSON بده.
            دقت کن:
            1. name: تایتل جذاب شامل برند، مدل و ویژگی مهم.
            2. brand_en: فقط نام برند به انگلیسی (مثلا VIVA).
            3. size: سایز چرخ (مثلا 26).
            4. color: رنگ اصلی بدنه به فارسی.
            5. description: توضیحات محصول HTML (با تگ h2, ul, li).
            6. short_description: توضیحات متا (حداکثر 160 کاراکتر).
            7. regular_price: قیمت به تومان (عدد خالی) اگر یافتی، وگرنه 0.
            """
        ]

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents
        )
        
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        
        return json.loads(raw_text)

    except Exception as e:
        print(f"🚨 خطا در جمینای: {e}")
        return None