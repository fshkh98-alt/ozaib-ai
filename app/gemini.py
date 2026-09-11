import os
import requests

# استخدام Gemini API الإصدار الجديد
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

SYSTEM_INSTRUCTION = """أنت CyberGuard AI، شات بوت تعليمي متخصص في الأمن السيبراني. أجب بالعربية مع شرح واضح."""

def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("لم يتم العثور على GEMINI_API_KEY في ملف .env")

    # بناء المحادثة بالـ interactions format
    contents = []
    for item in history:
        role = "model" if item["role"] == "model" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": item["content"]}]
        })
    
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 1200
        }
    }

    # إرسال الطلب مع ترميز UTF-8
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    url = f"{GEMINI_URL}?key={api_key}"
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(f"خطأ API {response.status_code}: {response.text[:200]}")

    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"استجابة غير صالحة من Gemini")