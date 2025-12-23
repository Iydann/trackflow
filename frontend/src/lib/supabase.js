import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Upload video to Supabase Storage with progress tracking
export async function uploadVideoToStorage(file, onProgress) {
  const timestamp = Date.now()
  const fileName = `${timestamp}_${file.name}`
  const filePath = `uploads/${fileName}`
  
  try {
    // For files larger than 50MB, use resumable upload
    const chunkSize = 6 * 1024 * 1024 // 6MB chunks
    
    if (file.size > 50 * 1024 * 1024) {
      // Large file - use chunked upload
      const totalChunks = Math.ceil(file.size / chunkSize)
      let uploadedBytes = 0
      
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize
        const end = Math.min(start + chunkSize, file.size)
        const chunk = file.slice(start, end)
        
        const { error } = await supabase.storage
          .from('videos')
          .upload(filePath, chunk, {
            cacheControl: '3600',
            upsert: i > 0, // Append to existing file for subsequent chunks
          })
        
        if (error) throw error
        
        uploadedBytes += chunk.size
        if (onProgress) {
          const percent = Math.round((uploadedBytes / file.size) * 100)
          onProgress(percent)
        }
      }
    } else {
      // Small file - direct upload
      const { data, error } = await supabase.storage
        .from('videos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
          onUploadProgress: (progress) => {
            if (onProgress && progress.total) {
              const percent = Math.round((progress.loaded / progress.total) * 100)
              onProgress(percent)
            }
          }
        })
      
      if (error) throw error
    }
    
    // Get public URL
    const { data: { publicUrl } } = supabase.storage
      .from('videos')
      .getPublicUrl(filePath)
    
    return {
      path: filePath,
      publicUrl,
      fileName
    }
  } catch (error) {
    console.error('Upload error:', error)
    throw error
  }
}

// Delete video from Supabase Storage
export async function deleteVideoFromStorage(filePath) {
  try {
    const { error } = await supabase.storage
      .from('videos')
      .remove([filePath])
    
    if (error) throw error
    return true
  } catch (error) {
    console.error('Delete error:', error)
    throw error
  }
}
