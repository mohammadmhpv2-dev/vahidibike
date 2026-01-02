from woocommerce import API
import config

wcapi = API(
    url=config.WOO_URL,
    consumer_key=config.WOO_CK,
    consumer_secret=config.WOO_CS,
    version="wc/v3",
    timeout=60
)

def send_product(final_data, mapped_data):
    """
    ارسال محصول با استفاده از ID های مپ شده
    """
    print("📤 در حال ارسال محصول به ووکامرس...")
    
    # ساخت ویژگی‌ها (Attributes)
    attributes = []
    
    # ۱. رنگ (Global Attribute)
    if mapped_data.get("color_id"):
        attributes.append({
            "id": 2, # فرض: آی دی ویژگی رنگ در سایت شما ۲ است (باید از fetch_ids چک کنی)
            "options": [mapped_data["brand_name"]] if mapped_data.get("brand_id") else [mapped_data["brand_name"]], 
            # نکته: برای Global Attribute باید ID ترم را بفرستیم یا نام دقیق
            # روش بهتر: نام دقیق رو میفرستیم چون ID کلی ویژگی رو داریم
            "name": "رنگ",
            "visible": True,
            "variation": False,
            "options": [mapped_data["color"]]
        })

    # ساختار محصول
    product_json = {
        "name": final_data["title"],
        "type": "simple",
        "status": "draft", # حتما پیش نویس باشه تا چک کنی
        "description": final_data["description"],
        "short_description": final_data["short_desc"], # این میره تو توضیحات کوتاه کنار محصول
        "manage_stock": True,
        "stock_quantity": 1, # موجودی دقیق ۱
        "regular_price": "0", # قیمت رو بعدا دستی بزن یا از اکسل بخون
        "meta_data": [
            {
                "key": "_yoast_wpseo_metadesc",
                "value": final_data["short_desc"] # توضیحات متا برای گوگل
            },
            {
                "key": "_yoast_wpseo_title",
                "value": final_data["title"] # تایتل سئو
            }
        ]
    }

    # اضافه کردن دسته‌بندی (اگر پیدا شده بود)
    if mapped_data.get("category_id"):
        product_json["categories"] = [{"id": mapped_data["category_id"]}]

    # ارسال
    try:
        response = wcapi.post("products", product_json)
        if response.status_code == 201:
            pid = response.json()['id']
            print(f"✅ محصول با موفقیت ساخته شد! ID: {pid}")
            print(f"لینک: {config.WOO_URL}/wp-admin/post.php?post={pid}&action=edit")
            return pid
        else:
            print(f"❌ خطا در ارسال: {response.text}")
            return None
    except Exception as e:
        print(f"❌ خطای ارتباط: {e}")
        return None