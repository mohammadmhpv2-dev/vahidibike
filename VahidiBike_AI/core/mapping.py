import json
import os

def finalize_product_data(ai_data):
    if not ai_data: return None

    # لود کردن نقشه
    map_path = os.path.join("data", "taxonomy_map.json")
    site_map = {}
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            site_map = json.load(f)

    # ۱. مپ کردن سایز به دسته‌بندی
    size_raw = str(ai_data.get("size", "26")).replace(".0", "")
    cat_id = 35 # پیش فرض
    
    # جستجو در دسته‌ها
    for name, data in site_map.get("categories", {}).items():
        # اگر سایز دقیقاً در اسم دسته بود (مثلا "دوچرخه سایز 26")
        if f"سایز {size_raw}" in name:
            cat_id = data["id"]
            break

    # ۲. مپ کردن هوشمند برند (رفع مشکل E)
    brand_input = str(ai_data.get("brand_en") or "").strip().upper()
    brand_id = None
    brand_final_name = ""

    brands_db = site_map.get("brands", {})
    
    # روش ۱: مچ دقیق (Exact Match) - اولویت اول
    if brand_input in brands_db:
        brand_id = brands_db[brand_input]
        brand_final_name = brand_input
    else:
        # روش ۲: جستجو (اگر دقیق نبود)
        # فقط در صورتی قبول میکنیم که طولش بیشتر از ۲ باشه (برای جلوگیری از باگ TR)
        for db_name, db_id in brands_db.items():
            db_upper = db_name.upper()
            if len(brand_input) > 2 and brand_input == db_upper: 
                 brand_id = db_id
                 brand_final_name = db_name
                 break
    
    # اگر برند پیدا نشد، برند را خالی رد میکنیم که در سایت "برند متفرقه" نخورد یا جدید نسازد
    
    # ۳. مپ کردن رنگ (سعی میکنیم رنگ استاندارد سایت را پیدا کنیم)
    color_input = ai_data.get("color", "مشکی")
    color_final = color_input
    # چک میکنیم اگر رنگ در لیست سایت بود، همان را بفرستیم
    if color_input in site_map.get("colors", {}):
        pass # عالی، رنگ استاندارد است
    else:
        # اگر نبود، نزدیکترین را پیدا نمیکنیم، فعلا همان متن را میفرستیم 
        # (یا میتوانی منطق مشابه برند پیاده کنی)
        pass

    return {
        "title": ai_data.get("name"),
        "description": ai_data.get("description", ""),
        "short_desc": ai_data.get("short_description", ""),
        "category_id": cat_id,
        "brand_id": brand_id,       # اگر پیدا نشه None میره
        "brand_name": brand_final_name, # نام دقیق موجود در سایت
        "color": color_final,
        "price": str(ai_data.get("regular_price", "0"))
    }