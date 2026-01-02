# fetch_ids.py
import json
import requests
from woocommerce import API
import config
import urllib3

urllib3.disable_warnings()

direct_session = requests.Session()
direct_session.trust_env = False 

wcapi = API(
    url=config.WOO_URL,
    consumer_key=config.WOO_CK,
    consumer_secret=config.WOO_CS,
    version="wc/v3",
    timeout=60,
    verify_ssl=False,
    session=direct_session
)

def get_all_items(endpoint):
    """
    این تابع به صورت خودکار تمام صفحات را ورق می‌زند
    تا همه آیتم‌ها را بگیرد (نه فقط ۱۰۰ تای اول)
    """
    items = []
    page = 1
    while True:
        print(f"🔄 در حال دریافت {endpoint} - صفحه {page}...")
        res = wcapi.get(endpoint, params={"per_page": 100, "page": page})
        
        if res.status_code != 200:
            print(f"❌ خطا در دریافت: {res.status_code}")
            break
            
        data = res.json()
        if not data: # اگر صفحه خالی بود یعنی تموم شده
            break
            
        items.extend(data)
        page += 1
    return items

def fetch_all():
    print("⏳ شروع استخراج کامل نقشه سایت...")
    data_map = {"categories": {}, "brands": {}, "colors": {}, "sizes": {}}

    # ۱. دریافت تمام دسته‌بندی‌ها
    cats = get_all_items("products/categories")
    for c in cats:
        data_map["categories"][c["name"]] = {"id": c["id"], "slug": c["slug"]}
        
    # ۲. دریافت لیست ویژگی‌های اصلی (برای پیدا کردن ID رنگ و برند)
    attrs = wcapi.get("products/attributes").json()
    
    # پیدا کردن ID ویژگی‌های سراسری
    color_attr_id = next((item['id'] for item in attrs if item['slug'] == 'pa_color'), None)
    brand_attr_id = next((item['id'] for item in attrs if item['slug'] == 'pa_brand'), None) # چک کن اسلاگ برندت pa_brand باشه

    # ۳. دریافت تمام رنگ‌ها
    if color_attr_id:
        colors = get_all_items(f"products/attributes/{color_attr_id}/terms")
        for c in colors:
            data_map["colors"][c["name"]] = c["id"]

    # ۴. دریافت تمام برندها
    if brand_attr_id:
        brands = get_all_items(f"products/attributes/{brand_attr_id}/terms")
        for b in brands:
            data_map["brands"][b["name"]] = b["id"] # ذخیره ID ترم برند
    else:
        print("⚠️ ویژگی برند (pa_brand) پیدا نشد! شاید برندها را جای دیگری ذخیره کردی؟")

    with open("data/taxonomy_map.json", "w", encoding="utf-8") as f:
        json.dump(data_map, f, ensure_ascii=False, indent=4)
    
    print(f"✅ نقشه سایت کامل شد! تعداد برندهای پیدا شده: {len(data_map['brands'])}")

if __name__ == "__main__":
    fetch_all()