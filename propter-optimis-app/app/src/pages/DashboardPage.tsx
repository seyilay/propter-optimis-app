import { useState, useEffect } from 'react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { AnalysisChart, ProcessingTimeChart, IntelligenceInsightsPanel } from '@/components/dashboard/AnalysisChart';
import { Button } from '@/components/ui/button';
import { VideoService } from '@/services/videoService';
import { AnalyticsService } from '@/services/analyticsService';
import { DashboardStats } from '@/types';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Link } from 'react-router-dom';
import { 
  Video, 
  BarChart3, 
  Clock, 
  TrendingUp, 
  Upload,
  Play,
  Target
} from 'lucide-react';

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [videos, analyses] = await Promise.all([
          VideoService.getVideos(),
          AnalyticsService.getAnalyses()
        ]);

        const completedAnalyses = analyses.filter(a => a.status === 'completed');
        const pendingAnalyses = analyses.filter(a => a.status === 'pending' || a.status === 'processing');
        
        const avgProcessingTime = completedAnalyses.length > 0
          ? completedAnalyses.reduce((sum, a) => sum + (a.processing_time || 0), 0) / completedAnalyses.length
          : 0;

        // Generate recent activity from videos and analyses
        const recentActivity = [
          ...videos.slice(0, 3).map(video => ({
            id: `video-${video.id}`,
            type: 'upload' as const,
            description: `Uploaded video: ${video.title}`,
            timestamp: video.upload_date
          })),
          ...completedAnalyses.slice(0, 2).map(analysis => ({
            id: `analysis-${analysis.id}`,
            type: 'analysis' as const,
            description: `Completed analysis for video`,
            timestamp: analysis.updated_at || analysis.created_at
          }))
        ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 5);

        setStats({
          totalVideos: videos.length,
          totalAnalyses: analyses.length,
          avgProcessingTime,
          completedAnalyses: completedAnalyses.length,
          pendingAnalyses: pendingAnalyses.length,
          recentActivity
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground">
            AI-powered sports analytics at your fingertips
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Link to="/upload">
            <Button className="bg-purple-600 hover:bg-purple-700">
              <Upload className="mr-2 h-4 w-4" />
              Upload Video
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Videos"
          value={stats?.totalVideos || 0}
          description="Videos uploaded for analysis"
          icon={<Video className="h-4 w-4" />}
          trend={{ value: 12, isPositive: true }}
        />
        <StatsCard
          title="Analyses Completed"
          value={stats?.completedAnalyses || 0}
          description="Successful AI analyses"
          icon={<BarChart3 className="h-4 w-4" />}
          trend={{ value: 8, isPositive: true }}
        />
        <StatsCard
          title="Avg Processing Time"
          value={stats?.avgProcessingTime ? `${Math.round(stats.avgProcessingTime)} min` : '0 min'}
          description="Time saved vs manual analysis"
          icon={<Clock className="h-4 w-4" />}
          trend={{ value: 22, isPositive: false }}
        />
        <StatsCard
          title="Pending Analyses"
          value={stats?.pendingAnalyses || 0}
          description="Currently being processed"
          icon={<TrendingUp className="h-4 w-4" />}
        />
      </div>

      {/* Main Content */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <AnalysisChart />
        <IntelligenceInsightsPanel />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <RecentActivity activities={stats?.recentActivity || []} />
        
        {/* Quick Actions */}
        <div className="col-span-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* AI Processing Status */}
            <div className="rounded-lg border bg-gradient-to-r from-purple-50 to-indigo-50 p-6">
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Target className="h-4 w-4 text-white" />
                </div>
                <h3 className="font-semibold text-purple-900">AI Analysis Performance</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-purple-700">Time Reduction:</span>
                  <span className="font-medium text-purple-900">87% faster</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-purple-700">From 4+ hours to:</span>
                  <span className="font-medium text-purple-900">~15 minutes</span>
                </div>
                <div className="w-full bg-purple-200 rounded-full h-2 mt-3">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '87%' }}></div>
                </div>
              </div>
            </div>

            {/* Quick Start */}
            <div className="rounded-lg border bg-gradient-to-r from-green-50 to-emerald-50 p-6">
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                  <Play className="h-4 w-4 text-white" />
                </div>
                <h3 className="font-semibold text-green-900">Quick Start</h3>
              </div>
              <p className="text-sm text-green-700 mb-4">
                New to Propter-Optimis? Upload your first video and experience AI-powered analysis.
              </p>
              <Link to="/upload">
                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}