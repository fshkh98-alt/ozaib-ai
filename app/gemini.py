import os
import requests

# استخدام Gemini API الإصدار الجديد
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

SYSTEM_INSTRUCTION = """أنت CyberGuard AI، شات بوت تعليمي متخصص في الأمن السيبراني. أجب بالعربية مع شرح واضح."""

def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("لم يتم العثور على GEMINI_API_KEY في ملف .env")

    # بناء المحادثة بالـ interactions format (الطريقة الجديدة)
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

    # إرسال الـ system instruction كـ HTTP header
    headers = {
        "Content-Type": "application/json",
        "System-Instruction": SYSTEM_INSTRUCTION
    }

    response = requests.post(
        f"{GEMINI_URL}?key={api_key}",
        json=payload,
        headers=headers,
        timeout=60
    )

    if not response.ok:
        error_detail = response.text[:400]
        print(f"Gemini API Error {response.status_code}: {error_detail}")
        raise RuntimeError(f"خطأ API: {response.status_code}")

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        print(f"Parse Error: {data}")
        raise RuntimeError(f"استجابة غير صالحة من Gemini")