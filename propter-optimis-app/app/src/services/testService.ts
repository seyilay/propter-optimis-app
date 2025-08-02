// Service to test Django backend connectivity
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class TestService {
  static async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      if (response.ok) {
        return { success: true, message: `Django server responding (${response.status})` };
      } else {
        return { success: false, message: `Django server error (${response.status})` };
      }
    } catch (error) {
      return { 
        success: false, 
        message: `Cannot connect to Django server: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  static async testUploadEndpoint(): Promise<{ success: boolean; message: string; details?: any }> {
    try {
      // Test with a simple POST to see if endpoint exists
      const response = await fetch(`${API_BASE_URL}/api/videos/upload/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ test: 'connectivity' }),
      });

      const responseText = await response.text();
      
      return {
        success: response.ok,
        message: response.ok 
          ? 'Upload endpoint accessible' 
          : `Upload endpoint error (${response.status})`,
        details: {
          status: response.status,
          statusText: response.statusText,
          response: responseText,
          headers: Object.fromEntries(response.headers.entries())
        }
      };
    } catch (error) {
      return {
        success: false,
        message: `Upload endpoint test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error: error instanceof Error ? error.message : 'Unknown error' }
      };
    }
  }

  static async debugUpload(file: File): Promise<{ success: boolean; message: string; details?: any }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', 'Debug Test Video');
      formData.append('analysis_intent', 'individual_player_performance');
      formData.append('description', 'Test upload for debugging');

      console.log('Sending FormData with keys:', Array.from(formData.keys()));

      const response = await fetch(`${API_BASE_URL}/api/videos/upload/`, {
        method: 'POST',
        body: formData,
      });

      const responseText = await response.text();
      
      return {
        success: response.ok,
        message: response.ok ? 'Debug upload successful' : `Debug upload failed (${response.status})`,
        details: {
          status: response.status,
          statusText: response.statusText,
          response: responseText,
          headers: Object.fromEntries(response.headers.entries()),
          requestInfo: {
            fileSize: file.size,
            fileName: file.name,
            fileType: file.type,
            formDataKeys: Array.from(formData.keys())
          }
        }
      };
    } catch (error) {
      return {
        success: false,
        message: `Debug upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error: error instanceof Error ? error.message : 'Unknown error' }
      };
    }
  }
}