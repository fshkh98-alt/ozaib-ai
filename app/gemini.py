import os
import requests

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.6-flash:generateContent"
)

SYSTEM_INSTRUCTION = """
أنت CyberGuard AI، شات بوت تعليمي متخصص حصراً في الأمن السيبراني.

قواعدك:
1) أجب باللغة العربية الواضحة، ويمكن استخدام المصطلحات الإنجليزية بين قوسين عند الحاجة.
2) مجال الإجابة المسموح: الأمن السيبراني فقط، مثل أمن الشبكات، أمن الويب، التشفير،
   أمن الأنظمة، البرمجيات الخبيثة، الاستجابة للحوادث، التحليل الجنائي الرقمي،
   SOC وSIEM، إدارة المخاطر، التوعية الأمنية، وأمن التطبيقات.
3) إذا كان السؤال خارج الأمن السيبراني، ارفضه باختصار وقل إن نطاق المشروع هو الأمن السيبراني.
4) الهدف تعليمي. عند شرح موضوع تقني، اشرح المفهوم ثم مثالاً آمناً أو مختبراً.
5) لا تختلق مراجع أو حقائق. إذا لم تكن متأكداً فاذكر ذلك بوضوح.
6) لا تقدم تعليمات عملية لسرقة الحسابات، تجاوز المصادقة، الاحتيال، سرقة البيانات،
   أو اختراق أنظمة حقيقية دون تصريح. يمكن شرح المفاهيم والهجمات في بيئة مختبرية آمنة.
7) حافظ على سياق المحادثة السابقة عندما يكون السؤال الجديد مرتبطاً بها.
8) اجعل الإجابات منظمة باستخدام عناوين ونقاط وأمثلة قصيرة.
"""

def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("لم يتم العثور على GEMINI_API_KEY في ملف .env")

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
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 1200
        }
    }

    response = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json=payload,
        timeout=60
    )

    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Gemini API error: {detail}")

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"استجابة Gemini غير متوقعة: {data}")
