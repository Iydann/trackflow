import express from 'express';
import cors from 'cors';
import multer from 'multer';
import axios from 'axios';
import FormData from 'form-data';
import { supabase } from './supabase.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const AI_API_URL = process.env.AI_API_URL || 'http://localhost:8000';

app.use(cors());
app.use(express.json());

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ storage });

app.post('/api/process', upload.single('video'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No video file uploaded' });
    }

    const videoPath = req.file.path;
    const videoName = req.file.originalname;
    const userId = req.body.userId || 'anonymous';

    const processRecord = {
      name: videoName,
      status: 'processing',
      user_id: userId,
      created_at: new Date().toISOString()
    };

    const { data: processData, error: insertError } = await supabase
      .from('processes')
      .insert(processRecord)
      .select()
      .single();

    if (insertError) {
      throw insertError;
    }

    res.json({
      processId: processData.id,
      status: 'processing',
      message: 'Video uploaded, processing started'
    });

    processVideoInBackground(processData.id, videoPath, videoName);

  } catch (error) {
    console.error('Error processing video:', error);
    res.status(500).json({ error: error.message });
  }
});

async function processVideoInBackground(processId, videoPath, videoName) {
  try {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(videoPath), {
      filename: videoName,
      contentType: 'video/mp4'
    });

    console.log(`Processing video for process ${processId}...`);

    const aiResponse = await axios.post(`${AI_API_URL}/process`, formData, {
      headers: formData.getHeaders(),
      timeout: 300000,
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    const results = aiResponse.data;
    console.log('AI processing complete:', results.statistics);
    
    const statistics = results.statistics || {};
    const vehicleCount = statistics.unique_vehicles || statistics.total_vehicles || 0;

    await supabase
      .from('processes')
      .update({
        status: 'completed',
        total_vehicles: vehicleCount,
        results: statistics,
        completed_at: new Date().toISOString()
      })
      .eq('id', processId);

    await supabase
      .from('history')
      .insert({
        process_id: processId,
        name: videoName,
        total_vehicles: vehicleCount,
        created_at: new Date().toISOString()
      });

    console.log(`Process ${processId} completed with ${vehicleCount} vehicles`);

    fs.unlinkSync(videoPath);

  } catch (error) {
    console.error('Background processing error:', error.message);
    
    await supabase
      .from('processes')
      .update({
        status: 'failed',
        error_message: error.message
      })
      .eq('id', processId);
  }
}

app.get('/api/processes', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('processes')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    res.json(data || []);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/processes/:id', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('processes')
      .select('*')
      .eq('id', req.params.id)
      .single();

    if (error) throw error;
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/history', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('history')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    res.json(data || []);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/history/:id', async (req, res) => {
  try {
    const { error } = await supabase
      .from('history')
      .delete()
      .eq('id', req.params.id);

    if (error) throw error;
    res.json({ message: 'Deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
