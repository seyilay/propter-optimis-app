import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  PlayerEvaluations, 
  PlayerMetrics,
  PerformanceInsight,
  TeamCohesionMetrics
} from '@/types';
import { 
  User,
  Trophy,
  Target,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  Star,
  Flame,
  Shield,
  Zap
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
  ScatterChart,
  Scatter,
  Cell
} from 'recharts';

interface PlayerPerformancePanelProps {
  playerEvaluations: PlayerEvaluations;
  className?: string;
}

export function PlayerPerformancePanel({ 
  playerEvaluations, 
  className = "" 
}: PlayerPerformancePanelProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      <Tabs defaultValue="performance" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="rankings">Rankings</TabsTrigger>
          <TabsTrigger value="cohesion">Team Cohesion</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <PerformanceTab playerMetrics={playerEvaluations.player_metrics} />
        </TabsContent>

        <TabsContent value="rankings" className="space-y-4">
          <RankingsTab playerMetrics={playerEvaluations.player_metrics} />
        </TabsContent>

        <TabsContent value="cohesion" className="space-y-4">
          <CohesionTab teamCohesion={playerEvaluations.team_cohesion_metrics} />
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <InsightsTab insights={playerEvaluations.performance_insights} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function PerformanceTab({ playerMetrics }: { playerMetrics: Record<string, PlayerMetrics> }) {
  const topPerformers = Object.values(playerMetrics)
    .sort((a, b) => b.overall_performance_score - a.overall_performance_score)
    .slice(0, 6);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {topPerformers.map((player) => (
        <PlayerCard key={player.player_id} player={player} />
      ))}
    </div>
  );
}

function PlayerCard({ player }: { player: PlayerMetrics }) {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+': case 'A': return 'text-green-600 bg-green-100';
      case 'B+': case 'B': return 'text-blue-600 bg-blue-100';
      case 'C+': case 'C': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-red-600 bg-red-100';
    }
  };

  const getTeamColor = (team: string) => {
    return team === 'home' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700';
  };

  const topActions = Object.entries(player.action_breakdown)
    .sort(([,a], [,b]) => b.count - a.count)
    .slice(0, 3);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center">
              <span className="text-lg font-bold text-purple-700">
                #{player.jersey_number}
              </span>
            </div>
            <div>
              <CardTitle className="text-base">
                Player #{player.jersey_number}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-xs">
                  {player.position}
                </Badge>
                <Badge className={`text-xs ${getTeamColor(player.team)}`}>
                  {player.team === 'home' ? 'Home' : 'Away'}
                </Badge>
              </div>
            </div>
          </div>
          <Badge className={`text-lg font-bold ${getGradeColor(player.performance_grade)}`}>
            {player.performance_grade}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overall Performance Score */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-600">Overall Performance</span>
            <span className="font-medium">
              {Math.round(player.overall_performance_score * 100)}%
            </span>
          </div>
          <Progress value={player.overall_performance_score * 100} className="h-2" />
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className="font-medium">{player.total_actions}</div>
            <div className="text-xs text-gray-500">Total Actions</div>
          </div>
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className="font-medium">{Math.round(player.consistency_score * 100)}%</div>
            <div className="text-xs text-gray-500">Consistency</div>
          </div>
        </div>

        {/* Top Actions */}
        <div>
          <div className="text-xs font-medium text-gray-600 mb-2">Top Actions</div>
          <div className="space-y-1">
            {topActions.map(([action, data]) => (
              <div key={action} className="flex justify-between text-xs">
                <span className="capitalize">{action.replace('_', ' ')}</span>
                <div className="flex items-center gap-2">
                  <span>{data.count}</span>
                  <div className={`w-2 h-2 rounded-full ${
                    data.success_rate > 0.7 ? 'bg-green-400' : 
                    data.success_rate > 0.5 ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Special Attributes */}
        <div className="flex justify-between text-xs">
          <div className="flex items-center gap-1">
            <Flame className="h-3 w-3 text-orange-500" />
            <span>Clutch: {Math.round(player.clutch_performance * 100)}%</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-3 w-3 text-blue-500" />
            <span>Team: {Math.round(player.team_contribution * 100)}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function RankingsTab({ playerMetrics }: { playerMetrics: Record<string, PlayerMetrics> }) {
  const allPlayers = Object.values(playerMetrics);
  
  const performanceRankings = allPlayers
    .sort((a, b) => b.overall_performance_score - a.overall_performance_score);

  const consistencyRankings = allPlayers
    .sort((a, b) => b.consistency_score - a.consistency_score);

  const clutchRankings = allPlayers
    .sort((a, b) => b.clutch_performance - a.clutch_performance);

  const teamContributionRankings = allPlayers
    .sort((a, b) => b.team_contribution - a.team_contribution);

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <RankingCard 
        title="Overall Performance"
        icon={<Trophy className="h-5 w-5" />}
        players={performanceRankings.slice(0, 5)}
        getValue={(player) => player.overall_performance_score * 100}
        getColor={() => "text-yellow-600"}
      />
      
      <RankingCard 
        title="Consistency"
        icon={<Target className="h-5 w-5" />}
        players={consistencyRankings.slice(0, 5)}
        getValue={(player) => player.consistency_score * 100}
        getColor={() => "text-blue-600"}
      />
      
      <RankingCard 
        title="Clutch Performance"
        icon={<Flame className="h-5 w-5" />}
        players={clutchRankings.slice(0, 5)}
        getValue={(player) => player.clutch_performance * 100}
        getColor={() => "text-orange-600"}
      />
      
      <RankingCard 
        title="Team Contribution"
        icon={<Users className="h-5 w-5" />}
        players={teamContributionRankings.slice(0, 5)}
        getValue={(player) => player.team_contribution * 100}
        getColor={() => "text-green-600"}
      />
    </div>
  );
}

function RankingCard({ 
  title, 
  icon, 
  players, 
  getValue, 
  getColor 
}: { 
  title: string;
  icon: React.ReactNode;
  players: PlayerMetrics[];
  getValue: (player: PlayerMetrics) => number;
  getColor: (player: PlayerMetrics) => string;
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {players.map((player, index) => (
            <div key={player.player_id} className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                index === 0 ? 'bg-yellow-100 text-yellow-700' :
                index === 1 ? 'bg-gray-100 text-gray-700' :
                index === 2 ? 'bg-orange-100 text-orange-700' :
                'bg-blue-50 text-blue-600'
              }`}>
                {index + 1}
              </div>
              <div className="flex-1 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium">#{player.jersey_number}</span>
                  <Badge variant="outline" className="text-xs">
                    {player.position}
                  </Badge>
                  <Badge className={`text-xs ${
                    player.team === 'home' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {player.team === 'home' ? 'H' : 'A'}
                  </Badge>
                </div>
                <div className={`font-bold ${getColor(player)}`}>
                  {Math.round(getValue(player))}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function CohesionTab({ teamCohesion }: { teamCohesion: TeamCohesionMetrics }) {
  const cohesionData = [
    { team: 'Home', cohesion: teamCohesion.home_team_cohesion * 100 },
    { team: 'Away', cohesion: teamCohesion.away_team_cohesion * 100 },
  ];

  const teamMetrics = [
    { 
      metric: 'Pass Network Density', 
      value: teamCohesion.pass_network_density * 100,
      icon: <Activity className="h-4 w-4" />,
      color: 'text-blue-600'
    },
    { 
      metric: 'Positional Coordination', 
      value: teamCohesion.positional_coordination * 100,
      icon: <Target className="h-4 w-4" />,
      color: 'text-green-600'
    },
    { 
      metric: 'Tactical Synchronization', 
      value: teamCohesion.tactical_synchronization * 100,
      icon: <Zap className="h-4 w-4" />,
      color: 'text-purple-600'
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Cohesion Comparison
          </CardTitle>
          <CardDescription>
            Overall team cohesion metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cohesionData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  dataKey="team" 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Cohesion']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Bar dataKey="cohesion" radius={[4, 4, 0, 0]}>
                  <Cell fill="#7C3AED" />
                  <Cell fill="#10B981" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Coordination Metrics
          </CardTitle>
          <CardDescription>
            Team coordination and synchronization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {teamMetrics.map((metric, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-sm">
                    <span className={metric.color}>{metric.icon}</span>
                    <span className="text-gray-700">{metric.metric}</span>
                  </div>
                  <span className="text-sm font-medium">
                    {Math.round(metric.value)}%
                  </span>
                </div>
                <Progress value={metric.value} className="h-2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Team Chemistry Analysis</CardTitle>
          <CardDescription>
            Detailed breakdown of team coordination metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(teamCohesion.home_team_cohesion * 100)}%
              </div>
              <div className="text-sm text-blue-700 font-medium">Home Cohesion</div>
              <div className="text-xs text-blue-600 mt-1">
                Team chemistry score
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {Math.round(teamCohesion.away_team_cohesion * 100)}%
              </div>
              <div className="text-sm text-green-700 font-medium">Away Cohesion</div>
              <div className="text-xs text-green-600 mt-1">
                Team chemistry score
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(teamCohesion.pass_network_density * 100)}%
              </div>
              <div className="text-sm text-purple-700 font-medium">Network Density</div>
              <div className="text-xs text-purple-600 mt-1">
                Passing connectivity
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(teamCohesion.tactical_synchronization * 100)}%
              </div>
              <div className="text-sm text-orange-700 font-medium">Synchronization</div>
              <div className="text-xs text-orange-600 mt-1">
                Tactical alignment
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InsightsTab({ insights }: { insights: PerformanceInsight[] }) {
  const sortedInsights = insights
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 6);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'top_performer':
        return <Star className="h-5 w-5" />;
      case 'consistency':
        return <Target className="h-5 w-5" />;
      case 'improvement_area':
        return <TrendingUp className="h-5 w-5" />;
      case 'tactical_impact':
        return <Shield className="h-5 w-5" />;
      default:
        return <User className="h-5 w-5" />;
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
      {sortedInsights.map((insight, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
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
            
            {insight.player_id && (
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline" className="text-xs">
                  Player ID: {insight.player_id}
                </Badge>
                {insight.performance_score && (
                  <Badge className="bg-purple-100 text-purple-800 text-xs">
                    Score: {Math.round(insight.performance_score * 100)}%
                  </Badge>
                )}
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
              <span className="capitalize">{insight.insight_type.replace('_', ' ')} insight</span>
            </div>
          </CardContent>
        </Card>
      ))}

      {insights.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Performance Insights Available
            </h3>
            <p className="text-gray-500">
              Player performance insights will appear here once the analysis is complete.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}