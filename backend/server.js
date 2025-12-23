import express from 'express';
import cors from 'cors';
import multer from 'multer';
import axios from 'axios';
import FormData from 'form-data';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { supabase } from './supabase.js';
import { authMiddleware, optionalAuth } from './middleware.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const AI_API_URL = process.env.AI_API_URL || 'http://localhost:8000';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// CORS - allow all for now
app.use(cors({
  origin: true,
  credentials: true
}));
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

const upload = multer({ 
  storage,
  limits: { 
    fileSize: 2 * 1024 * 1024 * 1024 // 2GB max file size
  }
});

// Auth endpoints
app.post('/api/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Check if user exists
    const { data: existing } = await supabase
      .from('users')
      .select('id')
      .eq('email', email)
      .single();

    if (existing) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    const { data: user, error } = await supabase
      .from('users')
      .insert({
        email,
        password_hash: passwordHash,
        name: name || null
      })
      .select()
      .single();

    if (error) throw error;

    // Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Get user
    const { data: user, error } = await supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();

    if (error || !user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Verify password
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/me', authMiddleware, async (req, res) => {
  try {
    const { data: user, error } = await supabase
      .from('users')
      .select('id, email, name, created_at')
      .eq('id', req.user.userId)
      .single();

    if (error) throw error;

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/process', optionalAuth, upload.single('video'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No video file uploaded' });
    }

    const videoPath = req.file.path;
    const videoName = req.file.originalname;
    const userId = req.user?.userId || null;
    
    // Extract counting line coordinates from request body
    const { line_x1, line_y1, line_x2, line_y2 } = req.body;

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

    // Pass line coordinates to background processing
    const lineCoords = (line_x1 && line_y1 && line_x2 && line_y2) 
      ? { line_x1, line_y1, line_x2, line_y2 }
      : null;
    
    processVideoInBackground(processData.id, videoPath, videoName, lineCoords);

  } catch (error) {
    console.error('Error processing video:', error);
    res.status(500).json({ error: error.message });
  }
});

async function processVideoInBackground(processId, videoPath, videoName, lineCoords = null) {
  try {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(videoPath), {
      filename: videoName,
      contentType: 'video/mp4'
    });

    console.log(`[${processId}] Starting AI processing...`);
    console.log(`[${processId}] Video: ${videoName}`);
    console.log(`[${processId}] Path: ${videoPath}`);
    
    if (lineCoords) {
      console.log(`[${processId}] Counting line: (${lineCoords.line_x1},${lineCoords.line_y1}) -> (${lineCoords.line_x2},${lineCoords.line_y2})`);
    }
    
    console.log(`[${processId}] AI URL: ${AI_API_URL}/process`);

    // Build query params for counting line
    let queryParams = '';
    if (lineCoords) {
      queryParams = `?line_x1=${lineCoords.line_x1}&line_y1=${lineCoords.line_y1}&line_x2=${lineCoords.line_x2}&line_y2=${lineCoords.line_y2}`;
    }

    const aiResponse = await axios.post(`${AI_API_URL}/process${queryParams}`, formData, {
      headers: formData.getHeaders(),
      timeout: 0,
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    const results = aiResponse.data;
    console.log(`[${processId}] AI processing complete!`);
    console.log(`[${processId}] Statistics:`, results.statistics);
    
    const statistics = results.statistics || {};
    const vehicleCount = statistics.unique_vehicles || statistics.total_vehicles || 0;
    const crossedCount = statistics.vehicles_crossed_line;
    
    if (crossedCount !== null && crossedCount !== undefined) {
      console.log(`[${processId}] Vehicles crossed line: ${crossedCount}`);
    }

    // Update process
    const { error: processUpdateError } = await supabase
      .from('processes')
      .update({
        status: 'completed',
        total_vehicles: vehicleCount,
        results: statistics,
        completed_at: new Date().toISOString()
      })
      .eq('id', processId);

    if (processUpdateError) {
      console.error(`[${processId}] Error updating process:`, processUpdateError);
    }

    // Insert into history
    const { error: historyInsertError } = await supabase
      .from('history')
      .insert({
        process_id: processId,
        name: fileName,
        total_vehicles: vehicleCount,
        created_at: new Date().toISOString()
      });

    if (historyInsertError) {
      console.error(`[${processId}] Error inserting history:`, historyInsertError);
    } else {
      console.log(`[${processId}] Successfully inserted into history table`);
    }

    console.log(`Process ${processId} completed with ${vehicleCount} vehicles`);
    if (crossedCount !== null && crossedCount !== undefined) {
      console.log(`Process ${processId} - ${crossedCount} crossed the line`);
    }

    // Clean up: Delete local file
    fs.unlinkSync(videoPath);
    console.log(`[${processId}] Local file deleted`);

  } catch (error) {
    console.error(`[${processId}] Background processing error:`, error.message);
    console.error(`[${processId}] Full error:`, error);
    
    await supabase
      .from('processes')
      .update({
        status: 'failed',
        error_message: error.message
      })
      .eq('id', processId);
  }
}

app.get('/api/processes', optionalAuth, async (req, res) => {
  try {
    let query = supabase
      .from('processes')
      .select('*')
      .order('created_at', { ascending: false });

    // If authenticated, filter by user
    if (req.user?.userId) {
      query = query.eq('user_id', req.user.userId);
    }

    const { data, error } = await query;

    if (error) throw error;
    res.json(data || []);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/processes/:id', optionalAuth, async (req, res) => {
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

app.get('/api/history', optionalAuth, async (req, res) => {
  try {
    let query = supabase
      .from('history')
      .select('id, process_id, name, total_vehicles, created_at')
      .order('created_at', { ascending: false });

    // If authenticated, join with processes to filter by user
    if (req.user?.userId) {
      const { data: userProcesses } = await supabase
        .from('processes')
        .select('id')
        .eq('user_id', req.user.userId);
      
      if (userProcesses && userProcesses.length > 0) {
        const processIds = userProcesses.map(p => p.id);
        query = query.in('process_id', processIds);
      } else {
        // User has no processes, return empty array
        return res.json([]);
      }
    }

    const { data, error } = await query;

    if (error) throw error;
    
    console.log('History API - Retrieved records:', data?.length || 0);
    console.log('History API - User ID:', req.user?.userId || 'not authenticated');
    
    res.json(data || []);
  } catch (error) {
    console.error('History API error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/history/:id', authMiddleware, async (req, res) => {
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

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ status: 'ok', message: 'TrackFlow Backend API' });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
