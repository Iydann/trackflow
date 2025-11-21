-- TrackFlow Database Schema for Supabase

-- Processes table: tracks video processing jobs
CREATE TABLE IF NOT EXISTS processes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'processing',
  user_id TEXT,
  total_vehicles INTEGER DEFAULT 0,
  results JSONB,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- History table: stores completed analysis records
CREATE TABLE IF NOT EXISTS history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  process_id UUID REFERENCES processes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  total_vehicles INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_processes_status ON processes(status);
CREATE INDEX IF NOT EXISTS idx_processes_created_at ON processes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_process_id ON history(process_id);
