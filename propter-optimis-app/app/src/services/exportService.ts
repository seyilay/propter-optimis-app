import { supabase } from '@/lib/supabase';
import { Export } from '@/types';

export class ExportService {
  static async createExport(
    analysisId: string,
    exportType: 'video_clips' | 'pdf_report' | 'csv_data' | 'full_package'
  ): Promise<{ success: boolean; exportId?: string; error?: string }> {
    try {
      const { data, error } = await supabase
        .from('exports')
        .insert({
          analysis_id: analysisId,
          export_type: exportType,
          status: 'pending',
          created_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        return { success: false, error: error.message };
      }

      // Trigger export processing
      await this.processExport(data.id, exportType);

      return { success: true, exportId: data.id };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  static async getExports(analysisId?: string): Promise<Export[]> {
    let query = supabase
      .from('exports')
      .select(`
        *,
        analyses (
          id,
          video_id,
          analysis_intent,
          videos (
            title
          )
        )
      `)
      .order('created_at', { ascending: false });

    if (analysisId) {
      query = query.eq('analysis_id', analysisId);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(error.message);
    }

    return data || [];
  }

  static async getExport(id: string): Promise<Export | null> {
    const { data, error } = await supabase
      .from('exports')
      .select(`
        *,
        analyses (
          id,
          video_id,
          analysis_intent,
          openstarlab_results,
          ai_insights,
          videos (
            title,
            description
          )
        )
      `)
      .eq('id', id)
      .single();

    if (error) {
      throw new Error(error.message);
    }

    return data;
  }

  static async downloadExport(exportId: string): Promise<{ success: boolean; url?: string; error?: string }> {
    try {
      const exportRecord = await this.getExport(exportId);
      if (!exportRecord) {
        return { success: false, error: 'Export not found' };
      }

      if (exportRecord.status !== 'completed' || !exportRecord.file_path) {
        return { success: false, error: 'Export not ready for download' };
      }

      // Generate signed URL for download
      const { data } = await supabase.storage
        .from('propter-optimis-exports')
        .createSignedUrl(exportRecord.file_path, 3600); // 1 hour expiry

      if (!data?.signedUrl) {
        return { success: false, error: 'Could not generate download URL' };
      }

      return { success: true, url: data.signedUrl };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private static async processExport(
    exportId: string,
    exportType: 'video_clips' | 'pdf_report' | 'csv_data' | 'full_package'
  ): Promise<void> {
    try {
      // Update status to generating
      await supabase
        .from('exports')
        .update({ status: 'generating' })
        .eq('id', exportId);

      // Simulate export processing
      setTimeout(async () => {
        const mockFilePath = `exports/${exportId}/${this.getFileNameForType(exportType)}`;
        
        // In a real implementation, this would generate the actual export file
        // For demo purposes, we'll just update the record as completed
        await supabase
          .from('exports')
          .update({
            status: 'completed',
            file_path: mockFilePath
          })
          .eq('id', exportId);
      }, 3000); // 3 second simulation delay
    } catch (error) {
      console.error('Error processing export:', error);
      await supabase
        .from('exports')
        .update({ status: 'failed' })
        .eq('id', exportId);
    }
  }

  private static getFileNameForType(exportType: string): string {
    const timestamp = new Date().toISOString().split('T')[0];
    
    switch (exportType) {
      case 'video_clips':
        return `highlights-${timestamp}.mp4`;
      case 'pdf_report':
        return `analysis-report-${timestamp}.pdf`;
      case 'csv_data':
        return `match-data-${timestamp}.csv`;
      case 'full_package':
        return `complete-analysis-${timestamp}.zip`;
      default:
        return `export-${timestamp}.file`;
    }
  }

  static getExportTypeConfig(): Record<string, {
    label: string;
    description: string;
    estimatedSize: string;
    features: string[];
  }> {
    return {
      video_clips: {
        label: 'Video Highlights',
        description: 'Key moments and highlights extracted from the analysis',
        estimatedSize: '50-200 MB',
        features: ['Key events', 'Goal highlights', 'Tactical moments', 'Player actions']
      },
      pdf_report: {
        label: 'PDF Report',
        description: 'Comprehensive analysis report with insights and statistics',
        estimatedSize: '2-5 MB',
        features: ['Executive summary', 'Statistical analysis', 'Tactical insights', 'Recommendations']
      },
      csv_data: {
        label: 'Raw Data (CSV)',
        description: 'All statistical data and metrics in spreadsheet format',
        estimatedSize: '500 KB - 2 MB',
        features: ['Player statistics', 'Event data', 'Positional data', 'Time-series metrics']
      },
      full_package: {
        label: 'Complete Package',
        description: 'All export formats bundled together',
        estimatedSize: '100-500 MB',
        features: ['Video highlights', 'PDF report', 'Raw data', 'Analysis files']
      }
    };
  }
}