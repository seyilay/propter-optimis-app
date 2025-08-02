import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { DetectedEvent, PlayerInvolved } from '@/types';
import { 
  Play,
  Pause,
  SkipForward,
  SkipBack,
  Target,
  Users,
  Clock,
  Filter,
  Search,
  Zap,
  AlertCircle,
  CheckCircle,
  MapPin
} from 'lucide-react';
import { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts';

interface EventTimelineProps {
  events: DetectedEvent[];
  className?: string;
}

export function EventTimeline({ events, className = "" }: EventTimelineProps) {
  const [selectedEventType, setSelectedEventType] = useState<string>('all');
  const [selectedTeam, setSelectedTeam] = useState<string>('all');
  const [confidenceFilter, setConfidenceFilter] = useState<number>(0);
  const [selectedEvent, setSelectedEvent] = useState<DetectedEvent | null>(null);

  // Get unique event types for filtering
  const eventTypes = useMemo(() => {
    const types = [...new Set(events.map(e => e.event_type))];
    return types.sort();
  }, [events]);

  // Filter events based on selected filters
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      if (selectedEventType !== 'all' && event.event_type !== selectedEventType) return false;
      if (selectedTeam !== 'all' && event.team !== selectedTeam) return false;
      if (event.confidence < confidenceFilter / 100) return false;
      return true;
    });
  }, [events, selectedEventType, selectedTeam, confidenceFilter]);

  // Create timeline data for chart
  const timelineData = useMemo(() => {
    const data: Array<{
      time: number;
      events: number;
      formattedTime: string;
    }> = [];

    // Create 10-minute buckets
    for (let i = 0; i <= 90; i += 10) {
      const eventsInBucket = filteredEvents.filter(
        event => event.timestamp >= i * 60 && event.timestamp < (i + 10) * 60
      ).length;
      
      data.push({
        time: i,
        events: eventsInBucket,
        formattedTime: `${i}-${i + 10}min`
      });
    }

    return data;
  }, [filteredEvents]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Event Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Event Type
              </label>
              <select
                value={selectedEventType}
                onChange={(e) => setSelectedEventType(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Events</option>
                {eventTypes.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Team
              </label>
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">Both Teams</option>
                <option value="home">Home Team</option>
                <option value="away">Away Team</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Min Confidence: {confidenceFilter}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={confidenceFilter}
                onChange={(e) => setConfidenceFilter(Number(e.target.value))}
                className="w-full"
              />
            </div>
            
            <div className="flex items-end">
              <div className="text-sm text-gray-600">
                <div>Showing {filteredEvents.length} of {events.length} events</div>
                <div className="text-xs text-gray-500 mt-1">
                  Avg confidence: {filteredEvents.length > 0 
                    ? Math.round(filteredEvents.reduce((sum, e) => sum + e.confidence, 0) / filteredEvents.length * 100)
                    : 0}%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timeline Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Event Distribution Over Time
          </CardTitle>
          <CardDescription>
            Number of events detected in 10-minute intervals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                <XAxis 
                  dataKey="formattedTime" 
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <Tooltip 
                  formatter={(value) => [`${value} events`, 'Events']}
                  labelFormatter={(label) => `Time: ${label}`}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="events" 
                  stroke="#7C3AED" 
                  strokeWidth={3}
                  dot={{ fill: '#7C3AED', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Event List */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Event Timeline ({filteredEvents.length})
                </span>
                <div className="text-sm text-gray-500">
                  Click event for details
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredEvents
                  .sort((a, b) => a.timestamp - b.timestamp)
                  .map((event) => (
                    <EventCard 
                      key={event.id} 
                      event={event} 
                      isSelected={selectedEvent?.id === event.id}
                      onClick={() => setSelectedEvent(event)}
                    />
                  ))}
                
                {filteredEvents.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No events match the current filters</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Event Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Event Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedEvent ? (
              <EventDetails event={selectedEvent} />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <MapPin className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Select an event to view details</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function EventCard({ 
  event, 
  isSelected, 
  onClick 
}: { 
  event: DetectedEvent; 
  isSelected: boolean;
  onClick: () => void;
}) {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'goal': return '⚽';
      case 'shot': return '🎯';
      case 'pass': return '➡️';
      case 'tackle': return '🛡️';
      case 'foul': return '⚠️';
      case 'yellow_card': return '🟨';
      case 'red_card': return '🟥';
      case 'corner_kick': return '📐';
      case 'throw_in': return '🤾';
      case 'offside': return '🚩';
      default: return '⚽';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800';
    if (confidence >= 0.8) return 'bg-blue-100 text-blue-800';
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div 
      className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-xl">{getEventIcon(event.event_type)}</div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {event.formatted_time}
              </span>
              <Badge variant={event.team === 'home' ? 'default' : 'secondary'} className="text-xs">
                {event.team === 'home' ? 'H' : 'A'}
              </Badge>
            </div>
            <div className="text-xs text-gray-600 capitalize">
              {event.event_type.replace('_', ' ')}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge className={`text-xs ${getConfidenceColor(event.confidence)}`}>
            {Math.round(event.confidence * 100)}%
          </Badge>
          {event.players_involved.length > 0 && (
            <div className="text-xs text-gray-500">
              #{event.players_involved[0].jersey_number}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EventDetails({ event }: { event: DetectedEvent }) {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'goal': return '⚽';
      case 'shot': return '🎯';
      case 'pass': return '➡️';
      case 'tackle': return '🛡️';
      case 'foul': return '⚠️';
      case 'yellow_card': return '🟨';
      case 'red_card': return '🟥';
      case 'corner_kick': return '📐';
      case 'throw_in': return '🤾';
      case 'offside': return '🚩';
      default: return '⚽';
    }
  };

  return (
    <div className="space-y-4">
      {/* Event Header */}
      <div className="text-center">
        <div className="text-4xl mb-2">{getEventIcon(event.event_type)}</div>
        <h3 className="font-bold text-lg capitalize">
          {event.event_type.replace('_', ' ')}
        </h3>
        <div className="text-sm text-gray-600">
          {event.formatted_time} • {event.team === 'home' ? 'Home Team' : 'Away Team'}
        </div>
      </div>

      {/* Confidence */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Confidence</span>
          <span className="font-medium">{Math.round(event.confidence * 100)}%</span>
        </div>
        <Progress value={event.confidence * 100} className="h-2" />
      </div>

      {/* Field Position */}
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="text-sm font-medium text-gray-700 mb-2">Field Position</div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-500">X:</span> {Math.round(event.coordinates.x)}%
          </div>
          <div>
            <span className="text-gray-500">Y:</span> {Math.round(event.coordinates.y)}%
          </div>
        </div>
        {event.coordinates.zone && (
          <div className="text-xs text-gray-500 mt-1 capitalize">
            {event.coordinates.zone.replace('_', ' ')}
          </div>
        )}
      </div>

      {/* Players Involved */}
      {event.players_involved.length > 0 && (
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">
            Players Involved
          </div>
          <div className="space-y-2">
            {event.players_involved.map((player, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    #{player.jersey_number}
                  </Badge>
                  <span className="text-gray-600">{player.position}</span>
                  <Badge 
                    variant={player.role === 'primary' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {player.role}
                  </Badge>
                </div>
                <div className="text-xs text-gray-500">
                  {Math.round(player.confidence * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Context Information */}
      {event.context && (
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="text-sm font-medium text-blue-800 mb-2">Context</div>
          <div className="space-y-1 text-xs text-blue-700">
            {event.context.phase_of_play && (
              <div className="flex justify-between">
                <span>Phase:</span>
                <span className="capitalize">{event.context.phase_of_play}</span>
              </div>
            )}
            {event.context.pressure_level && (
              <div className="flex justify-between">
                <span>Pressure:</span>
                <span className="capitalize">{event.context.pressure_level}</span>
              </div>
            )}
            {event.context.field_tilt !== undefined && (
              <div className="flex justify-between">
                <span>Field Tilt:</span>
                <span>{event.context.field_tilt > 0 ? '+' : ''}{Math.round(event.context.field_tilt * 100)}%</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2">
        <Button size="sm" variant="outline" className="flex-1">
          <Play className="h-3 w-3 mr-1" />
          Watch
        </Button>
        <Button size="sm" variant="outline" className="flex-1">
          <MapPin className="h-3 w-3 mr-1" />
          Locate
        </Button>
      </div>
    </div>
  );
}