import { Analysis } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class LocalAnalyticsService {
  static async getAnalyses(): Promise<Analysis[]> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch analyses: ${response.status}`);
    }

    const data = await response.json();
    return data.results || data;
  }

  static async getAnalysis(id: string): Promise<Analysis> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/${id}/`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch analysis: ${response.status}`);
    }

    return await response.json();
  }

  static async createAnalysis(videoId: string, analysisType: string): Promise<Analysis> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        analysis_type: analysisType,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create analysis: ${response.status}`);
    }

    return await response.json();
  }

  static async deleteAnalysis(id: string): Promise<{ success: boolean; error?: string }> {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete analysis: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }
}