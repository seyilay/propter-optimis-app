import { supabase } from '@/lib/supabase';
import { Video, AnalysisIntent, UploadProgress } from '@/types';

const IS_LOCAL_MODE = import.meta.env.VITE_AUTH_MODE === 'local';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class VideoService {
  static async uploadVideo(
    file: File,
    metadata: {
      title: string;
      description?: string;
      analysisIntent: AnalysisIntent;
    },
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ success: boolean; videoId?: string; error?: string }> {
    if (IS_LOCAL_MODE) {
      return this.uploadVideoLocal(file, metadata, onProgress);
    } else {
      return this.uploadVideoSupabase(file, metadata, onProgress);
    }
  }

  private static async uploadVideoLocal(
    file: File,
    metadata: {
      title: string;
      description?: string;
      analysisIntent: AnalysisIntent;
    },
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ success: boolean; videoId?: string; error?: string }> {
    try {
      onProgress?.({ progress: 0, status: 'uploading', message: 'Starting upload...' });

      // Create FormData for Django upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', metadata.title);
      formData.append('description', metadata.description || '');
      formData.append('analysis_intent', metadata.analysisIntent);

      // Add progress tracking
      onProgress?.({ progress: 30, status: 'uploading', message: 'Uploading to server...' });

      const response = await fetch(`${API_BASE_URL}/api/videos/upload/`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary for FormData
      });

      onProgress?.({ progress: 80, status: 'uploading', message: 'Processing upload...' });

      if (!response.ok) {
        const responseText = await response.text();
        console.error('Upload failed. Response:', responseText);
        
        // Try to parse as JSON, fallback to text
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = JSON.parse(responseText);
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch {
          errorMessage = responseText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      onProgress?.({ progress: 100, status: 'completed', message: 'Upload completed successfully!' });
      return { success: true, videoId: data.id };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      onProgress?.({ progress: 0, status: 'error', message: errorMessage });
      return { success: false, error: errorMessage };
    }
  }

  private static async uploadVideoSupabase(
    file: File,
    metadata: {
      title: string;
      description?: string;
      analysisIntent: AnalysisIntent;
    },
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ success: boolean; videoId?: string; error?: string }> {
    try {
      onProgress?.({ progress: 0, status: 'uploading', message: 'Starting upload...' });

      // Generate unique filename
      const timestamp = Date.now();
      const fileExt = file.name.split('.').pop();
      const fileName = `${timestamp}-${Math.random().toString(36).substring(7)}.${fileExt}`;
      const filePath = `videos/${fileName}`;

      // Upload to Supabase Storage
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('propter-optimis-videos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (uploadError) {
        onProgress?.({ progress: 0, status: 'error', message: uploadError.message });
        return { success: false, error: uploadError.message };
      }

      onProgress?.({ progress: 50, status: 'uploading', message: 'Creating video record...' });

      // Create video record in database
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      const { data: videoData, error: dbError } = await supabase
        .from('videos')
        .insert({
          title: metadata.title,
          description: metadata.description,
          file_path: uploadData.path,
          file_size: file.size,
          uploaded_by: user.id,
          status: 'processing',
          analysis_intent: metadata.analysisIntent,
          upload_date: new Date().toISOString()
        })
        .select()
        .single();

      if (dbError) {
        onProgress?.({ progress: 50, status: 'error', message: dbError.message });
        return { success: false, error: dbError.message };
      }

      onProgress?.({ progress: 100, status: 'completed', message: 'Upload completed successfully!' });
      return { success: true, videoId: videoData.id };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      onProgress?.({ progress: 0, status: 'error', message: errorMessage });
      return { success: false, error: errorMessage };
    }
  }

  static async getVideos(): Promise<Video[]> {
    if (IS_LOCAL_MODE) {
      const response = await fetch(`${API_BASE_URL}/api/videos/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch videos: ${response.status}`);
      }
      const data = await response.json();
      return data.results || data;
    } else {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .order('upload_date', { ascending: false });

      if (error) {
        throw new Error(error.message);
      }

      return data || [];
    }
  }

  static async getVideo(id: string): Promise<Video | null> {
    if (IS_LOCAL_MODE) {
      const response = await fetch(`${API_BASE_URL}/api/videos/${id}/`);
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Failed to fetch video: ${response.status}`);
      }
      return await response.json();
    } else {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        throw new Error(error.message);
      }

      return data;
    }
  }

  static async deleteVideo(id: string): Promise<{ success: boolean; error?: string }> {
    try {
      if (IS_LOCAL_MODE) {
        const response = await fetch(`${API_BASE_URL}/api/videos/${id}/`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error(`Failed to delete video: ${response.status}`);
        }

        return { success: true };
      } else {
        // Get video details to delete file from storage
        const video = await this.getVideo(id);
        if (!video) {
          return { success: false, error: 'Video not found' };
        }

        // Delete from storage
        const { error: storageError } = await supabase.storage
          .from('propter-optimis-videos')
          .remove([video.file_path]);

        if (storageError) {
          console.warn('Error deleting file from storage:', storageError);
        }

        // Delete from database
        const { error: dbError } = await supabase
          .from('videos')
          .delete()
          .eq('id', id);

        if (dbError) {
          return { success: false, error: dbError.message };
        }

        return { success: true };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  static async getVideoUrl(filePath: string): Promise<string> {
    if (IS_LOCAL_MODE) {
      // For local Django development, return direct file URL
      return `${API_BASE_URL}/media/${filePath}`;
    } else {
      const { data } = await supabase.storage
        .from('propter-optimis-videos')
        .createSignedUrl(filePath, 3600); // 1 hour expiry

      return data?.signedUrl || '';
    }
  }
}