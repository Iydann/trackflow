# Deploy Frontend TrackFlow ke Vercel

## Langkah Deploy

### 1. Buka Vercel

https://vercel.com

### 2. Import Project

- Klik "Add New" → "Project"
- Pilih "Import Git Repository" atau "Import from..."
- Connect GitHub (jika belum)
- Pilih repository atau upload folder `frontend`

### 3. Configure Project

```
Framework Preset: Vite
Root Directory: frontend (jika upload full repo)
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 4. Environment Variables

Tambahkan di Vercel project settings → Environment Variables:

**Production:**

```
VITE_API_URL=https://<backend-url>
```

**Untuk testing lokal backend:**

```
VITE_API_URL=http://localhost:3000
```

### 5. Deploy

Klik "Deploy" dan tunggu build selesai (2-3 menit)

## Setelah Deploy

URL frontend Anda akan jadi:

```
https://<project-name>.vercel.app
```

## Update VITE_API_URL Nanti

Setelah backend di-deploy (Railway/Render):

1. Buka Vercel project → Settings → Environment Variables
2. Edit `VITE_API_URL` ke URL backend
3. Redeploy (Deployments → klik "..." → Redeploy)

## Alternatif: Deploy via Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy dari folder frontend
cd frontend
vercel

# Set environment variable
vercel env add VITE_API_URL
```

## Notes

- Frontend Vite sudah configured di `vite.config.js`
- API endpoint diambil dari `import.meta.env.VITE_API_URL` di `src/lib/api.js`
- Vercel auto-detect Vite dan build dengan benar
- Setiap push ke branch akan auto-deploy (jika connect GitHub)
