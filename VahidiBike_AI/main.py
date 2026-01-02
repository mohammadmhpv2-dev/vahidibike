import os
import glob
import requests
import urllib3
import json
from woocommerce import API
import config
from core.extractor import extract_bike_data
from core.mapping import finalize_product_data

# غیرفعال کردن اخطار SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# سشن مستقیم
direct_session = requests.Session()
direct_session.trust_env = False 

wcapi = API(
    url=config.WOO_URL,
    consumer_key=config.WOO_CK,
    consumer_secret=config.WOO_CS,
    version="wc/v3",
    timeout=120,
    verify_ssl=False,
    session=direct_session
)

def main():
    print("--- 🏁 شروع عملیات اتوماتیک وحیدی‌بایک ---")
    print(f"📂 مسیر اجرا: {os.getcwd()}")

    # 1. پیدا کردن عکس (jpg, jpeg, webp)
    files = glob.glob(os.path.join("uploads", "*"))
    images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.webp', '.png'))]
    
    if not images:
        print("❌ هیچ عکسی در پوشه uploads پیدا نشد!")
        return

    img_path = images[0]
    print(f"✅ عکس پیدا شد: {img_path}")

    # 2. تحلیل با هوش مصنوعی
    print("📡 در حال ارسال به Gemini-2.5-Flash...")
    ai_raw = extract_bike_data(img_path)
    
    if not ai_raw:
        print("❌ خطا: خروجی از گوگل دریافت نشد.")
        return
    print(f"📝 دیتای خام دریافت شد: {ai_raw.get('name')}")

    # 3. تطبیق با نقشه سایت (Mapping)
    print("🔗 در حال تطبیق با داده‌های سایت...")
    final = finalize_product_data(ai_raw)
    
    if not final:
        print("❌ خطا در مرحله Mapping.")
        return

    # 4. آماده سازی ویژگی‌ها (Attributes)
    # این بخش خیلی مهم است تا ویژگی تکراری نسازد
    prod_attributes = []

    # الف) ویژگی رنگ
    prod_attributes.append({
        "name": "رنگ",
        "visible": True,
        "variation": False,
        "options": [final["color"]]
    })

    # ب) ویژگی برند (فقط اگر در سایت پیدا شده بود)
    if final.get("brand_id"):
        # اگر ID ویژگی برند را داری (مثلا 50 یا 8) اینجا بنویس: "id": 50,
        # اگر نداری، همین که نامش دقیق باشد (که ما دقیق کردیم) کافیست.
        prod_attributes.append({
            "name": "برند", # نام دقیق ویژگی در سایت
            "visible": True,
            "options": [final["brand_name"]] # نام دقیق ترم (مثلا TRINX)
        })
    
    # ج) ساخت Payload نهایی
    payload = {
        "name": final["title"],
        "status": "pending", # در انتظار بررسی
        "description": final["description"],
        "short_description": final["short_desc"],
        "categories": [{"id": final["category_id"]}],
        "regular_price": final["price"],
        "attributes": prod_attributes
    }

    # 5. ارسال به ووکامرس
    try:
        print(f"📤 در حال ارسال محصول '{final['title']}' ...")
        res = wcapi.post("products", payload)
        
        if res.status_code == 201:
            product_id = res.json().get('id')
            print(f"✅✅ موفقیت آمیز بود! محصول ثبت شد.")
            print(f"🆔 ID محصول: {product_id}")
            print(f"🔗 لینک ویرایش: {config.WOO_URL}/wp-admin/post.php?post={product_id}&action=edit")
            
            # انتقال عکس پردازش شده به پوشه done (اختیاری)
            # os.rename(img_path, os.path.join("uploads", "done", os.path.basename(img_path)))
            
        else:
            print(f"❌ خطا در ووکامرس: {res.status_code}")
            print(res.text)
            
    except Exception as e:
        print(f"🚨 خطای غیرمنتظره: {e}")

if __name__ == "__main__":
    main()