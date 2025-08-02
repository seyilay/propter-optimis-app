import { Video, AnalysisIntent, UploadProgress } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class LocalVideoService {
  static async uploadVideo(
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

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', metadata.title);
      formData.append('description', metadata.description || '');
      formData.append('analysis_intent', metadata.analysisIntent);

      // Get JWT token from localStorage
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/api/videos/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Upload failed' }));
        throw new Error(errorData.error || `HTTP ${response.status}`);
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

  static async getVideos(): Promise<Video[]> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/videos/`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch videos: ${response.status}`);
    }

    const data = await response.json();
    return data.results || data;
  }

  static async getVideo(id: string): Promise<Video | null> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/videos/${id}/`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`Failed to fetch video: ${response.status}`);
    }

    return await response.json();
  }

  static async deleteVideo(id: string): Promise<{ success: boolean; error?: string }> {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/api/videos/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete video: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  static async getVideoUrl(filePath: string): Promise<string> {
    // For local Django development, return direct file URL
    return `${API_BASE_URL}/media/${filePath}`;
  }
}