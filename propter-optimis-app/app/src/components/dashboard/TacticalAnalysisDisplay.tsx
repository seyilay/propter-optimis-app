import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TacticalAnalysis, 
  FormationAnalysis, 
  HPUSMetrics, 
  StrategicInsight,
  PossessionSequence,
  FieldTilt
} from '@/types';
import { 
  Shield, 
  Target, 
  TrendingUp, 
  Activity, 
  Users,
  ArrowRight,
  Timer,
  Zap,
  Brain
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

interface TacticalAnalysisDisplayProps {
  tacticalAnalysis: TacticalAnalysis;
  className?: string;
}

export function TacticalAnalysisDisplay({ 
  tacticalAnalysis, 
  className = "" 
}: TacticalAnalysisDisplayProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      <Tabs defaultValue="formations" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="formations">Formations</TabsTrigger>
          <TabsTrigger value="possession">Possession</TabsTrigger>
          <TabsTrigger value="pressure">HPUS Metrics</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="formations" className="space-y-4">
          <FormationsTab formations={tacticalAnalysis.formations} />
        </TabsContent>

        <TabsContent value="possession" className="space-y-4">
          <PossessionTab possessionAnalysis={tacticalAnalysis.possession_analysis} />
        </TabsContent>

        <TabsContent value="pressure" className="space-y-4">
          <HPUSTab hpusMetrics={tacticalAnalysis.hpus_metrics} />
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <InsightsTab insights={tacticalAnalysis.strategic_insights} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function FormationsTab({ formations }: { formations: any }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <FormationCard 
        title="Home Team Formation"
        formation={formations.home_team}
        team="home"
      />
      <FormationCard 
        title="Away Team Formation"
        formation={formations.away_team}
        team="away"
      />
      
      {formations.formation_changes && formations.formation_changes.length > 0 && (
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Formation Changes
            </CardTitle>
            <CardDescription>
              Tactical adjustments detected during the match
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {formations.formation_changes.map((change: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="text-sm text-gray-500">
                      {Math.floor(change.timestamp / 60)}:{String(Math.floor(change.timestamp % 60)).padStart(2, '0')}'
                    </div>
                    <Badge variant={change.team === 'home' ? 'default' : 'secondary'}>
                      {change.team === 'home' ? 'Home' : 'Away'}
                    </Badge>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-medium">{change.from_formation}</span>
                      <ArrowRight className="h-4 w-4 text-gray-400" />
                      <span className="font-medium">{change.to_formation}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {Math.round(change.confidence * 100)}% confidence
                    </Badge>
                    <div className="text-xs text-gray-500 capitalize">
                      {change.trigger_event.replace('_', ' ')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function FormationCard({ 
  title, 
  formation, 
  team 
}: { 
  title: string; 
  formation: FormationAnalysis; 
  team: 'home' | 'away' 
}) {
  const radarData = [
    { metric: 'Stability', value: formation.formation_stability * 100 },
    { metric: 'Discipline', value: formation.tactical_discipline * 100 },
    { metric: 'Confidence', value: formation.confidence * 100 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            {title}
          </span>
          <Badge variant={team === 'home' ? 'default' : 'secondary'} className="text-lg font-bold">
            {formation.primary_formation}
          </Badge>
        </CardTitle>
        <CardDescription>
          Formation analysis with tactical metrics
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Formation Stability</div>
              <div className="flex items-center gap-2 mt-1">
                <Progress 
                  value={formation.formation_stability * 100} 
                  className="flex-1 h-2"
                />
                <span className="font-medium">
                  {Math.round(formation.formation_stability * 100)}%
                </span>
              </div>
            </div>
            <div>
              <div className="text-gray-500">Tactical Discipline</div>
              <div className="flex items-center gap-2 mt-1">
                <Progress 
                  value={formation.tactical_discipline * 100} 
                  className="flex-1 h-2"
                />
                <span className="font-medium">
                  {Math.round(formation.tactical_discipline * 100)}%
                </span>
              </div>
            </div>
          </div>

          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 100]} 
                  tick={{ fontSize: 10 }}
                />
                <Radar
                  name="Formation Metrics"
                  dataKey="value"
                  stroke={team === 'home' ? '#7C3AED' : '#10B981'}
                  fill={team === 'home' ? '#7C3AED' : '#10B981'}
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="text-xs text-gray-500 text-center">
            Confidence: {Math.round(formation.confidence * 100)}%
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function PossessionTab({ possessionAnalysis }: { possessionAnalysis: any }) {
  const fieldTiltData = [
    { zone: 'Attacking', value: possessionAnalysis.field_tilt.attacking_tilt * 100 },
    { zone: 'Neutral', value: possessionAnalysis.field_tilt.neutral_play * 100 },
    { zone: 'Defensive', value: possessionAnalysis.field_tilt.defensive_tilt * 100 },
  ];

  const tempoData = [
    { period: '1st Half', tempo: possessionAnalysis.tempo_analysis.tempo_variations.first_half * 100 },
    { period: '2nd Half', tempo: possessionAnalysis.tempo_analysis.tempo_variations.second_half * 100 },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Field Tilt Analysis
          </CardTitle>
          <CardDescription>
            Territorial control and field positioning
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fieldTiltData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  dataKey="zone" 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Control']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#7C3AED" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-center">
            <div className="text-sm text-gray-500">Overall Field Tilt</div>
            <div className="text-lg font-bold">
              {possessionAnalysis.field_tilt.overall_tilt > 0 ? '+' : ''}
              {Math.round(possessionAnalysis.field_tilt.overall_tilt * 100)}%
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Timer className="h-5 w-5" />
            Match Tempo
          </CardTitle>
          <CardDescription>
            Game intensity and tempo variations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={tempoData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  dataKey="period" 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Tempo']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="tempo"
                  stroke="#10B981"
                  strokeWidth={2}
                  fill="#10B981"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-center">
            <div className="text-sm text-gray-500">Overall Tempo</div>
            <div className="text-lg font-bold">
              {Math.round(possessionAnalysis.tempo_analysis.overall_tempo * 100)}%
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Key Possession Sequences
          </CardTitle>
          <CardDescription>
            High-value possession chains and outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {possessionAnalysis.possession_sequences
              .filter((seq: PossessionSequence) => seq.xg_value > 0.1)
              .slice(0, 5)
              .map((sequence: PossessionSequence, index: number) => (
              <div key={sequence.sequence_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <Badge variant={sequence.team === 'home' ? 'default' : 'secondary'}>
                    {sequence.team === 'home' ? 'Home' : 'Away'}
                  </Badge>
                  <div className="flex items-center gap-2 text-sm">
                    <span>{sequence.passes_count} passes</span>
                    <span className="text-gray-400">•</span>
                    <span>{Math.round(sequence.duration)}s</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">{sequence.start_zone}</span>
                    <ArrowRight className="h-3 w-3 inline mx-1 text-gray-400" />
                    <span className="text-gray-500">{sequence.end_zone}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-sm font-medium">xG: {sequence.xg_value.toFixed(2)}</div>
                    <div className="text-xs text-gray-500 capitalize">{sequence.outcome}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function HPUSTab({ hpusMetrics }: { hpusMetrics: HPUSMetrics }) {
  const hpusData = [
    { metric: 'Overall HPUS', value: hpusMetrics.overall_hpus * 100 },
    { metric: 'Attacking HPUS', value: hpusMetrics.attacking_hpus * 100 },
    { metric: 'Defensive HPUS', value: hpusMetrics.defensive_hpus * 100 },
  ];

  const pressureData = [
    { 
      metric: 'High Press Success', 
      value: hpusMetrics.pressure_situations.high_press_success_rate * 100 
    },
    { 
      metric: 'Counter Press Efficiency', 
      value: hpusMetrics.pressure_situations.counter_press_efficiency * 100 
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            HPUS Metrics
          </CardTitle>
          <CardDescription>
            High-Pressure Utility Score analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hpusData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  type="number"
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  type="category"
                  dataKey="metric" 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  width={80}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Score']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#F59E0B" 
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Pressure Analysis
          </CardTitle>
          <CardDescription>
            Pressing effectiveness and recovery metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {pressureData.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{item.metric}</span>
                  <span className="font-medium">{Math.round(item.value)}%</span>
                </div>
                <Progress value={item.value} className="h-2" />
              </div>
            ))}
            
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Avg Recovery Time</span>
                <span className="font-medium">
                  {hpusMetrics.pressure_situations.pressure_recovery_time.toFixed(1)}s
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>HPUS Breakdown</CardTitle>
          <CardDescription>
            Detailed breakdown of High-Pressure Utility components
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {Math.round(hpusMetrics.overall_hpus * 100)}%
              </div>
              <div className="text-sm text-yellow-700 font-medium">Overall HPUS</div>
              <div className="text-xs text-yellow-600 mt-1">
                Combined pressure effectiveness
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-red-50 to-pink-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {Math.round(hpusMetrics.attacking_hpus * 100)}%
              </div>
              <div className="text-sm text-red-700 font-medium">Attacking HPUS</div>
              <div className="text-xs text-red-600 mt-1">
                High press efficiency
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(hpusMetrics.defensive_hpus * 100)}%
              </div>
              <div className="text-sm text-blue-700 font-medium">Defensive HPUS</div>
              <div className="text-xs text-blue-600 mt-1">
                Counter-press success
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InsightsTab({ insights }: { insights: StrategicInsight[] }) {
  const priorityOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
  
  const sortedInsights = insights
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 6); // Show top 6 insights

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'formation_effectiveness':
        return <Shield className="h-5 w-5" />;
      case 'possession_pattern':
        return <Target className="h-5 w-5" />;
      case 'tactical_pattern':
        return <Brain className="h-5 w-5" />;
      default:
        return <TrendingUp className="h-5 w-5" />;
    }
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.9) return <Badge className="bg-green-100 text-green-800">Very High</Badge>;
    if (confidence >= 0.8) return <Badge className="bg-blue-100 text-blue-800">High</Badge>;
    if (confidence >= 0.7) return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>;
    return <Badge className="bg-gray-100 text-gray-800">Low</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {sortedInsights.map((insight, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
                    {getInsightIcon(insight.insight_type)}
                  </div>
                  <div>
                    <CardTitle className="text-base">{insight.title}</CardTitle>
                    <CardDescription className="text-sm capitalize">
                      {insight.insight_type.replace('_', ' ')}
                    </CardDescription>
                  </div>
                </div>
                {getConfidenceBadge(insight.confidence)}
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm text-gray-700 mb-3">
                {insight.description}
              </p>
              {insight.actionable_recommendation && (
                <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                  <div className="text-xs font-medium text-blue-800 mb-1">
                    Recommendation
                  </div>
                  <p className="text-sm text-blue-700">
                    {insight.actionable_recommendation}
                  </p>
                </div>
              )}
              <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                {insight.supporting_metrics && Object.keys(insight.supporting_metrics).length > 0 && (
                  <span>
                    {Object.keys(insight.supporting_metrics).length} supporting metrics
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {insights.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Strategic Insights Available
            </h3>
            <p className="text-gray-500">
              Strategic insights will appear here once the tactical analysis is complete.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}