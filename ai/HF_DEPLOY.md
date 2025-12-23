# Cara Deploy AI ke Hugging Face Spaces

## Opsi 1: Via Git (REKOMENDASI - Paling Mudah)

```powershell
# 1. Clone Space Anda
git clone https://huggingface.co/spaces/lydain/trackflow-ai
cd trackflow-ai

# 2. Copy semua file AI (dengan struktur folder)
# Dari folder ai/ di project TrackFlow
copy ..\Dockerfile.hf Dockerfile
copy ..\requirements.txt .
xcopy ..\api api\ /E /I /Y
xcopy ..\config config\ /E /I /Y
xcopy ..\src src\ /E /I /Y
copy ..\yolov8n.pt . /Y

# 3. Push ke Hugging Face
git add .
git commit -m "Deploy TrackFlow AI"
git push
```

Tunggu build selesai di https://huggingface.co/spaces/lydain/trackflow-ai

## Opsi 2: Via Web UI (Manual)

1. Buka https://huggingface.co/spaces/lydain/trackflow-ai
2. Tab "Files" → "Add file" → "Create a new file"
3. Buat file dengan path lengkap (otomatis buat folder):
   - `Dockerfile` - copy dari Dockerfile.hf
   - `requirements.txt` - copy isi requirements.txt
   - `api/__init__.py` - copy isi api/__init__.py
   - `api/main.py` - copy isi api/main.py
   - `config/__init__.py` - copy isi config/__init__.py
   - `config/settings.py` - copy isi config/settings.py
   - `src/__init__.py` - copy isi src/__init__.py
   - `src/detector.py` - copy isi src/detector.py
   - `src/tracker.py` - copy isi src/tracker.py
   - `src/utils.py` - copy isi src/utils.py
   - (opsional) `yolov8n.pt` - upload model

## Set Environment Variables

1. Klik "Settings" di Space
2. Scroll ke "Repository secrets" atau "Variables"
3. Tambahkan:
   - `ALLOWED_ORIGINS` = `*` (atau `https://backend-anda.onrender.com`)
   - `MODEL_NAME` = `yolov8n.pt`
   - `MAX_VIDEO_SIZE_MB` = `500`

## Test Endpoint

Setelah running, test:
```
https://lydain-trackflow-ai.hf.space/health
```

Endpoint AI Anda:
```
https://lydain-trackflow-ai.hf.space/process
```

Set di backend .env:
```
AI_API_URL=https://lydain-trackflow-ai.hf.space
```
