# Ngrok Setup Guide (Pengganti Cloudflare Tunnel)

Ngrok lebih cocok untuk upload file besar (500MB+) dibanding Cloudflare Tunnel.

## 1) Download & Install Ngrok

1. Download dari https://ngrok.com/download
2. Extract ke folder (misal: `C:\Users\willy\ngrok.exe`)
3. Sign up gratis di https://dashboard.ngrok.com/signup
4. Copy Auth Token dari dashboard

## 2) Setup Auth Token (Sekali Saja)

```powershell
C:\Users\willy\ngrok.exe config add-authtoken YOUR_AUTH_TOKEN
```

## 3) Start Ngrok Tunnel

```powershell
cd C:\Users\willy\Documents\AASchool\Semester5\ippl\trackflow-main
python -m uvicorn ai.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Pastikan AI service sudah jalan di port 8000, lalu:

```powershell
C:\Users\willy\ngrok.exe http 8000
```

Output akan menampilkan URL forwarding seperti:

```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

**IMPORTANT:** Copy URL `https://abc123.ngrok.io` ini untuk Railway.

## 4) Update Railway Backend

1. Buka Railway → trackflow-backend → Variables
2. Update `AI_API_URL` = `https://abc123.ngrok.io` (URL dari ngrok)
3. Redeploy backend

## 5) Keep Ngrok Running

- Console mode (lihat logs):

```powershell
C:\Users\willy\ngrok.exe http 8000
```

- Background minimized:

```powershell
Start-Process -FilePath "C:\Users\willy\ngrok.exe" -ArgumentList "http 8000" -WindowStyle Minimized
```

## 6) Test Upload

Sekarang coba upload file 500MB dari frontend.

## Catatan Penting

- **Free tier ngrok:** URL berubah setiap restart (seperti Cloudflare quick tunnel)
- **Paid ngrok ($8/month):** Bisa pakai custom domain yang stabil
- **Connection limit:** Free tier ada connection limit tapi lebih tinggi dari Cloudflare
- **File size:** Ngrok bisa handle file >500MB tanpa masalah

## Troubleshooting

### Ngrok timeout

Jika upload timeout di tengah jalan, coba:

1. Kompres video dulu (480p)
2. Upgrade ngrok ke paid plan
3. Atau pakai LocalTunnel (opsi 2 di LOCALTUNNEL_SETUP.md)

### "ERR_NGROK_108"

Auth token belum disetup. Jalankan:

```powershell
C:\Users\willy\ngrok.exe config add-authtoken YOUR_TOKEN
```

## Daily Routine

1. Start AI service:

```powershell
cd C:\Users\willy\Documents\AASchool\Semester5\ippl\trackflow-main
python -m uvicorn ai.api.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Start ngrok:

```powershell
C:\Users\willy\ngrok.exe http 8000
```

3. Copy ngrok URL, update Railway `AI_API_URL`, redeploy

4. Test upload!
