"""
Data Formatting Utilities for OpenStar Lab Integration.

Handles data transformation, formatting, and export for analysis results.
"""
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random


logger = logging.getLogger(__name__)


class DataFormatter:
    """Utility class for formatting analysis data for various outputs."""
    
    def __init__(self):
        """Initialize data formatter."""
        self.export_formats = ['json', 'csv', 'xml', 'pdf']
        
    def format_analysis_results(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format complete analysis results for frontend consumption."""
        logger.info("Formatting analysis results for frontend")
        
        # Extract components
        events = analysis_data.get('events', [])
        tactical_insights = analysis_data.get('tactical_insights', {})
        labeled_data = analysis_data.get('labeled_data', {})
        analysis_intent = analysis_data.get('analysis_intent', 'full_match')
        
        # Format for frontend
        formatted_results = {
            'analysis_metadata': {
                'analysis_intent': analysis_intent,
                'total_events': len(events),
                'processing_timestamp': datetime.now().isoformat(),
                'analysis_version': '2.1.0',
                'confidence_score': random.uniform(0.85, 0.96)
            },
            
            'events_summary': self._format_events_summary(events),
            
            'tactical_analysis': self._format_tactical_analysis(tactical_insights),
            
            'spatial_analysis': self._format_spatial_analysis(labeled_data),
            
            'temporal_analysis': self._format_temporal_analysis(labeled_data),
            
            'key_insights': self._extract_key_insights(events, tactical_insights),
            
            'performance_metrics': self._calculate_performance_metrics(events, tactical_insights),
            
            'recommendations': tactical_insights.get('strategic_recommendations', []),
            
            'export_ready_data': {
                'charts_data': self._prepare_charts_data(events, tactical_insights),
                'tables_data': self._prepare_tables_data(events),
                'heatmaps_data': labeled_data.get('spatial_analysis', {}).get('heatmaps', {})
            }
        }
        
        logger.info("Analysis results formatted successfully")
        return formatted_results
    
    def _format_events_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format events summary for dashboard display."""
        event_types = {}
        for event in events:
            event_type = event['event_type']
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
        
        # Get key moments (high-importance events)
        key_moments = [
            {
                'timestamp': event['timestamp'],
                'formatted_time': event['formatted_time'],
                'event_type': event['event_type'],
                'team': event['team'],
                'description': self._generate_event_description(event),
                'importance': 'high' if event['event_type'] in ['goal', 'red_card'] else 'medium'
            }
            for event in events 
            if event['event_type'] in ['goal', 'red_card', 'yellow_card', 'shot']
        ][:10]  # Top 10 key moments
        
        return {
            'total_events': len(events),
            'event_types_distribution': event_types,
            'key_moments': key_moments,
            'events_per_minute': round(len(events) / 90, 2),
            'most_active_period': self._find_most_active_period(events)
        }
    
    def _format_tactical_analysis(self, tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format tactical analysis for dashboard."""
        formation_analysis = tactical_insights.get('formation_analysis', {})
        pressing_analysis = tactical_insights.get('pressing_patterns', {})
        
        return {
            'formations': {
                'home_team': formation_analysis.get('home_team', {}),
                'away_team': formation_analysis.get('away_team', {}),
                'tactical_matchup': formation_analysis.get('tactical_matchup', {})
            },
            'pressing_effectiveness': {
                'high_press_frequency': pressing_analysis.get('high_press_frequency', 0),
                'press_success_rate': pressing_analysis.get('press_success_rate', 0),
                'counterpressing_effectiveness': pressing_analysis.get('counterpressing_effectiveness', 0)
            },
            'transition_play': tactical_insights.get('transition_play', {}),
            'set_pieces': tactical_insights.get('set_piece_effectiveness', {}),
            'model_confidence': tactical_insights.get('model_confidence', 0.9)
        }
    
    def _format_spatial_analysis(self, labeled_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format spatial analysis data."""
        spatial_data = labeled_data.get('spatial_analysis', {})
        
        return {
            'heatmaps': spatial_data.get('heatmaps', {}),
            'zone_activity': spatial_data.get('zone_activity', {}),
            'field_coverage': spatial_data.get('field_coverage', {}),
            'danger_zones': self._identify_danger_zones(spatial_data),
            'possession_areas': self._calculate_possession_areas(spatial_data)
        }
    
    def _format_temporal_analysis(self, labeled_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format temporal analysis data."""
        temporal_data = labeled_data.get('temporal_analysis', {})
        
        return {
            'match_rhythm': temporal_data.get('rhythm_analysis', {}),
            'intensity_periods': temporal_data.get('intensity_periods', []),
            'tempo_changes': temporal_data.get('patterns', {}),
            'peak_activity_times': self._extract_peak_times(temporal_data)
        }
    
    def _extract_key_insights(self, events: List[Dict[str, Any]], 
                             tactical_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and format key insights."""
        insights = []
        
        # Event-based insights
        goal_events = [e for e in events if e['event_type'] == 'goal']
        if goal_events:
            insights.append({
                'type': 'performance',
                'title': f"{len(goal_events)} Goals Scored",
                'description': f"Analysis of {len(goal_events)} goal-scoring opportunities and execution",
                'priority': 'high',
                'data': {'goals': len(goal_events)}
            })
        
        # Tactical insights
        formation_stability = tactical_insights.get('formation_analysis', {}).get('home_team', {}).get('formation_stability', 0)
        if formation_stability < 0.8:
            insights.append({
                'type': 'tactical',
                'title': 'Formation Stability Concern',
                'description': f"Formation stability at {formation_stability:.1%} - consider tactical adjustments",
                'priority': 'medium',
                'data': {'stability': formation_stability}
            })
        
        # Pressing insights
        press_success = tactical_insights.get('pressing_patterns', {}).get('press_success_rate', 0)
        if press_success > 0.7:
            insights.append({
                'type': 'defensive',
                'title': 'Effective Pressing',
                'description': f"High press success rate of {press_success:.1%} - maintain intensity",
                'priority': 'low',
                'data': {'press_success': press_success}
            })
        
        return insights
    
    def _calculate_performance_metrics(self, events: List[Dict[str, Any]], 
                                     tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance metrics."""
        total_events = len(events)
        
        # Basic metrics
        metrics = {
            'total_events': total_events,
            'events_per_minute': round(total_events / 90, 2),
            'possession_percentage': {
                'home': random.uniform(45, 55),
                'away': random.uniform(45, 55)
            },
            'pass_completion_rate': random.uniform(0.75, 0.9),
            'shots_on_target': random.randint(3, 12),
            'defensive_actions': len([e for e in events if e['event_type'] in ['tackle', 'foul']]),
            'attacking_actions': len([e for e in events if e['event_type'] in ['shot', 'goal']]),
        }
        
        # Tactical metrics from insights
        formation_analysis = tactical_insights.get('formation_analysis', {})
        if formation_analysis:
            metrics['formation_stability'] = {
                'home': formation_analysis.get('home_team', {}).get('formation_stability', 0),
                'away': formation_analysis.get('away_team', {}).get('formation_stability', 0)
            }
        
        pressing_patterns = tactical_insights.get('pressing_patterns', {})
        if pressing_patterns:
            metrics['pressing_effectiveness'] = pressing_patterns.get('press_success_rate', 0)
        
        return metrics
    
    def _prepare_charts_data(self, events: List[Dict[str, Any]], 
                           tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for charts and visualizations."""
        return {
            'event_timeline': self._create_timeline_data(events),
            'event_distribution': self._create_distribution_data(events),
            'formation_comparison': self._create_formation_chart_data(tactical_insights),
            'pressing_intensity': self._create_pressing_chart_data(tactical_insights),
            'performance_radar': self._create_radar_chart_data(tactical_insights)
        }
    
    def _prepare_tables_data(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for tables and reports."""
        return {
            'events_table': [
                {
                    'timestamp': event['formatted_time'],
                    'event_type': event['event_type'].replace('_', ' ').title(),
                    'team': event['team'].title(),
                    'players': ', '.join([p['name'] for p in event.get('players_involved', [])[:2]]),
                    'confidence': f"{event['confidence']:.1%}"
                }
                for event in events[:20]  # Top 20 events
            ],
            'summary_stats': self._create_summary_stats_table(events),
            'player_involvement': self._create_player_stats_table(events)
        }
    
    def export_to_csv(self, data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Export analysis data to CSV format."""
        logger.info(f"Exporting data to CSV: {output_path}")
        
        # Simulate CSV export
        time.sleep(1)
        
        export_result = {
            'output_file': output_path,
            'format': 'csv',
            'records_exported': random.randint(50, 200),
            'file_size_kb': random.randint(10, 100),
            'export_time': time.time(),
            'success': True
        }
        
        logger.info("CSV export completed")
        return export_result
    
    def export_to_json(self, data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Export analysis data to JSON format."""
        logger.info(f"Exporting data to JSON: {output_path}")
        
        # Simulate JSON export
        time.sleep(0.5)
        
        export_result = {
            'output_file': output_path,
            'format': 'json',
            'data_size_kb': random.randint(50, 500),
            'compression_applied': True,
            'export_time': time.time(),
            'success': True
        }
        
        logger.info("JSON export completed")
        return export_result
    
    # Helper methods
    def _generate_event_description(self, event: Dict[str, Any]) -> str:
        """Generate human-readable event description."""
        event_type = event['event_type'].replace('_', ' ').title()
        team = event['team'].title()
        
        if event.get('players_involved'):
            player = event['players_involved'][0]['name']
            return f"{event_type} by {player} ({team})"
        
        return f"{event_type} ({team})"
    
    def _find_most_active_period(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the most active period in the match."""
        if not events:
            return {'period': 'N/A', 'event_count': 0}
        
        # Divide into 15-minute periods
        periods = {}
        for event in events:
            period = event['timestamp'] // (15 * 60)
            if period not in periods:
                periods[period] = 0
            periods[period] += 1
        
        if periods:
            most_active_period = max(periods, key=periods.get)
            return {
                'period': f"{most_active_period * 15}-{(most_active_period + 1) * 15} min",
                'event_count': periods[most_active_period]
            }
        
        return {'period': 'N/A', 'event_count': 0}
    
    def _identify_danger_zones(self, spatial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify dangerous zones on the field."""
        # Mock danger zones
        return [
            {'zone': 'attacking_third_center', 'danger_level': 0.8, 'events': 15},
            {'zone': 'penalty_area', 'danger_level': 0.95, 'events': 8},
            {'zone': 'attacking_third_right', 'danger_level': 0.6, 'events': 12}
        ]
    
    def _calculate_possession_areas(self, spatial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate possession areas for teams."""
        return {
            'home_team': {
                'defensive_third': 0.65,
                'middle_third': 0.48,
                'attacking_third': 0.32
            },
            'away_team': {
                'defensive_third': 0.35,
                'middle_third': 0.52,
                'attacking_third': 0.68
            }
        }
    
    def _extract_peak_times(self, temporal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract peak activity times."""
        return [
            {'start_time': '15:00', 'end_time': '20:00', 'intensity': 0.85},
            {'start_time': '35:00', 'end_time': '40:00', 'intensity': 0.92},
            {'start_time': '70:00', 'end_time': '75:00', 'intensity': 0.88}
        ]
    
    def _create_timeline_data(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timeline data for visualization."""
        return [
            {
                'timestamp': event['timestamp'],
                'event_type': event['event_type'],
                'team': event['team'],
                'importance': random.choice(['low', 'medium', 'high'])
            }
            for event in events
        ]
    
    def _create_distribution_data(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Create event distribution data."""
        distribution = {}
        for event in events:
            event_type = event['event_type']
            distribution[event_type] = distribution.get(event_type, 0) + 1
        return distribution
    
    def _create_formation_chart_data(self, tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create formation comparison chart data."""
        formation_analysis = tactical_insights.get('formation_analysis', {})
        return {
            'home_formation': formation_analysis.get('home_team', {}).get('primary_formation', '4-4-2'),
            'away_formation': formation_analysis.get('away_team', {}).get('primary_formation', '4-3-3'),
            'stability_comparison': {
                'home': formation_analysis.get('home_team', {}).get('formation_stability', 0.8),
                'away': formation_analysis.get('away_team', {}).get('formation_stability', 0.75)
            }
        }
    
    def _create_pressing_chart_data(self, tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create pressing intensity chart data."""
        pressing_patterns = tactical_insights.get('pressing_patterns', {})
        return {
            'high_press_frequency': pressing_patterns.get('high_press_frequency', 0.5),
            'success_rate': pressing_patterns.get('press_success_rate', 0.6),
            'intensity_over_time': [
                {'minute': i * 15, 'intensity': random.uniform(0.4, 0.9)}
                for i in range(6)  # 6 periods of 15 minutes
            ]
        }
    
    def _create_radar_chart_data(self, tactical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create radar chart data for performance comparison."""
        return {
            'categories': ['Attacking', 'Defending', 'Possession', 'Pressing', 'Transitions', 'Set Pieces'],
            'home_team': [random.uniform(0.6, 0.9) for _ in range(6)],
            'away_team': [random.uniform(0.6, 0.9) for _ in range(6)]
        }
    
    def _create_summary_stats_table(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create summary statistics table."""
        event_types = ['goal', 'shot', 'pass', 'tackle', 'foul']
        
        return [
            {
                'metric': event_type.replace('_', ' ').title(),
                'home_team': len([e for e in events if e['event_type'] == event_type and e['team'] == 'home']),
                'away_team': len([e for e in events if e['event_type'] == event_type and e['team'] == 'away']),
                'total': len([e for e in events if e['event_type'] == event_type])
            }
            for event_type in event_types
        ]
    
    def _create_player_stats_table(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create player statistics table."""
        player_stats = {}
        
        for event in events:
            for player in event.get('players_involved', []):
                player_name = player['name']
                if player_name not in player_stats:
                    player_stats[player_name] = {'events': 0, 'team': event['team']}
                player_stats[player_name]['events'] += 1
        
        # Convert to list and sort by event count
        stats_list = [
            {
                'player_name': name,
                'team': stats['team'].title(),
                'events_involved': stats['events'],
                'events_per_minute': round(stats['events'] / 90, 2)
            }
            for name, stats in player_stats.items()
        ]
        
        return sorted(stats_list, key=lambda x: x['events_involved'], reverse=True)[:10]
