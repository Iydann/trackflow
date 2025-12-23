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
