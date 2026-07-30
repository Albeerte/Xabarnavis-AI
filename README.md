# xabarnavis.png Xabarnavis AI

> Raqamli kontentning haqiqiyligini tekshiruvchi sun’iy intellekt platformasi.

**Xabarnavis AI** — rasm, video, audio va matnlarni tahlil qilib, ularning sun’iy intellekt yordamida yaratilganligi, deepfake qilinganligi, tahrirlanganligi yoki manipulyatsiya qilinganligini aniqlashga yordam beruvchi multimodal AI platforma.

Tizim tahlil natijalarini yagona ishonchlilik bahosiga birlashtiradi hamda foydalanuvchiga dalillar, metadata, vizual izohlar va tekshiruv tafsilotlari asosida professional hisobot taqdim etadi.

---

## 📌 Loyiha haqida

Internetda sun’iy intellekt yordamida yaratilgan soxta rasmlar, deepfake videolar, klonlangan ovozlar va manipulyativ matnlar soni tez ortib bormoqda.

Bunday kontent:

* yolg‘on axborot tarqalishiga;
* moliyaviy firibgarlikka;
* shaxsiy obro‘ga zarar yetishiga;
* soxta hujjatlar yaratilishiga;
* media manipulyatsiyasiga;
* ijtimoiy tarmoqlarda ishonchsizlik paydo bo‘lishiga sabab bo‘lishi mumkin.

**Xabarnavis AI** ushbu muammoni turli AI modellarini bitta platformada birlashtirish orqali hal qiladi.

---

## 🎯 Asosiy maqsad

Xabarnavis AI loyihasining maqsadi — foydalanuvchilar, jurnalistlar, davlat tashkilotlari, banklar, sug‘urta kompaniyalari va bizneslar uchun raqamli kontentni tez, tushunarli va dalillarga asoslangan tarzda tekshirish imkoniyatini yaratish.

---

## ✨ Asosiy imkoniyatlar

### 🖼️ Rasm tahlili

* AI yordamida yaratilgan rasmlarni aniqlash
* Photoshop yoki boshqa dasturlarda tahrirlangan hududlarni topish
* Rasm metadata ma’lumotlarini tekshirish
* EXIF ma’lumotlarini tahlil qilish
* Nusxalangan va ko‘chirilgan hududlarni aniqlash
* Error Level Analysis
* Noise pattern tahlili
* AI-detektor modellarini birlashtirish
* Shubhali hududlarni heatmap orqali ko‘rsatish

### 🎥 Video tahlili

* Deepfake videolarni aniqlash
* Kadrlar bo‘yicha yuz tahlili
* Yuz almashtirish belgilarini topish
* Lab-sync nomuvofiqligini aniqlash
* Video metadata ma’lumotlarini tekshirish
* Kadrlar orasidagi vizual o‘zgarishlarni tahlil qilish
* Shubhali kadrlarni ajratib ko‘rsatish

### 🎙️ Audio tahlili

* Klonlangan ovozlarni aniqlash
* AI-generated audio tahlili
* Spektrogramma asosida tekshiruv
* Ovozdagi sun’iy artefaktlarni aniqlash
* Audio metadata ma’lumotlarini tekshirish
* Kesilgan yoki birlashtirilgan segmentlarni topish
* Speaker consistency tahlili

### 📝 Matn tahlili

* AI yordamida yozilgan matnlarni aniqlash
* Manipulyativ va clickbait jumlalarni topish
* Matndagi ehtimoliy yolg‘on da’volarni ajratish
* Faktlarni tekshirishga tayyorlash
* Matn uslubi va semantik izchillikni tahlil qilish
* Shubhali iboralarni belgilash

### 📄 Professional hisobot

* PDF formatidagi hisobot
* DOCX formatidagi hisobot
* Har bir tekshiruv uchun noyob identifikator
* QR-kod orqali hisobotni ochish
* Tahlil sanasi va vaqti
* Tekshiruv qurilmasi haqida ma’lumot
* Ishlatilgan AI modellari
* Har bir model natijasi
* Umumiy ishonchlilik bahosi
* Vizual dalillar va heatmap
* Yakuniy xulosa
* Hisobotni tekshirish sahifasi

---

## 🧠 Tizim qanday ishlaydi?

Xabarnavis AI bir nechta mustaqil detektorlarning natijalarini birlashtiradi.

```text
Foydalanuvchi fayl yuklaydi
            │
            ▼
Fayl turi va xavfsizligi tekshiriladi
            │
            ▼
Metadata va texnik xususiyatlar olinadi
            │
            ▼
Mos AI modellar ishga tushiriladi
            │
            ▼
Har bir model alohida natija beradi
            │
            ▼
Fusion Engine natijalarni birlashtiradi
            │
            ▼
Ishonchlilik darajasi hisoblanadi
            │
            ▼
Dalillar va tushuntirishlar yaratiladi
            │
            ▼
PDF, DOCX va QR-kodli hisobot tayyorlanadi
```

---

## 🏗️ Arxitektura

```text
Xabarnavis/
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── db.py
│   ├── schemas.py
│   │
│   └── services/
│       ├── analyzer.py
│       ├── media_analyzer.py
│       ├── fusion.py
│       ├── image_reasoning.py
│       ├── metadata.py
│       ├── report.py
│       ├── docx_report.py
│       ├── image_models/
│       ├── video_models/
│       ├── audio_models/
│       ├── text_models/
│       └── adapters/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
│
├── models/
│   ├── image/
│   ├── video/
│   ├── audio/
│   └── text/
│
├── reports/
├── uploads/
├── tests/
├── scripts/
├── manage.py
├── requirements.txt
├── requirements-training.txt
├── requirements-datasets.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔬 Tahlil modullari

### 1. Metadata Analyzer

Faylning texnik ma’lumotlarini o‘rganadi:

* fayl nomi;
* hajmi;
* format;
* MIME turi;
* yaratilgan vaqt;
* o‘zgartirilgan vaqt;
* kamera yoki qurilma modeli;
* dasturiy ta’minot nomi;
* GPS ma’lumotlari;
* kodek va siqish parametrlari.

### 2. Media Analyzer

Rasm, video va audio fayllarini AI modellar uchun tayyorlaydi:

* formatni tekshirish;
* faylni normalizatsiya qilish;
* videodan kadr olish;
* audioni segmentlarga ajratish;
* yuzlarni aniqlash;
* kerakli preprocessing jarayonlarini bajarish.

### 3. Model Adapters

Turli AI modellarni yagona interfeys orqali ishga tushiradi.

Har bir adapter quyidagi formatda natija qaytaradi:

```json
{
  "model_name": "model-name",
  "label": "ai_generated",
  "confidence": 0.94,
  "processing_time": 1.82,
  "evidence": [],
  "warnings": []
}
```

### 4. Fusion Engine

Bir nechta model natijalarini umumlashtiradi.

```text
Yakuniy natija =
    Model ishonchliligi
    × Model vazni
    × Fayl sifati
    × Tahlil dalillari
```

Fusion Engine oddiy o‘rtacha qiymat bilan cheklanmaydi. U model kalibratsiyasi, fayl turi, modelning shu turdagi ma’lumotdagi samaradorligi va mavjud dalillarni hisobga oladi.

### 5. Explainability Engine

Tizim faqat natija bermaydi, balki natijaning sabablarini ham ko‘rsatadi:

* heatmap;
* shubhali kadrlar;
* audio spektrogramma;
* metadata nomuvofiqligi;
* model bo‘yicha ishonchlilik;
* aniqlangan sun’iy artefaktlar.

### 6. Report Generator

Tahlil tugagach, professional hisobot yaratadi:

* umumiy xulosa;
* ishonchlilik darajasi;
* dalillar;
* texnik ma’lumotlar;
* model natijalari;
* QR-kod;
* hisobot identifikatori;
* PDF va DOCX fayllari.

---

## 📊 Natija formatlari

Xabarnavis AI natijani quyidagi klasslardan biri sifatida ko‘rsatishi mumkin:

| Holat          | Tavsif                                                    |
| -------------- | --------------------------------------------------------- |
| `REAL`         | Kontent haqiqiy bo‘lish ehtimoli yuqori                   |
| `AI_GENERATED` | Kontent AI yordamida yaratilgan bo‘lishi mumkin           |
| `MANIPULATED`  | Kontent tahrirlangan yoki o‘zgartirilgan                  |
| `DEEPFAKE`     | Yuz yoki ovoz deepfake texnologiyasi bilan o‘zgartirilgan |
| `SUSPICIOUS`   | Shubhali belgilar mavjud                                  |
| `INCONCLUSIVE` | Aniq xulosa chiqarish uchun dalillar yetarli emas         |

> Tizim natijasi mutlaq hukm emas. Natija ehtimollik, mavjud modellar va texnik dalillar asosida shakllantiriladi.

---

## 🧰 Texnologiyalar

### Backend

* Python
* FastAPI yoki Django
* Pydantic
* SQLAlchemy yoki Django ORM
* Celery
* Redis
* PostgreSQL
* OpenCV
* FFmpeg
* Pillow
* NumPy
* Librosa

### Artificial Intelligence

* PyTorch
* Transformers
* timm
* ONNX Runtime
* Hugging Face
* OpenCLIP
* Computer Vision modellar
* Audio classification modellar
* NLP modellar

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui
* Recharts

### Infrastructure

* Docker
* Docker Compose
* Nginx
* PostgreSQL
* Redis
* CUDA
* GitHub Actions

---

## ⚙️ O‘rnatish

### Talablar

Loyihani ishga tushirish uchun quyidagilar tavsiya etiladi:

* Python 3.10 yoki undan yuqori
* Node.js 20 yoki undan yuqori
* PostgreSQL
* Redis
* FFmpeg
* Git
* CUDA qo‘llab-quvvatlovchi GPU — ixtiyoriy, lekin tavsiya etiladi

---

## 1. Repozitoriyni yuklab olish

```bash
git clone https://github.com/USERNAME/xabarnavis-ai.git
cd xabarnavis-ai
```

`USERNAME` o‘rniga GitHub foydalanuvchi yoki tashkilot nomini yozing.

---

## 2. Python virtual muhit yaratish

### Linux yoki macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Python paketlarini o‘rnatish

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Agar trening modullari ham kerak bo‘lsa:

```bash
pip install -r requirements-training.txt
```

Dataset vositalari uchun:

```bash
pip install -r requirements-datasets.txt
```

---

## 4. FFmpeg o‘rnatish

### Ubuntu

```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows

FFmpeg dasturini o‘rnating va uning `bin` papkasini tizimning `PATH` o‘zgaruvchisiga qo‘shing.

Tekshirish:

```bash
ffmpeg -version
```

---

## 5. Environment sozlamalari

`.env.example` faylidan yangi `.env` fayli yarating:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Misol:

```env
APP_NAME=Xabarnavis AI
APP_ENV=development
DEBUG=true

SECRET_KEY=change-this-secret-key

DATABASE_URL=postgresql://postgres:password@localhost:5432/xabarnavis
REDIS_URL=redis://localhost:6379/0

UPLOAD_DIR=uploads
REPORT_DIR=reports
MODEL_DIR=models

MAX_UPLOAD_SIZE_MB=500

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

JWT_SECRET_KEY=change-this-jwt-secret
JWT_ALGORITHM=HS256

HF_TOKEN=
OPENAI_API_KEY=
```

Maxfiy kalitlarni GitHub’ga yuklamang.

---

## 6. Ma’lumotlar bazasini tayyorlash

Agar loyiha Django migratsiyalaridan foydalansa:

```bash
python manage.py makemigrations
python manage.py migrate
```

Administrator yaratish:

```bash
python manage.py createsuperuser
```

Agar loyiha Alembic’dan foydalansa:

```bash
alembic upgrade head
```

---

## 7. Backend’ni ishga tushirish

FastAPI konfiguratsiyasi uchun:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Django konfiguratsiyasi uchun:

```bash
python manage.py runserver 0.0.0.0:8000
```

Backend manzili:

```text
http://localhost:8000
```

API dokumentatsiyasi:

```text
http://localhost:8000/docs
```

---

## 8. Frontend’ni ishga tushirish

```bash
cd frontend
npm install
npm run dev
```

Yoki `pnpm` orqali:

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend manzili:

```text
http://localhost:3000
```

---

## 9. Redis va Celery

Redis’ni ishga tushiring:

```bash
redis-server
```

Celery worker:

```bash
celery -A app.worker.celery worker --loglevel=info
```

Og‘ir video va audio tahlillari background worker orqali bajarilishi tavsiya etiladi.

---

## 🐳 Docker orqali ishga tushirish

```bash
docker compose up --build
```

Background rejimida:

```bash
docker compose up -d --build
```

Loglarni ko‘rish:

```bash
docker compose logs -f
```

Servislarni to‘xtatish:

```bash
docker compose down
```

---

## 🔌 API misoli

### Fayl yuborish

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample.jpg" \
  -F "media_type=image"
```

### Kutiladigan javob

```json
{
  "analysis_id": "analysis_8f27c31a",
  "media_type": "image",
  "status": "completed",
  "verdict": "AI_GENERATED",
  "confidence": 0.93,
  "risk_level": "high",
  "processing_time": 4.21,
  "models": [
    {
      "name": "image-detector-1",
      "label": "AI_GENERATED",
      "confidence": 0.95
    },
    {
      "name": "image-detector-2",
      "label": "AI_GENERATED",
      "confidence": 0.90
    }
  ],
  "evidence": [
    "Sun’iy tekstura belgilari aniqlandi",
    "Noise pattern tabiiy kamera tasviriga mos kelmadi"
  ],
  "report": {
    "pdf": "/reports/analysis_8f27c31a.pdf",
    "docx": "/reports/analysis_8f27c31a.docx",
    "verification_url": "/verify/analysis_8f27c31a"
  }
}
```

---

## 🔐 Xavfsizlik

Xabarnavis AI quyidagi xavfsizlik choralarini qo‘llashi kerak:

* fayl formatlarini tekshirish;
* zararli fayllarni bloklash;
* MIME turini tekshirish;
* fayl hajmini cheklash;
* vaqtinchalik fayllarni avtomatik o‘chirish;
* JWT autentifikatsiya;
* rolga asoslangan ruxsatlar;
* API rate limiting;
* foydalanuvchi harakatlarini loglash;
* shaxsiy fayllarni shifrlash;
* hisobotlarni noyob havola orqali himoyalash;
* maxfiy kalitlarni environment orqali boshqarish.

---

## 👥 Foydalanuvchi rollari

| Rol          | Imkoniyatlar                              |
| ------------ | ----------------------------------------- |
| Guest        | Cheklangan demo tahlili                   |
| User         | Fayl tahlili va hisobot olish             |
| Expert       | Kengaytirilgan texnik natijalarni ko‘rish |
| Organization | Jamoa, API va umumiy hisobotlar           |
| Admin        | Foydalanuvchi, model va tizim boshqaruvi  |

---

## 🖥️ Admin panel

Admin panel orqali quyidagilar boshqariladi:

* foydalanuvchilar;
* tashkilotlar;
* obunalar;
* tahlillar;
* hisobotlar;
* AI modellar;
* model versiyalari;
* model vaznlari;
* noto‘g‘ri natijalar;
* foydalanuvchi fikrlari;
* qurilmalar;
* kirishlar tarixi;
* bildirishnomalar;
* API tokenlar;
* tizim loglari.

---

## 📱 Foydalanuvchi interfeysi

Platforma interfeysi quyidagi imkoniyatlarga ega:

* to‘liq o‘zbek tilidagi interfeys;
* kunduzgi va tungi rejim;
* mobil qurilmalarga mos dizayn;
* drag-and-drop fayl yuklash;
* real vaqt tahlil holati;
* tahlil tarixini ko‘rish;
* hisobotlarni yuklab olish;
* QR-kod orqali tekshirish;
* bildirishnomalar;
* qurilmalar boshqaruvi;
* oxirgi kirishlar tarixi.

---

## 🧪 Testlar

Barcha testlarni ishga tushirish:

```bash
pytest
```

Coverage bilan:

```bash
pytest --cov=app --cov-report=term-missing
```

Faqat API testlari:

```bash
pytest tests/api/
```

Faqat model testlari:

```bash
pytest tests/models/
```

Frontend testlari:

```bash
cd frontend
npm run test
```

---

## 📈 Modelni baholash

Faqat `accuracy` ko‘rsatkichi model sifatini to‘liq ifodalamaydi.

Quyidagi metrikalardan foydalanish tavsiya etiladi:

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC
* PR-AUC
* False Positive Rate
* False Negative Rate
* Equal Error Rate
* Confusion Matrix
* Calibration Error

Model turli generatorlar, kameralar, platformalar va fayl siqish darajalarida alohida test qilinishi kerak.

---

## ⚠️ Muhim cheklovlar

* Hech bir AI detektor 100% aniqlikni kafolatlamaydi.
* Fayl kuchli siqilgan bo‘lsa, aniqlik kamayishi mumkin.
* Yangi AI generatorlar eski modellar tomonidan aniqlanmasligi mumkin.
* Metadata o‘chirilgan yoki o‘zgartirilgan bo‘lishi mumkin.
* Natijalar mustaqil ekspertiza o‘rnini to‘liq bosa olmaydi.
* Huquqiy qarorlar faqat bitta AI natijasiga asoslanmasligi kerak.
* Model natijalari dataset va real sharoitdagi kontent o‘rtasida farq qilishi mumkin.

Xabarnavis AI yakuniy hukm emas, balki raqamli ekspertiza va qaror qabul qilishga yordam beruvchi vositadir.

---

## 🗺️ Roadmap

### 1-bosqich — MVP

* [x] Rasm tahlili
* [x] Audio tahlili
* [x] Asosiy backend API
* [x] Tahlil natijasini ko‘rsatish
* [x] PDF hisobot
* [ ] DOCX hisobot
* [ ] QR-kodli tekshiruv sahifasi
* [ ] Foydalanuvchi kabineti
* [ ] Tahlil tarixi

### 2-bosqich — Multimodal platforma

* [ ] Video deepfake tahlili
* [ ] Matn tahlili
* [ ] Fusion Engine
* [ ] Explainable AI heatmap
* [ ] Admin panel
* [ ] Qurilmalar boshqaruvi
* [ ] Bildirishnomalar
* [ ] API tokenlar

### 3-bosqich — Tashkilotlar uchun yechim

* [ ] SaaS tariflari
* [ ] Organization workspace
* [ ] Team management
* [ ] Batch analysis
* [ ] API integratsiyasi
* [ ] Webhook tizimi
* [ ] Audit log
* [ ] White-label hisobotlar

### 4-bosqich — Global platforma

* [ ] Ingliz va rus tillari
* [ ] Brauzer extension
* [ ] Telegram bot
* [ ] Mobil ilova
* [ ] Real-time video tekshiruv
* [ ] Blockchain yoki raqamli imzo orqali hisobot tasdiqlash
* [ ] Xalqaro media va fact-checking tashkilotlari bilan integratsiya

---

## 💼 Qo‘llanish sohalari

Xabarnavis AI quyidagi sohalarda ishlatilishi mumkin:

* jurnalistika;
* fact-checking;
* davlat tashkilotlari;
* bank va moliya;
* sug‘urta;
* huquqni muhofaza qilish;
* sud ekspertizasi;
* ta’lim;
* elektron tijorat;
* ijtimoiy tarmoqlar;
* HR va identifikatsiya;
* marketing;
* kiberxavfsizlik;
* kontent moderatsiyasi.

---

## 🤝 Hissa qo‘shish

Loyihaga hissa qo‘shish uchun:

1. Repozitoriyni fork qiling.
2. Yangi branch yarating.

```bash
git checkout -b feature/new-feature
```

3. O‘zgarishlarni commit qiling.

```bash
git commit -m "feat: yangi imkoniyat qo‘shildi"
```

4. Branch’ni GitHub’ga yuboring.

```bash
git push origin feature/new-feature
```

5. Pull Request yarating.

---

## 📝 Commit standartlari

```text
feat: yangi imkoniyat
fix: xatoni tuzatish
docs: dokumentatsiyani yangilash
refactor: kod strukturasini yaxshilash
test: test qo‘shish
chore: texnik o‘zgarish
perf: ishlash tezligini yaxshilash
security: xavfsizlik yangilanishi
```

Misol:

```bash
git commit -m "feat: QR-kodli PDF hisobot qo‘shildi"
```

---

## 🐛 Muammo haqida xabar berish

Muammo yuborishda quyidagilarni ko‘rsating:

* operatsion tizim;
* Python versiyasi;
* GPU modeli;
* CUDA versiyasi;
* xato matni;
* xato yuz bergan bosqich;
* qayta takrorlash qadamlari;
* zarur bo‘lsa, skrinshot.

Shaxsiy, maxfiy yoki noqonuniy media fayllarni ommaviy GitHub issue ichiga joylamang.

---

## 📜 Litsenziya

Loyiha litsenziyasi `LICENSE` faylida ko‘rsatiladi.

Tijoriy foydalanish, model vaznlari, datasetlar va uchinchi tomon kutubxonalari uchun alohida litsenziya shartlari mavjud bo‘lishi mumkin.

---

## 👨‍💻 Muallif

**Solijonov Abduxoliq**

Xabarnavis AI asoschisi va loyiha rahbari.

* GitHub: `https://github.com/`Albeerte
* Email: `solijonovabduxoliq137@gmail.com`
* Telegram: `@`albert_std

---

## 📬 Bog‘lanish

Hamkorlik, investitsiya, texnik integratsiya yoki loyiha bo‘yicha takliflar uchun:

```text
Email: solijonovabduxoliq137@gmail.com
Telegram: @albert_std
Website: https://xabarnavis.uz
```

---

## ⭐ Loyihani qo‘llab-quvvatlash

Xabarnavis AI loyihasi sizga foydali bo‘lsa:

* GitHub’da yulduzcha bosing;
* loyihani fork qiling;
* xatolar haqida xabar bering;
* yangi dataset yoki model taklif qiling;
* loyiha haqida boshqalarga ulashing.

---

<div align="center">

### Xabarnavis AI

**Raqamli axborotga ishonchni qayta tiklaymiz.**

Made in Uzbekistan 🇺🇿

</div>
