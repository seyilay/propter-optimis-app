import { supabase } from '@/lib/supabase';
import { Analysis, AnalysisIntent } from '@/types';

const IS_LOCAL_MODE = import.meta.env.VITE_AUTH_MODE === 'local';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class AnalyticsService {
  static async createAnalysis(
    videoId: string,
    analysisIntent: AnalysisIntent
  ): Promise<{ success: boolean; analysisId?: string; error?: string }> {
    try {
      const { data, error } = await supabase
        .from('analyses')
        .insert({
          video_id: videoId,
          analysis_intent: analysisIntent,
          status: 'pending',
          created_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        return { success: false, error: error.message };
      }

      // Trigger OpenStar Lab processing
      await this.triggerProcessing(data.id);

      return { success: true, analysisId: data.id };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  static async getAnalyses(): Promise<Analysis[]> {
    if (IS_LOCAL_MODE) {
      const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch analyses: ${response.status}`);
      }
      const data = await response.json();
      return data.results || data;
    } else {
      const { data, error } = await supabase
        .from('analyses')
        .select(`
          *,
          videos (
            id,
            title,
            file_path
          )
        `)
        .order('created_at', { ascending: false });

      if (error) {
        throw new Error(error.message);
      }

      return data || [];
    }
  }

  static async getAnalysis(id: string): Promise<Analysis | null> {
    if (IS_LOCAL_MODE) {
      const response = await fetch(`${API_BASE_URL}/api/analytics/analyses/${id}/`);
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Failed to fetch analysis: ${response.status}`);
      }
      return await response.json();
    } else {
      const { data, error } = await supabase
        .from('analyses')
        .select(`
          *,
          videos (
            id,
            title,
            file_path,
            duration
          )
        `)
        .eq('id', id)
        .single();

      if (error) {
        throw new Error(error.message);
      }

      return data;
    }
  }

  static async updateAnalysis(
    id: string,
    updates: Partial<Analysis>
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await supabase
        .from('analyses')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', id);

      if (error) {
        return { success: false, error: error.message };
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  static async addManualAnnotation(
    analysisId: string,
    annotation: {
      timestamp: number;
      type: string;
      description: string;
      coordinates?: { x: number; y: number };
    }
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const analysis = await this.getAnalysis(analysisId);
      if (!analysis) {
        return { success: false, error: 'Analysis not found' };
      }

      const currentAnnotations = analysis.manual_annotations || [];
      const updatedAnnotations = [
        ...currentAnnotations,
        {
          ...annotation,
          id: Math.random().toString(36).substring(7),
          created_at: new Date().toISOString()
        }
      ];

      return await this.updateAnalysis(analysisId, {
        manual_annotations: updatedAnnotations
      });
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private static async triggerProcessing(analysisId: string): Promise<void> {
    try {
      // Update status to processing
      await this.updateAnalysis(analysisId, { status: 'processing' });

      // In a real implementation, this would trigger the OpenStar Lab processing
      // For now, we'll simulate processing with a timeout
      setTimeout(async () => {
        const mockResults = {
          events: [
            {
              timestamp: 120,
              type: 'goal',
              player: 'Player #10',
              confidence: 0.95
            },
            {
              timestamp: 340,
              type: 'tackle',
              player: 'Player #5',
              confidence: 0.87
            }
          ],
          statistics: {
            possession: { home: 65, away: 35 },
            shots: { home: 12, away: 8 },
            passes: { home: 450, away: 320 }
          },
          heatmap: {
            // Mock heatmap data
            data: Array.from({ length: 100 }, () => Math.random())
          }
        };

        const mockInsights = `
        ## Analysis Summary
        
        **Match Overview:**
        - Dominant possession by home team (65%)
        - High pressing intensity in first half
        - Key tactical switch at 60' mark
        
        **Key Findings:**
        1. **Attacking Patterns:** Home team favored right-wing attacks (78% of forward passes)
        2. **Defensive Structure:** Compact defensive line maintained throughout
        3. **Set Pieces:** 3 goals from corner situations, indicating set-piece weakness
        
        **Recommendations:**
        - Improve set-piece defending
        - Counter-press more effectively after losing possession
        - Exploit left-wing space in future matches
        `;

        await this.updateAnalysis(analysisId, {
          status: 'completed',
          openstarlab_results: mockResults,
          ai_insights: mockInsights,
          processing_time: 15 // 15 minutes
        });
      }, 5000); // 5 second simulation delay
    } catch (error) {
      console.error('Error triggering processing:', error);
      await this.updateAnalysis(analysisId, {
        status: 'failed'
      });
    }
  }

  static getAnalysisIntentConfig(): Record<AnalysisIntent, {
    label: string;
    description: string;
    estimatedTime: string;
    features: string[];
  }> {
    return {
      individual_player_performance: {
        label: 'Individual Player Performance',
        description: 'Detailed analysis of individual player statistics, heat maps, and performance metrics',
        estimatedTime: '12-15 minutes',
        features: ['Heat maps', 'Touch analysis', 'Movement patterns', 'Performance metrics']
      },
      tactical_phase_analysis: {
        label: 'Tactical Phase Analysis',
        description: 'Breaking down game phases, formations, and tactical transitions',
        estimatedTime: '10-12 minutes',
        features: ['Formation analysis', 'Phase transitions', 'Tactical patterns', 'Team shape']
      },
      opposition_scouting: {
        label: 'Opposition Scouting',
        description: 'Comprehensive analysis for opponent preparation and weakness identification',
        estimatedTime: '15-18 minutes',
        features: ['Weakness analysis', 'Pattern recognition', 'Key player identification', 'Tactical tendencies']
      },
      set_piece_analysis: {
        label: 'Set Piece Analysis',
        description: 'Focused analysis on corners, free kicks, and set piece situations',
        estimatedTime: '8-10 minutes',
        features: ['Set piece detection', 'Success rates', 'Pattern analysis', 'Defensive positioning']
      },
      full_match_review: {
        label: 'Full Match Review',
        description: 'Complete match analysis with all available insights and metrics',
        estimatedTime: '20-25 minutes',
        features: ['Complete match breakdown', 'All metrics', 'Advanced insights', 'Comprehensive report']
      }
    };
  }
}