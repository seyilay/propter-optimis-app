import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

// Import our intelligence components
import { TacticalAnalysisDisplay } from '@/components/dashboard/TacticalAnalysisDisplay';
import { PlayerPerformancePanel } from '@/components/dashboard/PlayerPerformancePanel';
import { EventTimeline } from '@/components/dashboard/EventTimeline';
import { PredictionInsights } from '@/components/dashboard/PredictionInsights';
import { IntelligenceExport } from '@/components/dashboard/IntelligenceExport';

import { 
  Analysis, 
  OpenStarLabResults, 
  AIInsights,
  Recommendation
} from '@/types';
import { AnalyticsService } from '@/services/analyticsService';
import { 
  Brain,
  Download,
  Share2,
  BarChart3,
  Users,
  Target,
  Crystal,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  TrendingUp,
  Activity
} from 'lucide-react';

export function AnalysisResultsPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!analysisId) return;

      try {
        setLoading(true);
        const result = await AnalyticsService.getAnalysis(analysisId);
        setAnalysis(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Error Loading Analysis
          </h3>
          <p className="text-gray-500 mb-4">{error || 'Analysis not found'}</p>
          <Link to="/dashboard">
            <Button variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (analysis.status !== 'completed') {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <Clock className="h-12 w-12 text-blue-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Analysis In Progress
          </h3>
          <p className="text-gray-500 mb-4">
            Your analysis is being processed. Please check back in a few minutes.
          </p>
          <Link to="/dashboard">
            <Button variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const openstarResults = analysis.openstarlab_results as OpenStarLabResults;
  const aiInsights = analysis.ai_insights as AIInsights;

  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analysis Results</h1>
            <p className="text-muted-foreground">
              AI-powered football intelligence insights
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Link to={`#export`} onClick={(e) => {
            e.preventDefault();
            document.getElementById('export-section')?.scrollIntoView({ behavior: 'smooth' });
          }}>
            <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </Link>
        </div>
      </div>

      {/* Analysis Overview */}
      <AnalysisOverview 
        analysis={analysis} 
        openstarResults={openstarResults}
        aiInsights={aiInsights}
      />

      {/* Intelligence Dashboard */}
      <IntelligenceDashboard 
        openstarResults={openstarResults}
        aiInsights={aiInsights}
      />

      {/* Export Section */}
      <div id="export-section">
        <IntelligenceExport 
          analysis={analysis}
          openstarResults={openstarResults}
          aiInsights={aiInsights}
        />
      </div>
    </div>
  );
}

function AnalysisOverview({ 
  analysis, 
  openstarResults, 
  aiInsights 
}: { 
  analysis: Analysis;
  openstarResults: OpenStarLabResults | null;
  aiInsights: AIInsights | null;
}) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-blue-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const confidenceScore = openstarResults?.confidence_scores?.overall_intelligence_confidence || 0;
  const processingTime = analysis.processing_time || 0;
  const eventsDetected = openstarResults?.events?.length || 0;
  const insightsGenerated = aiInsights?.performance_summary?.tactical_patterns_identified || 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Analysis Status</CardTitle>
          {getStatusIcon(analysis.status)}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold capitalize">{analysis.status}</div>
          <p className="text-xs text-muted-foreground">
            {analysis.status === 'completed' ? 'Analysis complete' : 'In progress'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {Math.floor(processingTime / 60)}m {processingTime % 60}s
          </div>
          <p className="text-xs text-muted-foreground">
            87% faster than manual analysis
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Events Detected</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{eventsDetected}</div>
          <p className="text-xs text-muted-foreground">
            AI-detected match events
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Confidence Score</CardTitle>
          <Brain className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {Math.round(confidenceScore * 100)}%
          </div>
          <Progress value={confidenceScore * 100} className="mt-2 h-1" />
        </CardContent>
      </Card>
    </div>
  );
}

function IntelligenceDashboard({ 
  openstarResults, 
  aiInsights 
}: { 
  openstarResults: OpenStarLabResults | null;
  aiInsights: AIInsights | null;
}) {
  if (!openstarResults) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Intelligence Data Available
          </h3>
          <p className="text-gray-500">
            Intelligence results will appear here once processing is complete.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Recommendations */}
      {aiInsights?.key_recommendations && aiInsights.key_recommendations.length > 0 && (
        <KeyRecommendations recommendations={aiInsights.key_recommendations} />
      )}

      {/* Intelligence Tabs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-6 w-6" />
            Football Intelligence Dashboard
          </CardTitle>
          <CardDescription>
            Comprehensive AI-powered analysis using OpenStarLab intelligence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="events" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="events" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Events
              </TabsTrigger>
              <TabsTrigger value="tactical" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Tactical
              </TabsTrigger>
              <TabsTrigger value="players" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Players
              </TabsTrigger>
              <TabsTrigger value="predictions" className="flex items-center gap-2">
                <Crystal className="h-4 w-4" />
                Predictions
              </TabsTrigger>
            </TabsList>

            <TabsContent value="events" className="mt-6">
              <EventTimeline events={openstarResults.events} />
            </TabsContent>

            <TabsContent value="tactical" className="mt-6">
              <TacticalAnalysisDisplay tacticalAnalysis={openstarResults.tactical_analysis} />
            </TabsContent>

            <TabsContent value="players" className="mt-6">
              <PlayerPerformancePanel playerEvaluations={openstarResults.player_evaluations} />
            </TabsContent>

            <TabsContent value="predictions" className="mt-6">
              <PredictionInsights predictions={openstarResults.predictions} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

function KeyRecommendations({ recommendations }: { recommendations: Recommendation[] }) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <AlertCircle className="h-4 w-4" />;
      case 'high':
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Target className="h-4 w-4" />;
    }
  };

  const sortedRecommendations = recommendations
    .sort((a, b) => {
      const priorityOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
      return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
             (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
    })
    .slice(0, 6);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Key Recommendations
        </CardTitle>
        <CardDescription>
          AI-generated insights and actionable recommendations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 md:grid-cols-2">
          {sortedRecommendations.map((rec, index) => (
            <div 
              key={index}
              className={`p-4 rounded-lg border ${getPriorityColor(rec.priority)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 pt-1">
                  {getPriorityIcon(rec.priority)}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm mb-1">{rec.title}</h4>
                  <p className="text-sm opacity-90 mb-2">{rec.recommendation}</p>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs capitalize">
                      {rec.type.replace('_', ' ')}
                    </Badge>
                    <span className="text-xs opacity-75">
                      {Math.round(rec.confidence * 100)}% confidence
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}