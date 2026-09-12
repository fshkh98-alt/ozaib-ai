import os
import requests
import json

# استخدام Gemini API الإصدار الجديد
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

SYSTEM_INSTRUCTION = """أنت CyberGuard AI، شات بوت تعليمي متخصص حصرياً في الأمن السيبراني.

قواعد صارمة:
1. أجب بالعربية الفصحى مع استخدام مصطلحات إنجليزية عند الضرورة بين قوسين
2. مجال تخصصك: الأمن السيبراني فقط (شبكات، ويب، تشفير، برمجيات خبيثة، SOC، SIEM، تحليل جنائي، استجابة حوادث، إدارة مخاطر، أمن تطبيقات)
3. إذا سأل المستخدم عن أي موضوع خارج الأمن السيبراني، رد بـ:
   '❌ عذراً، تخصصي يقتصر على الأمن السيبراني فقط. اسألني عن أمان الشبكات، التشفير، تحليل البرمجيات الخبيثة، SOC/SIEM، أمان الويب، أو أي موضوع أمني آخر.'
4. عند شرح موضوع تقني، استخدم تنسيق Markdown:
   - **عناوين واضحة**
   - قوائم نقطية
   - أكواد بلغة ```code```
   - جداول عند الحاجة
5. اجعل الإجابات تعليمية ومبسطة مع أمثلة عملية آمنة
6. لا تختلق معلومات - إذا لم تكن متأكداً، قل ذلك
7. لا تقدم طرقاً للاختراق الحقيقي - اقتصر على المفاهيم النظرية في بيئة تعليمية"""

def ask_gemini(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("لم يتم العثور على GEMINI_API_KEY في ملف .env")

    # بناء المحادثة
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

    # إرسال System Instruction بطريقة آمنة للـ API
    full_payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95
        }
    }

    # تحويل إلى JSON بترميز UTF-8
    json_payload = json.dumps(full_payload, ensure_ascii=False).encode('utf-8')

    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    url = f"{GEMINI_URL}?key={api_key}"
    
    response = requests.post(
        url,
        data=json_payload,
        headers=headers,
        timeout=60
    )

    if not response.ok:
        error_text = response.text[:300]
        print(f"Gemini API Error: {response.status_code} - {error_text}")
        raise RuntimeError(f"خطأ API {response.status_code}")

    # فك تشفير الاستجابة كـ UTF-8
    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError, TypeError) as e:
        print(f"Parse Error: {data}")
        raise RuntimeError("استجابة غير صالحة من Gemini")