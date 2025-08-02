import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Brain, Target, TrendingUp, Activity, Eye, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const analysisData = [
  {
    month: 'Jan',
    analyses: 12,
    avgTime: 16.2,
    aiAccuracy: 89,
    eventsDetected: 340
  },
  {
    month: 'Feb',
    analyses: 19,
    avgTime: 15.8,
    aiAccuracy: 91,
    eventsDetected: 520
  },
  {
    month: 'Mar',
    analyses: 15,
    avgTime: 14.9,
    aiAccuracy: 93,
    eventsDetected: 430
  },
  {
    month: 'Apr',
    analyses: 23,
    avgTime: 15.4,
    aiAccuracy: 92,
    eventsDetected: 680
  },
  {
    month: 'May',
    analyses: 28,
    avgTime: 14.7,
    aiAccuracy: 94,
    eventsDetected: 820
  },
  {
    month: 'Jun',
    analyses: 31,
    avgTime: 14.2,
    aiAccuracy: 95,
    eventsDetected: 910
  }
];

// Mock recent analysis data for intelligence showcase
const recentIntelligenceData = [
  {
    id: '1',
    videoTitle: 'Premier League Match',
    eventsDetected: 87,
    tacticalInsights: 12,
    playerEvaluations: 22,
    confidenceScore: 0.94,
    processingTime: 12.3,
    analysisIntent: 'full_match_review',
    status: 'completed'
  },
  {
    id: '2',
    videoTitle: 'Training Session Analysis',
    eventsDetected: 45,
    tacticalInsights: 8,
    playerEvaluations: 16,
    confidenceScore: 0.91,
    processingTime: 8.7,
    analysisIntent: 'individual_player_performance',
    status: 'completed'
  },
  {
    id: '3',
    videoTitle: 'Opposition Scouting',
    eventsDetected: 62,
    tacticalInsights: 15,
    playerEvaluations: 11,
    confidenceScore: 0.89,
    processingTime: 14.1,
    analysisIntent: 'opposition_scouting',
    status: 'completed'
  }
];

export function AnalysisChart() {
  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          AI Intelligence Performance
        </CardTitle>
        <CardDescription>
          OpenStarLab analysis performance and intelligence metrics
        </CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={analysisData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis 
              dataKey="month" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value, name) => {
                switch (name) {
                  case 'analyses':
                    return [`${value} analyses`, 'Total Analyses'];
                  case 'avgTime':
                    return [`${value} min avg`, 'Avg Processing Time'];
                  case 'aiAccuracy':
                    return [`${value}%`, 'AI Accuracy'];
                  case 'eventsDetected':
                    return [`${value} events`, 'Events Detected'];
                  default:
                    return [value, name];
                }
              }}
            />
            <Bar 
              dataKey="analyses" 
              fill="#7C3AED" 
              radius={[4, 4, 0, 0]}
              name="analyses"
            />
            <Bar 
              dataKey="aiAccuracy" 
              fill="#10B981" 
              radius={[4, 4, 0, 0]}
              name="aiAccuracy"
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function IntelligenceInsightsPanel() {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Recent Intelligence Results
        </CardTitle>
        <CardDescription>
          Latest AI-powered football analysis insights
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentIntelligenceData.map((analysis, index) => (
            <div 
              key={analysis.id}
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium text-sm">{analysis.videoTitle}</h4>
                  <Badge variant="outline" className="text-xs capitalize">
                    {analysis.analysisIntent.replace('_', ' ')}
                  </Badge>
                </div>
                <Link to={`/analysis/${analysis.id}`}>
                  <Button size="sm" variant="outline">
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </Button>
                </Link>
              </div>
              
              <div className="grid grid-cols-4 gap-3 text-xs text-gray-600 mb-3">
                <div className="text-center">
                  <div className="font-medium text-purple-600">{analysis.eventsDetected}</div>
                  <div>Events</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-blue-600">{analysis.tacticalInsights}</div>
                  <div>Insights</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-green-600">{analysis.playerEvaluations}</div>
                  <div>Players</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-orange-600">{analysis.processingTime}m</div>
                  <div>Time</div>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Confidence:</span>
                  <Progress 
                    value={analysis.confidenceScore * 100} 
                    className="w-16 h-1"
                  />
                  <span className="text-xs font-medium">
                    {Math.round(analysis.confidenceScore * 100)}%
                  </span>
                </div>
                <Badge 
                  className={`text-xs ${
                    analysis.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {analysis.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ProcessingTimeChart() {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Processing Time Trend</CardTitle>
        <CardDescription>
          Average analysis processing time over time
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={analysisData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis 
              dataKey="month" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value) => [`${value} minutes`, 'Avg Processing Time']}
            />
            <Line 
              type="monotone" 
              dataKey="avgTime" 
              stroke="#10B981" 
              strokeWidth={3}
              dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#10B981', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}