# CyberGuard AI — مساعد الأمن السيبراني

مشروع مقرر **الذكاء الاصطناعي التطبيقي**: شات بوت تعليمي متخصص في الأمن السيبراني.

## فكرة المشروع
واجهة ويب بـ HTML/CSS/JavaScript + خادم FastAPI بلغة Python + Gemini API.
يحتفظ النظام بسجل المحادثة في SQLite ويرسل السياق السابق مع السؤال الجديد إلى Gemini،
مع تقييد المساعد على نطاق الأمن السيبراني.

## المتطلبات
- Python 3.11 أو أحدث
- مفتاح Gemini API

## التشغيل

### 1) إنشاء بيئة افتراضية
```bash
python -m venv .venv
```

### 2) التفعيل في Windows
```bash
.venv\Scripts\activate
```

### 3) التثبيت
```bash
pip install -r requirements.txt
```

### 4) إعداد المفتاح
انسخ `.env.example` إلى `.env` ثم ضع مفتاح Gemini:
```env
GEMINI_API_KEY=YOUR_KEY
```

### 5) التشغيل
```bash
uvicorn app.main:app --reload
```

ثم افتح:
http://127.0.0.1:8000

## تقسيم العرض على 3 طلاب
1. الطالب الأول: HTML/CSS/JavaScript وتصميم الواجهة.
2. الطالب الثاني: FastAPI وSQLite وإدارة History.
3. الطالب الثالث: Gemini API، الـ prompt، واختبارات نطاق الإجابة.

## عنوان مختصر مقترح
**CyberGuard AI — مساعد الأمن السيبراني**

## أمثلة لاختبار نطاق الإجابة
- سؤال داخل التخصص: "ما هو SIEM؟" → يجيب.
- سؤال خارج التخصص: "ما عاصمة فرنسا؟" → يرفض لأنه خارج نطاق المشروع.
- سؤال متابع: "طيب وما الفرق بينه وبين SOC؟" → يستخدم سجل المحادثة السابق لفهم المقصود.

## ملاحظة أمنية
لا تضع مفتاح Gemini داخل JavaScript أو GitHub. يجب أن يبقى في `.env` على الخادم.

## النشر على Railway

1. ارفع المشروع إلى GitHub.
2. أنشئ مشروعًا جديدًا في Railway واربط مستودع GitHub.
3. Railway سيكتشف مشروع Python تلقائيًا.
4. في Railway → Variables أضف:
```env
GEMINI_API_KEY=ضع_مفتاح_Gemini_هنا
```
5. اجعل Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
6. بعد نجاح النشر افتح رابط Railway للمشروع.

> لا ترفع ملف `.env` إلى GitHub. استخدم Variables داخل Railway.

