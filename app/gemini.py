```python
import os
import requests


# Gemini Interactions API
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

MODEL = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = (
    "أنت CyberGuard AI، شات بوت تعليمي متخصص في الأمن السيبراني. "
    "أجب بالعربية مع شرح واضح ومفيد. "
    "عند شرح المفاهيم التقنية، استخدم أمثلة عملية وآمنة. "
    "لا تقدم تعليمات تؤدي إلى اختراق أنظمة أو سرقة بيانات أو تجاوز صلاحيات "
    "بشكل غير قانوني."
)


def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "لم يتم العثور على GEMINI_API_KEY في ملف .env"
        )

    # تحويل سجل المحادثة إلى صيغة Interactions API
    inputs = []

    for item in history:
        role = item.get("role", "user")
        content = item.get("content", "")

        if not content:
            continue

        # Gemini يستخدم user / model
        if role not in ("user", "model"):
            role = "user"

        inputs.append(
            {
                "role": role,
                "content": content,
            }
        )

    # إضافة الرسالة الحالية
    inputs.append(
        {
            "role": "user",
            "content": message,
        }
    )

    payload = {
        "model": MODEL,
        "input": inputs,
        "system_instruction": SYSTEM_INSTRUCTION,
        "generation_config": {
            "max_output_tokens": 1200
        },
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"تعذر الاتصال بخدمة Gemini: {exc}"
        ) from exc

    if not response.ok:
        raise RuntimeError(
            f"Gemini Error {response.status_code}: "
            f"{response.text[:1000]}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"استجابة Gemini ليست JSON صالحة: {response.text[:1000]}"
        ) from exc

    # Interactions API يعيد النص في output_text
    output_text = data.get("output_text")

    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    # محاولة استخراج النص من output إذا لم يوجد output_text
    output = data.get("output")

    if isinstance(output, list):
        text_parts = []

        for item in output:
            if not isinstance(item, dict):
                continue

            content = item.get("content")

            if isinstance(content, str):
                text_parts.append(content)

            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        text = part.get("text")
                        if isinstance(text, str):
                            text_parts.append(text)

        if text_parts:
            return "\n".join(text_parts).strip()

    raise RuntimeError(
        f"استجابة Gemini غير متوقعة: {data}"
    )
```
