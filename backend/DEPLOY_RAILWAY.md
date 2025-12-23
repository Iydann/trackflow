# Deploy Backend TrackFlow ke Railway

## Persiapan

Backend sudah siap untuk production dengan:
- ✅ `package.json` dengan script `start`
- ✅ Environment variables via `.env`
- ✅ Support Supabase
- ✅ CORS enabled
- ✅ File upload dengan Multer

## Langkah Deploy ke Railway

### 1. Buka Railway
https://railway.app

### 2. Sign Up / Login
- Login dengan GitHub (recommended)

### 3. Create New Project
- Klik "New Project"
- Pilih "Deploy from GitHub repo"
- Pilih repository `trackflow` (atau folder `backend` jika bisa)
- Atau klik "Empty Project" lalu "Deploy from GitHub"

### 4. Configure Build
Railway akan auto-detect Node.js. Pastikan settings:

**Root Directory:** `backend` (jika deploy full repo)
**Build Command:** `npm install`
**Start Command:** `npm start`

Atau tambahkan file `railway.json` di folder backend:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm install"
  },
  "deploy": {
    "startCommand": "npm start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 5. Environment Variables
Klik tab "Variables" dan tambahkan:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_anon_key>
AI_API_URL=https://iydain-trackflow-ai.hf.space
PORT=3000
JWT_SECRET=<generate_random_string>
NODE_ENV=production
```

**Cara generate JWT_SECRET:**
```powershell
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 6. Deploy
Klik "Deploy" dan tunggu build (2-3 menit)

### 7. Get Public URL
Setelah deploy sukses:
- Railway akan generate URL: `https://<project-name>.up.railway.app`
- Copy URL ini untuk frontend

## Update Frontend

Di Vercel project, update Environment Variable:
```
VITE_API_URL=https://<backend-url>.up.railway.app
```
Lalu redeploy frontend.

## Alternatif: Deploy ke Render

### 1. Buka Render
https://render.com

### 2. Create Web Service
- New → Web Service
- Connect GitHub repo
- Root Directory: `backend`
- Runtime: Node
- Build Command: `npm install`
- Start Command: `npm start`

### 3. Environment Variables
Tambahkan sama seperti Railway di atas.

### 4. Deploy
Free tier: `https://<service-name>.onrender.com`

**Note:** Render free tier akan sleep setelah 15 menit tidak ada traffic, butuh ~30 detik untuk wake up.

## Testing Backend

Setelah deploy, test endpoint:
```
https://<backend-url>/api/health
```

## Troubleshooting

**Error: Cannot find module**
- Pastikan `type: "module"` ada di package.json
- Import statement harus pakai `.js` extension

**Upload folder issue**
- Railway/Render ephemeral filesystem
- Pertimbangkan pakai Supabase Storage untuk video uploads

**CORS errors**
- Pastikan frontend URL di-whitelist di CORS settings (atau tetap `*` untuk testing)
