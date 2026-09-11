import os
import requests

# استخدام نموذج gemini-1.5-flash المتوفر عالمياً
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_INSTRUCTION = """أنت CyberGuard AI، شات بوت تعليمي متخصص في الأمن السيبراني. أجب بالعربية مع شرح واضح."""

def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("لم يتم العثور على GEMINI_API_KEY في ملف .env")

    # بناء المحادثة
    contents = []
    for item in history:
        role = "model" if item["role"] == "model" else "user"
        contents.append({"role": role, "parts": [{"text": item["content"]}]})
    
    contents.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "contents": contents,
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "generationConfig": {"maxOutputTokens": 1200}
    }

    response = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json=payload,
        timeout=60
    )

    # طباعة الخطأ للتصحيح
    if not response.ok:
        error_text = response.text[:500]
        print(f"Gemini API Error: {response.status_code} - {error_text}")
        raise RuntimeError(f"Gemini Error {response.status_code}: {error_text[:200]}")

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        print(f"Parse Error: {data}")
        raise RuntimeError(f"استجابة غير متوقعة")
