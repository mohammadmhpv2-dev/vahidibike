import json

def build_full_content(mapped_data):
    """
    ساخت تایتل، توضیحات کامل HTML، و اسکیما
    """
    brand = mapped_data.get("brand_name", "دوچرخه")
    model = mapped_data.get("model_name", "")
    size = mapped_data.get("size", "")
    
    # ۱. ساخت تایتل استاندارد
    # الگو: خرید دوچرخه [برند] [مدل] سایز [سایز] | دوچرخه وحیدی مشهد
    title = f"خرید دوچرخه {brand} مدل {model} سایز {size} | دوچرخه وحیدی مشهد"
    
    # ۲. ساخت توضیحات HTML با نقاط قوت و ضعف
    html_desc = mapped_data["seo"]["long_desc_html"]
    
    # اضافه کردن باکس نقاط قوت و ضعف
    if mapped_data["seo"]["pros"] or mapped_data["seo"]["cons"]:
        html_desc += '<div class="review-box" style="display: flex; gap: 20px; margin-top: 20px;">'
        
        if mapped_data["seo"]["pros"]:
            pros_li = "".join([f"<li>✅ {p}</li>" for p in mapped_data["seo"]["pros"]])
            html_desc += f'<div style="flex:1; border: 1px solid #4caf50; padding: 10px; border-radius: 8px;"><h4>نقاط قوت</h4><ul style="list-style: none; padding: 0;">{pros_li}</ul></div>'
            
        if mapped_data["seo"]["cons"]:
            cons_li = "".join([f"<li>❌ {c}</li>" for c in mapped_data["seo"]["cons"]])
            html_desc += f'<div style="flex:1; border: 1px solid #f44336; padding: 10px; border-radius: 8px;"><h4>نقاط ضعف</h4><ul style="list-style: none; padding: 0;">{cons_li}</ul></div>'
            
        html_desc += '</div>'

    # ۳. ساخت اسکیما (FAQ)
    schema_faq = []
    for faq in mapped_data["seo"]["faqs"]:
        schema_faq.append({
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["answer"]
            }
        })
        
    schema_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": schema_faq
    }
    
    # اضافه کردن اسکیما به انتهای توضیحات (به صورت مخفی یا اسکریپت)
    # ترفند: یواست خودش اسکیما می‌سازد اما برای FAQ می‌توانیم اسکریپت تزریق کنیم اگر ادیتور اجازه دهد
    # یا می‌توانیم متن سوال و جواب را در توضیحات اضافه کنیم.
    
    return {
        "title": title,
        "description": html_desc,
        "short_desc": mapped_data["seo"]["short_desc_yoast"],
        "schema": json.dumps(schema_faq) # این را بعدا می توان با پلاگین های خاص ست کرد
    }