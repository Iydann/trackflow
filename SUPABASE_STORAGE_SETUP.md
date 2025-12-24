# Supabase Storage Setup for TrackFlow

## Why Supabase Storage?

To bypass Railway's 10-minute HTTP request timeout, videos are uploaded directly to Supabase Storage from the browser. This allows:

- **Unlimited upload time** - No Railway timeout during upload
- **Support for large videos** - Up to 2GB+
- **Better user experience** - Real progress tracking
- **Auto-cleanup** - Videos deleted after processing (no storage cost)

## Setup Instructions

### 1. Create Storage Bucket in Supabase

1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **New bucket**
4. **Bucket name**: `videos`
5. **Public bucket**: ✅ **Enable** (required for AI to download)
6. Click **Create bucket**

### 2. Set Bucket Policies (Important!)

After creating the bucket, set these policies:

**Policy 1: Allow authenticated uploads**

- Policy name: `Allow authenticated uploads`
- Allowed operation: `INSERT`
- Policy definition:

```sql
(auth.role() = 'authenticated')
```

**Policy 2: Allow public read access**

- Policy name: `Allow public read`
- Allowed operation: `SELECT`
- Policy definition:

```sql
true
```

**Policy 3: Allow service role delete**

- Policy name: `Allow service role delete`
- Allowed operation: `DELETE`
- Policy definition:

```sql
(auth.role() = 'service_role')
```

### 3. Update Environment Variables

**Frontend (.env in Vercel)**

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://trackflow-production.up.railway.app
```

**Backend (Railway environment variables - already set)**

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
AI_API_URL=https://your-tunnel-url.trycloudflare.com
```

### 4. Update Database Schema

Run this SQL in Supabase SQL Editor to add video_path column:

```sql
ALTER TABLE processes
ADD COLUMN IF NOT EXISTS video_path TEXT;
```

### 5. Deploy

**Frontend:**

```bash
cd frontend
npm install
# Push to GitHub - Vercel auto-deploys
```

**Backend:**

```bash
# Push to GitHub - Railway auto-deploys
```

## How It Works

### Old Flow (Limited by Railway timeout):

```
Browser → [Upload 10min max] → Railway → AI
          ^^^ Timeout for large videos
```

### New Flow (No timeout):

```
Browser → [Upload unlimited] → Supabase Storage
                                    ↓
Railway ← [Download fast] ← [Public URL]
   ↓
  AI (laptop via tunnel)
   ↓
Railway → [Auto-delete from Supabase]
```

## Benefits

✅ **No Railway timeout** - Upload doesn't go through Railway
✅ **Support large videos** - 1-2 hour videos, 500MB-2GB files
✅ **Real progress tracking** - Supabase SDK has built-in progress
✅ **Auto-cleanup** - Videos deleted after processing (no storage cost)
✅ **Faster** - Supabase CDN optimized for file delivery

## Testing

1. Upload a large video (>100MB)
2. Watch progress bar show real upload percentage
3. After processing completes, video is automatically deleted from Supabase
4. Check Supabase Storage dashboard - `videos` bucket should be empty after processing

## Troubleshooting

**"Missing Supabase environment variables"**

- Make sure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set in Vercel

**"Upload failed: new row violates row-level security policy"**

- Check that `videos` bucket is public
- Verify upload policy allows authenticated users

**"AI cannot download video"**

- Ensure bucket is **public** (not private)
- Check public read policy is enabled

**"Video not deleted after processing"**

- Check backend logs for deletion errors
- Verify service role key has delete permissions
