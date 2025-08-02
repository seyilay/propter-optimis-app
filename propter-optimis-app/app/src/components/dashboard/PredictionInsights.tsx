import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  PredictiveInsights, 
  ScorePrediction,
  FormationChangePrediction,
  TacticalAdjustment
} from '@/types';
import { 
  Crystal,
  Target,
  TrendingUp,
  Clock,
  Users,
  Activity,
  Zap,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowRight,
  Timer
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

interface PredictionInsightsProps {
  predictions: PredictiveInsights;
  className?: string;
}

export function PredictionInsights({ 
  predictions, 
  className = "" 
}: PredictionInsightsProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      <Tabs defaultValue="match-outcomes" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="match-outcomes">Match Outcomes</TabsTrigger>
          <TabsTrigger value="tactical">Tactical</TabsTrigger>
          <TabsTrigger value="players">Players</TabsTrigger>
          <TabsTrigger value="formations">Formations</TabsTrigger>
        </TabsList>

        <TabsContent value="match-outcomes" className="space-y-4">
          <MatchOutcomesTab predictions={predictions.match_outcomes} />
        </TabsContent>

        <TabsContent value="tactical" className="space-y-4">
          <TacticalTab predictions={predictions.tactical_scenarios} />
        </TabsContent>

        <TabsContent value="players" className="space-y-4">
          <PlayersTab predictions={predictions.player_performance} />
        </TabsContent>

        <TabsContent value="formations" className="space-y-4">
          <FormationsTab predictions={predictions.formation_effectiveness} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function MatchOutcomesTab({ predictions }: { predictions: any }) {
  const COLORS = ['#7C3AED', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6'];

  const pieData = predictions.final_score_predictions
    .slice(0, 6)
    .map((pred: ScorePrediction, index: number) => ({
      name: pred.scoreline,
      value: pred.probability * 100,
      color: COLORS[index]
    }));

  const eventsData = [
    { 
      event: 'Goals', 
      predicted: predictions.match_events_predictions.total_goals.predicted,
      confidence: predictions.match_events_predictions.total_goals.confidence * 100
    },
    { 
      event: 'Cards', 
      predicted: predictions.match_events_predictions.total_cards.predicted,
      confidence: predictions.match_events_predictions.total_cards.confidence * 100
    },
    { 
      event: 'Corners', 
      predicted: predictions.match_events_predictions.corner_kicks.predicted,
      confidence: predictions.match_events_predictions.corner_kicks.confidence * 100
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Score Predictions
          </CardTitle>
          <CardDescription>
            Most likely final score outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Probability']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {predictions.final_score_predictions.slice(0, 3).map((pred: ScorePrediction, index: number) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: COLORS[index] }}
                  />
                  <span className="font-medium">{pred.scoreline}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>{Math.round(pred.probability * 100)}%</span>
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${
                      pred.confidence > 0.8 ? 'text-green-600' : 
                      pred.confidence > 0.6 ? 'text-yellow-600' : 'text-red-600'
                    }`}
                  >
                    {Math.round(pred.confidence * 100)}% conf
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Match Events Forecast
          </CardTitle>
          <CardDescription>
            Predicted number of key events
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={eventsData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  dataKey="event" 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'predicted' ? `${value} events` : `${value}%`,
                    name === 'predicted' ? 'Predicted' : 'Confidence'
                  ]}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Bar 
                  dataKey="predicted" 
                  fill="#7C3AED" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Comeback Analysis */}
      {predictions.comeback_probability.comeback_team && (
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Comeback Probability Analysis
            </CardTitle>
            <CardDescription>
              Likelihood of comeback scenario
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {Math.round(predictions.comeback_probability.comeback_probability * 100)}%
                </div>
                <div className="text-sm text-orange-700 font-medium">Comeback Chance</div>
                <div className="text-xs text-orange-600 mt-1">
                  {predictions.comeback_probability.comeback_team === 'home' ? 'Home' : 'Away'} team
                </div>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {predictions.comeback_probability.goal_deficit}
                </div>
                <div className="text-sm text-blue-700 font-medium">Goal Deficit</div>
                <div className="text-xs text-blue-600 mt-1">
                  Current gap to overcome
                </div>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(predictions.comeback_probability.confidence * 100)}%
                </div>
                <div className="text-sm text-green-700 font-medium">Confidence</div>
                <div className="text-xs text-green-600 mt-1">
                  Prediction reliability
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function TacticalTab({ predictions }: { predictions: any }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Formation Changes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Predicted Formation Changes
          </CardTitle>
          <CardDescription>
            Likely tactical adjustments during the match
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {predictions.formation_changes.slice(0, 4).map((change: FormationChangePrediction, index: number) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">
                      {Math.floor(change.predicted_time / 60)}:{String(Math.floor(change.predicted_time % 60)).padStart(2, '0')}'
                    </span>
                    <Badge variant={change.team === 'home' ? 'default' : 'secondary'} className="text-xs">
                      {change.team === 'home' ? 'Home' : 'Away'}
                    </Badge>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${
                      change.expected_impact === 'positive' ? 'text-green-600' :
                      change.expected_impact === 'negative' ? 'text-red-600' : 'text-gray-600'
                    }`}
                  >
                    {Math.round(change.probability * 100)}% likely
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="font-medium">{change.current_formation}</span>
                  <ArrowRight className="h-3 w-3" />
                  <span className="font-medium">{change.predicted_formation}</span>
                  <span className="text-gray-500 ml-2">
                    ({change.expected_impact} impact)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tactical Adjustments */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Tactical Adjustments
          </CardTitle>
          <CardDescription>
            Expected strategic modifications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {predictions.tactical_adjustments.map((adjustment: TacticalAdjustment, index: number) => (
              <div key={index} className="border-l-4 border-purple-400 pl-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium capitalize">
                    {adjustment.adjustment_type.replace('_', ' ')}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {Math.round(adjustment.probability * 100)}% likely
                  </Badge>
                </div>
                <div className="text-xs text-gray-600 mb-2">
                  Predicted change: <span className="font-medium">{adjustment.predicted_change}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Effectiveness:</span>
                  <Progress value={adjustment.expected_effectiveness * 100} className="flex-1 h-1" />
                  <span className="text-xs font-medium">
                    {Math.round(adjustment.expected_effectiveness * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Substitution Impact */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Substitution Impact Analysis
          </CardTitle>
          <CardDescription>
            Predicted substitution timing and effectiveness
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg text-center">
              <Timer className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-blue-600">
                {Math.floor(predictions.substitution_impact.optimal_substitution_time / 60)}'
              </div>
              <div className="text-sm text-blue-700 font-medium">Optimal Timing</div>
              <div className="text-xs text-blue-600">
                Best substitution window
              </div>
            </div>
            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg text-center">
              <Users className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-green-600">
                {predictions.substitution_impact.predicted_substitutions}
              </div>
              <div className="text-sm text-green-700 font-medium">Expected Subs</div>
              <div className="text-xs text-green-600">
                Total substitutions
              </div>
            </div>
            <div className="space-y-2">
              {predictions.substitution_impact.impact_predictions.map((impact: any, index: number) => (
                <div key={index} className="p-2 bg-gray-50 rounded text-sm">
                  <div className="flex justify-between items-center">
                    <span className="capitalize font-medium">
                      {impact.substitution_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {Math.round(impact.expected_impact * 100)}% impact
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function PlayersTab({ predictions }: { predictions: any }) {
  const impactPlayers = predictions.impact_players.slice(0, 5);
  const substitutionCandidates = predictions.substitution_candidates.slice(0, 5);

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Impact Players
          </CardTitle>
          <CardDescription>
            Players predicted to have significant influence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {impactPlayers.map((player: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    index === 0 ? 'bg-yellow-100 text-yellow-700' :
                    index === 1 ? 'bg-gray-100 text-gray-700' :
                    index === 2 ? 'bg-orange-100 text-orange-700' :
                    'bg-blue-50 text-blue-600'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium text-sm">Player {player.player_id}</div>
                    <div className="text-xs text-gray-600">
                      Impact Score: {Math.round(player.impact_score * 100)}%
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-green-600">
                    {Math.round(player.predicted_contribution * 100)}%
                  </div>
                  <div className="text-xs text-green-700">Expected</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Substitution Candidates
          </CardTitle>
          <CardDescription>
            Players likely to be substituted
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {substitutionCandidates.map((candidate: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                    {candidate.urgency === 'high' ? (
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                    ) : (
                      <Clock className="h-4 w-4 text-orange-600" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-sm">Player {candidate.player_id}</div>
                    <div className="text-xs text-gray-600 capitalize">
                      Reason: {candidate.reason}
                    </div>
                  </div>
                </div>
                <Badge 
                  variant={candidate.urgency === 'high' ? 'destructive' : 'secondary'}
                  className="text-xs"
                >
                  {candidate.urgency} urgency
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Trends Chart */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Performance Trend Predictions
          </CardTitle>
          <CardDescription>
            Expected performance changes throughout the match
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {Object.entries(predictions.performance_trends)
              .slice(0, 6)
              .map(([playerId, trend]: [string, any], index) => (
                <div key={playerId} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Player {playerId}</span>
                    <Badge 
                      variant={
                        trend.predicted_trend === 'improving' ? 'default' :
                        trend.predicted_trend === 'declining' ? 'destructive' : 'secondary'
                      }
                      className="text-xs"
                    >
                      {trend.predicted_trend}
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <div className="text-xs text-gray-600">
                      Current: {Math.round(trend.current_score * 100)}%
                    </div>
                    <div className="text-xs text-gray-600">
                      Confidence: {Math.round(trend.confidence * 100)}%
                    </div>
                    <Progress 
                      value={trend.current_score * 100} 
                      className="h-1"
                    />
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function FormationsTab({ predictions }: { predictions: any }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Current Formation Effectiveness
          </CardTitle>
          <CardDescription>
            Analysis of current tactical setup
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(predictions.current_formation_effectiveness).map(([team, data]: [string, any]) => (
              <div key={team} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Badge variant={team === 'home_team' ? 'default' : 'secondary'}>
                      {team === 'home_team' ? 'Home' : 'Away'}
                    </Badge>
                    <span className="font-bold text-lg">{data.formation}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-purple-600">
                      {Math.round(data.predicted_effectiveness * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">Effectiveness</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <div className="font-medium text-green-600 mb-1">Strengths</div>
                    <ul className="space-y-1">
                      {data.strengths.map((strength: string, index: number) => (
                        <li key={index} className="flex items-center gap-1">
                          <CheckCircle className="h-3 w-3 text-green-500" />
                          <span className="capitalize">{strength.replace('_', ' ')}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="font-medium text-red-600 mb-1">Weaknesses</div>
                    <ul className="space-y-1">
                      {data.weaknesses.map((weakness: string, index: number) => (
                        <li key={index} className="flex items-center gap-1">
                          <XCircle className="h-3 w-3 text-red-500" />
                          <span className="capitalize">{weakness.replace('_', ' ')}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Crystal className="h-5 w-5" />
            Alternative Formations
          </CardTitle>
          <CardDescription>
            Potential tactical alternatives and their impact
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(predictions.alternative_formation_analysis).map(([team, alternatives]: [string, any]) => (
              <div key={team}>
                <h4 className="font-medium mb-2 capitalize">
                  {team.replace('_', ' ')} Alternatives
                </h4>
                <div className="space-y-2">
                  {alternatives.slice(0, 3).map((alt: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{alt.formation}</span>
                        <Badge 
                          variant={alt.expected_improvement > 0 ? 'default' : 'destructive'}
                          className="text-xs"
                        >
                          {alt.expected_improvement > 0 ? '+' : ''}{Math.round(alt.expected_improvement * 100)}%
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-500">
                        {Math.round(alt.predicted_effectiveness * 100)}% effective
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}