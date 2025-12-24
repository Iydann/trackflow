# Cloudflare Tunnel Restart Guide (Windows)

This guide helps you quickly restart the AI service and Cloudflare Tunnel whenever your PC or tunnel has been stopped.

## Prerequisites
- AI service (FastAPI) runs on localhost port 8000
- Cloudflared installed at `C:\Users\willy\cloudflared.exe`
- Railway backend uses `AI_API_URL` to reach your tunnel URL

## 1) Start the AI Service (port 8000)
Use one of the following:

- From project root (recommended):
```powershell
cd C:\Users\willy\Documents\AASchool\Semester5\ippl\trackflow-main
python -m uvicorn ai.api.main:app --host 0.0.0.0 --port 8000 --reload
```

- Or from `ai` folder using main script:
```powershell
cd C:\Users\willy\Documents\AASchool\Semester5\ippl\trackflow-main\ai
python main.py
```

Verify local health:
```powershell
curl.exe -s http://localhost:8000/health
```
You should see `{"status":"healthy"}`.

## 2) Quick Tunnel (temporary URL)
A quick tunnel creates a new random `*.trycloudflare.com` URL on each start.

- Stop any existing tunnel:
```powershell
taskkill /F /IM cloudflared.exe
```

- Start a new tunnel to localhost:8000 (console):
```powershell
C:\Users\willy\cloudflared.exe tunnel --url http://localhost:8000
```
Cloudflared prints the new public URL, e.g.:
```
https://infections-classroom-por-spiritual.trycloudflare.com
```

- Start minimized (detached background):
```powershell
Start-Process -FilePath "C:\Users\willy\cloudflared.exe" -ArgumentList "tunnel --url http://localhost:8000" -WindowStyle Minimized
```

- Verify tunnel health:
```powershell
curl.exe -s https://<your-tunnel>.trycloudflare.com/health
```
Expect a JSON health response.

- Update Railway backend to use the new URL:
  - Open Railway → Service → Variables
  - Set `AI_API_URL` = `https://<your-tunnel>.trycloudflare.com`
  - Redeploy or Restart service

Notes:
- Quick tunnel URL changes every restart. If the old URL is used, uploads fail with `ENOTFOUND`.

## 3) Named Tunnel (stable URL via your domain)
For a permanent URL, use a Named Tunnel and route a DNS record in Cloudflare.

1. Login (opens browser):
```powershell
C:\Users\willy\cloudflared.exe login
```
2. Create a named tunnel:
```powershell
C:\Users\willy\cloudflared.exe tunnel create trackflow
```
3. Route DNS (replace with your domain):
```powershell
C:\Users\willy\cloudflared.exe tunnel route dns trackflow ai.yourdomain.com
```
4. Run the named tunnel:
```powershell
C:\Users\willy\cloudflared.exe tunnel run trackflow --url http://localhost:8000
```
5. Set Railway `AI_API_URL` to `https://ai.yourdomain.com` (stable) and redeploy.

## 4) Useful Checks
- See if port 8000 is occupied:
```powershell
netstat -ano | findstr :8000
```
- Kill by PID (replace <PID>):
```powershell
taskkill /F /PID <PID>
```
- Confirm backend health:
```powershell
curl.exe -s https://trackflow-production.up.railway.app/api/health
```

## 5) Common Issues
- `ENOTFOUND <old-url>.trycloudflare.com` → Tunnel URL changed. Start a new tunnel and update `AI_API_URL`.
- `524/504 timeout` via tunnel → Fixed by our async endpoints. Ensure AI service is running, and backend polls `/task/{id}`.
- Upload fails mid-transfer → Railway free tier bandwidth/connection limits. We increased timeouts and keep-alive; still consider compressing to 480p or upgrading Railway plan for reliability.

## 6) Quick Routine (daily)
1. Start AI service
2. Start tunnel (quick or named)
3. Verify `.../health`
4. Update Railway `AI_API_URL` if using quick tunnel and redeploy
5. Test upload from the frontend

This file lives at `trackflow-main/TUNNEL_RESTART.md`. Keep it handy for restarts.