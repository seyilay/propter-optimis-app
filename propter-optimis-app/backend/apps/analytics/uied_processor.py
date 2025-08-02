"""
UIED (Unified Intelligent Event Data) Format Processor.

This module implements the UIED format data processing pipeline for standardizing
multi-source football data as specified in the OpenStarLab integration requirements.

UIED format enables seamless integration of data from:
- StatsBomb, Wyscout, DataStadium
- GPS tracking data
- Video analysis outputs
- Manual scouting inputs
"""
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class UIEDEventType(Enum):
    """Standardized event types in UIED format."""
    PASS = "pass"
    SHOT = "shot"
    GOAL = "goal"
    TACKLE = "tackle"
    FOUL = "foul"
    OFFSIDE = "offside"
    CORNER_KICK = "corner_kick"
    THROW_IN = "throw_in"
    FREE_KICK = "free_kick"
    PENALTY = "penalty"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    DRIBBLE = "dribble"
    CLEARANCE = "clearance"
    INTERCEPTION = "interception"
    CROSS = "cross"
    HEADER = "header"
    SAVE = "save"
    BLOCK = "block"


class UIEDDataSource(Enum):
    """Supported data sources for UIED conversion."""
    STATSBOMB = "statsbomb"
    WYSCOUT = "wyscout"
    DATASTADIUM = "datastadium"
    GPS_TRACKING = "gps_tracking"
    VIDEO_ANALYSIS = "video_analysis"
    MANUAL_SCOUTING = "manual_scouting"
    OPENSTARLAB = "openstarlab"


@dataclass
class UIEDCoordinates:
    """Standardized coordinate system (0-100 scale)."""
    x: float  # 0 = left goal line, 100 = right goal line
    y: float  # 0 = bottom touchline, 100 = top touchline
    z: Optional[float] = None  # Height (for aerial events)
    
    def __post_init__(self):
        """Validate coordinate ranges."""
        self.x = max(0.0, min(100.0, self.x))
        self.y = max(0.0, min(100.0, self.y))
        if self.z is not None:
            self.z = max(0.0, min(50.0, self.z))  # 50m max height


@dataclass
class UIEDPlayer:
    """Standardized player representation."""
    player_id: str
    jersey_number: int
    position: str  # GK, CB, LB, RB, CDM, CM, CAM, LW, RW, CF, ST
    team: str  # 'home' or 'away'
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate player data."""
        if not self.player_id:
            self.player_id = f"player_{uuid.uuid4().hex[:8]}"
        
        valid_positions = {
            'GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 
            'LM', 'RM', 'LW', 'RW', 'CF', 'ST', 'SS'
        }
        if self.position not in valid_positions:
            self.position = 'CM'  # Default to center midfield


@dataclass
class UIEDEvent:
    """Standardized event representation in UIED format."""
    event_id: str
    timestamp: float  # Seconds from match start
    event_type: UIEDEventType
    coordinates: UIEDCoordinates
    players_involved: List[UIEDPlayer]
    team: str  # 'home' or 'away'
    
    # Optional metadata
    confidence: Optional[float] = None
    duration: Optional[float] = None  # Event duration in seconds
    outcome: Optional[str] = None  # 'success', 'failure', 'neutral'
    context: Optional[Dict[str, Any]] = None
    
    # Data provenance
    source: Optional[UIEDDataSource] = None
    source_confidence: Optional[float] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate and normalize event data."""
        if not self.event_id:
            self.event_id = f"event_{uuid.uuid4().hex[:8]}"
        
        if self.confidence is not None:
            self.confidence = max(0.0, min(1.0, self.confidence))
        
        if self.source_confidence is not None:
            self.source_confidence = max(0.0, min(1.0, self.source_confidence))
        
        if self.context is None:
            self.context = {}


@dataclass
class UIEDMatch:
    """Complete match data in UIED format."""
    match_id: str
    events: List[UIEDEvent]
    metadata: Dict[str, Any]
    
    # Match context
    home_team: str
    away_team: str
    competition: str
    season: str
    match_date: datetime
    
    # Processing information
    processing_timestamp: datetime
    data_sources: List[UIEDDataSource]
    quality_metrics: Dict[str, float]
    
    def __post_init__(self):
        """Validate match data."""
        if not self.match_id:
            self.match_id = f"match_{uuid.uuid4().hex[:8]}"
        
        # Sort events by timestamp
        self.events.sort(key=lambda e: e.timestamp)


class UIEDConverter:
    """
    Converter for transforming various data formats to UIED standard.
    
    Supports conversion from multiple data providers and formats while
    maintaining data integrity and traceability.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize UIED converter with configuration."""
        self.config = config or {}
        self.converter_version = "UIED-Converter-v2.0.0"
        self.field_dimensions = self.config.get('field_dimensions', {
            'length': 100,  # meters
            'width': 64,    # meters
            'coordinate_system': 'opta'  # Default coordinate system
        })
        
        logger.info(f"Initialized UIED converter v{self.converter_version}")
    
    def convert_to_uied(self, raw_data: Dict[str, Any], 
                       source: UIEDDataSource) -> UIEDMatch:
        """
        Convert raw data to UIED format.
        
        Args:
            raw_data: Raw data from various sources
            source: Data source type
            
        Returns:
            Standardized UIED match data
        """
        logger.info(f"Converting {source.value} data to UIED format")
        
        try:
            if source == UIEDDataSource.STATSBOMB:
                return self._convert_statsbomb_to_uied(raw_data)
            elif source == UIEDDataSource.WYSCOUT:
                return self._convert_wyscout_to_uied(raw_data)
            elif source == UIEDDataSource.DATASTADIUM:
                return self._convert_datastadium_to_uied(raw_data)
            elif source == UIEDDataSource.GPS_TRACKING:
                return self._convert_gps_to_uied(raw_data)
            elif source == UIEDDataSource.VIDEO_ANALYSIS:
                return self._convert_video_analysis_to_uied(raw_data)
            elif source == UIEDDataSource.MANUAL_SCOUTING:
                return self._convert_manual_scouting_to_uied(raw_data)
            elif source == UIEDDataSource.OPENSTARLAB:
                return self._convert_openstarlab_to_uied(raw_data)
            else:
                raise ValueError(f"Unsupported data source: {source}")
                
        except Exception as e:
            logger.error(f"UIED conversion failed for {source.value}: {str(e)}")
            raise
    
    def _convert_statsbomb_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert StatsBomb data to UIED format."""
        events = []
        
        # Extract match metadata
        match_info = raw_data.get('match_info', {})
        match_id = str(match_info.get('match_id', uuid.uuid4().hex[:8]))
        
        # Convert events
        raw_events = raw_data.get('events', [])
        
        for raw_event in raw_events:
            try:
                # Map StatsBomb event types to UIED
                event_type = self._map_statsbomb_event_type(raw_event.get('type', {}).get('name', ''))
                if not event_type:
                    continue
                
                # Extract coordinates
                location = raw_event.get('location', [50.0, 32.0])  # Default center field
                coordinates = UIEDCoordinates(
                    x=self._normalize_x_coordinate(location[0], 'statsbomb'),
                    y=self._normalize_y_coordinate(location[1], 'statsbomb')
                )
                
                # Extract players
                players_involved = []
                player_data = raw_event.get('player', {})
                if player_data:
                    player = UIEDPlayer(
                        player_id=str(player_data.get('id', '')),
                        jersey_number=player_data.get('jersey_number', 0),
                        position=self._normalize_position(raw_event.get('position', {}).get('name', 'CM')),
                        team='home' if raw_event.get('team', {}).get('name') == match_info.get('home_team', '') else 'away',
                        name=player_data.get('name', '')
                    )
                    players_involved.append(player)
                
                # Create UIED event
                uied_event = UIEDEvent(
                    event_id=str(raw_event.get('id', uuid.uuid4().hex[:8])),
                    timestamp=self._convert_timestamp(raw_event.get('timestamp', '0:00.000')),
                    event_type=event_type,
                    coordinates=coordinates,
                    players_involved=players_involved,
                    team='home' if raw_event.get('team', {}).get('name') == match_info.get('home_team', '') else 'away',
                    confidence=0.95,  # StatsBomb has high confidence
                    outcome=self._determine_outcome(raw_event),
                    context=self._extract_statsbomb_context(raw_event),
                    source=UIEDDataSource.STATSBOMB,
                    source_confidence=0.95,
                    processing_metadata={
                        'original_event_type': raw_event.get('type', {}).get('name', ''),
                        'conversion_timestamp': datetime.now().isoformat()
                    }
                )
                
                events.append(uied_event)
                
            except Exception as e:
                logger.warning(f"Failed to convert StatsBomb event: {str(e)}")
                continue
        
        # Create UIED match
        uied_match = UIEDMatch(
            match_id=match_id,
            events=events,
            metadata=self._extract_statsbomb_metadata(raw_data),
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition=match_info.get('competition', 'Unknown'),
            season=match_info.get('season', '2023-24'),
            match_date=self._parse_match_date(match_info.get('match_date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.STATSBOMB],
            quality_metrics=self._calculate_statsbomb_quality_metrics(raw_data)
        )
        
        logger.info(f"Converted {len(events)} StatsBomb events to UIED format")
        return uied_match
    
    def _convert_wyscout_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert Wyscout data to UIED format."""
        events = []
        
        # Extract match metadata
        match_info = raw_data.get('match', {})
        match_id = str(match_info.get('wyId', uuid.uuid4().hex[:8]))
        
        # Convert events
        raw_events = raw_data.get('events', [])
        
        for raw_event in raw_events:
            try:
                # Map Wyscout event types to UIED
                event_type = self._map_wyscout_event_type(raw_event.get('eventName', ''))
                if not event_type:
                    continue
                
                # Extract coordinates
                positions = raw_event.get('positions', [{}])
                position = positions[0] if positions else {}
                coordinates = UIEDCoordinates(
                    x=self._normalize_x_coordinate(position.get('x', 50.0), 'wyscout'),
                    y=self._normalize_y_coordinate(position.get('y', 50.0), 'wyscout')
                )
                
                # Extract players
                players_involved = []
                player_data = raw_event.get('player', {})
                if player_data:
                    player = UIEDPlayer(
                        player_id=str(player_data.get('wyId', '')),
                        jersey_number=player_data.get('shirtNumber', 0),
                        position=self._normalize_position(player_data.get('role', {}).get('name', 'CM')),
                        team='home' if raw_event.get('team', {}).get('name') == match_info.get('label', '').split(' - ')[0] else 'away',
                        name=player_data.get('name', '')
                    )
                    players_involved.append(player)
                
                # Create UIED event
                uied_event = UIEDEvent(
                    event_id=str(raw_event.get('id', uuid.uuid4().hex[:8])),
                    timestamp=raw_event.get('eventSec', 0.0),
                    event_type=event_type,
                    coordinates=coordinates,
                    players_involved=players_involved,
                    team='home' if raw_event.get('team', {}).get('name') == match_info.get('label', '').split(' - ')[0] else 'away',
                    confidence=0.90,  # Wyscout has good confidence
                    outcome=self._determine_wyscout_outcome(raw_event),
                    context=self._extract_wyscout_context(raw_event),
                    source=UIEDDataSource.WYSCOUT,
                    source_confidence=0.90,
                    processing_metadata={
                        'original_event_name': raw_event.get('eventName', ''),
                        'conversion_timestamp': datetime.now().isoformat()
                    }
                )
                
                events.append(uied_event)
                
            except Exception as e:
                logger.warning(f"Failed to convert Wyscout event: {str(e)}")
                continue
        
        # Create UIED match
        uied_match = UIEDMatch(
            match_id=match_id,
            events=events,
            metadata=self._extract_wyscout_metadata(raw_data),
            home_team=match_info.get('label', 'Home - Away').split(' - ')[0],
            away_team=match_info.get('label', 'Home - Away').split(' - ')[-1],
            competition=raw_data.get('competition', {}).get('name', 'Unknown'),
            season=raw_data.get('season', {}).get('name', '2023-24'),
            match_date=self._parse_match_date(match_info.get('date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.WYSCOUT],
            quality_metrics=self._calculate_wyscout_quality_metrics(raw_data)
        )
        
        logger.info(f"Converted {len(events)} Wyscout events to UIED format")
        return uied_match
    
    def _convert_datastadium_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert DataStadium data to UIED format."""
        # Implementation for DataStadium format conversion
        # This would follow similar pattern to StatsBomb/Wyscout
        
        events = []
        match_info = raw_data.get('game', {})
        
        # Simulate DataStadium conversion
        for i, raw_event in enumerate(raw_data.get('events', [])):
            event_type = self._map_datastadium_event_type(raw_event.get('type', ''))
            if event_type:
                coordinates = UIEDCoordinates(
                    x=raw_event.get('x', 50.0),
                    y=raw_event.get('y', 50.0)
                )
                
                uied_event = UIEDEvent(
                    event_id=f"ds_event_{i:04d}",
                    timestamp=raw_event.get('time_seconds', 0.0),
                    event_type=event_type,
                    coordinates=coordinates,
                    players_involved=[],  # Would extract from raw_event
                    team=raw_event.get('team', 'home'),
                    confidence=0.85,
                    source=UIEDDataSource.DATASTADIUM,
                    source_confidence=0.85
                )
                events.append(uied_event)
        
        uied_match = UIEDMatch(
            match_id=str(match_info.get('id', uuid.uuid4().hex[:8])),
            events=events,
            metadata={},
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition='Unknown',
            season='2023-24',
            match_date=datetime.now(),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.DATASTADIUM],
            quality_metrics={'completeness': 0.85, 'accuracy': 0.85}
        )
        
        return uied_match
    
    def _convert_gps_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert GPS tracking data to UIED format."""
        events = []
        
        # GPS data typically contains positional information
        # Convert to movement and positioning events
        tracking_data = raw_data.get('tracking_data', [])
        
        for i, frame in enumerate(tracking_data[::25]):  # Sample every 25 frames (1 second)
            for player_data in frame.get('players', []):
                # Create positioning events from GPS data
                coordinates = UIEDCoordinates(
                    x=self._normalize_x_coordinate(player_data.get('x', 50.0), 'gps'),
                    y=self._normalize_y_coordinate(player_data.get('y', 50.0), 'gps')
                )
                
                player = UIEDPlayer(
                    player_id=str(player_data.get('player_id', '')),
                    jersey_number=player_data.get('jersey_number', 0),
                    position=player_data.get('position', 'CM'),
                    team=player_data.get('team', 'home')
                )
                
                # Only create events for significant movements or actions
                if player_data.get('speed', 0) > 5.0:  # Moving at >5 m/s
                    uied_event = UIEDEvent(
                        event_id=f"gps_movement_{i:04d}_{player.player_id}",
                        timestamp=frame.get('timestamp', 0.0),
                        event_type=UIEDEventType.DRIBBLE,  # Approximate high-speed movement as dribble
                        coordinates=coordinates,
                        players_involved=[player],
                        team=player.team,
                        confidence=0.70,  # GPS inference has lower confidence
                        context={
                            'speed': player_data.get('speed', 0),
                            'acceleration': player_data.get('acceleration', 0),
                            'distance_covered': player_data.get('distance_covered', 0)
                        },
                        source=UIEDDataSource.GPS_TRACKING,
                        source_confidence=0.95  # GPS coordinates are very accurate
                    )
                    events.append(uied_event)
        
        match_info = raw_data.get('match_info', {})
        uied_match = UIEDMatch(
            match_id=str(match_info.get('match_id', uuid.uuid4().hex[:8])),
            events=events,
            metadata=raw_data.get('metadata', {}),
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition=match_info.get('competition', 'Training'),
            season=match_info.get('season', '2023-24'),
            match_date=self._parse_match_date(match_info.get('date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.GPS_TRACKING],
            quality_metrics={'positional_accuracy': 0.95, 'event_inference_accuracy': 0.70}
        )
        
        return uied_match
    
    def _convert_video_analysis_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert video analysis results to UIED format."""
        events = []
        
        # Convert detected events from video analysis
        detected_events = raw_data.get('detected_events', [])
        
        for raw_event in detected_events:
            event_type = self._map_video_analysis_event_type(raw_event.get('event_type', ''))
            if event_type:
                coordinates = UIEDCoordinates(
                    x=raw_event.get('coordinates', {}).get('x', 50.0),
                    y=raw_event.get('coordinates', {}).get('y', 50.0)
                )
                
                players_involved = []
                for player_data in raw_event.get('players_involved', []):
                    player = UIEDPlayer(
                        player_id=player_data.get('player_id', ''),
                        jersey_number=player_data.get('jersey_number', 0),
                        position=player_data.get('position', 'CM'),
                        team=player_data.get('team', 'home'),
                        name=player_data.get('name', '')
                    )
                    players_involved.append(player)
                
                uied_event = UIEDEvent(
                    event_id=raw_event.get('id', f"video_event_{uuid.uuid4().hex[:8]}"),
                    timestamp=raw_event.get('timestamp', 0.0),
                    event_type=event_type,
                    coordinates=coordinates,
                    players_involved=players_involved,
                    team=raw_event.get('team', 'home'),
                    confidence=raw_event.get('confidence', 0.75),
                    context=raw_event.get('context', {}),
                    source=UIEDDataSource.VIDEO_ANALYSIS,
                    source_confidence=raw_event.get('confidence', 0.75),
                    processing_metadata={
                        'detection_model': raw_event.get('detection_model', 'unknown'),
                        'frame_number': raw_event.get('frame_number', 0)
                    }
                )
                events.append(uied_event)
        
        match_info = raw_data.get('match_info', {})
        uied_match = UIEDMatch(
            match_id=str(match_info.get('match_id', uuid.uuid4().hex[:8])),
            events=events,
            metadata=raw_data.get('metadata', {}),
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition=match_info.get('competition', 'Unknown'),
            season=match_info.get('season', '2023-24'),
            match_date=self._parse_match_date(match_info.get('date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.VIDEO_ANALYSIS],
            quality_metrics={
                'detection_accuracy': np.mean([e.confidence for e in events]) if events else 0.0,
                'temporal_resolution': raw_data.get('frame_rate', 25)
            }
        )
        
        return uied_match
    
    def _convert_manual_scouting_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert manual scouting data to UIED format."""
        events = []
        
        # Convert scouting observations to events
        observations = raw_data.get('observations', [])
        
        for obs in observations:
            event_type = self._map_scouting_observation_type(obs.get('type', ''))
            if event_type:
                coordinates = UIEDCoordinates(
                    x=obs.get('field_position', {}).get('x', 50.0),
                    y=obs.get('field_position', {}).get('y', 50.0)
                )
                
                players_involved = []
                if obs.get('player'):
                    player = UIEDPlayer(
                        player_id=obs['player'].get('id', ''),
                        jersey_number=obs['player'].get('number', 0),
                        position=obs['player'].get('position', 'CM'),
                        team=obs['player'].get('team', 'home'),
                        name=obs['player'].get('name', '')
                    )
                    players_involved.append(player)
                
                uied_event = UIEDEvent(
                    event_id=f"scout_obs_{uuid.uuid4().hex[:8]}",
                    timestamp=obs.get('minute', 0) * 60 + obs.get('second', 0),
                    event_type=event_type,
                    coordinates=coordinates,
                    players_involved=players_involved,
                    team=obs.get('team', 'home'),
                    confidence=0.90,  # Manual scouting has high confidence
                    context={
                        'scout_notes': obs.get('notes', ''),
                        'importance_rating': obs.get('importance', 'medium'),
                        'quality_rating': obs.get('quality', 'good')
                    },
                    source=UIEDDataSource.MANUAL_SCOUTING,
                    source_confidence=0.90,
                    processing_metadata={
                        'scout_id': obs.get('scout_id', ''),
                        'observation_type': obs.get('type', '')
                    }
                )
                events.append(uied_event)
        
        match_info = raw_data.get('match_info', {})
        uied_match = UIEDMatch(
            match_id=str(match_info.get('match_id', uuid.uuid4().hex[:8])),
            events=events,
            metadata=raw_data.get('metadata', {}),
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition=match_info.get('competition', 'Unknown'),
            season=match_info.get('season', '2023-24'),
            match_date=self._parse_match_date(match_info.get('date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.MANUAL_SCOUTING],
            quality_metrics={
                'human_accuracy': 0.90,
                'completeness': len(events) / 100,  # Assume 100 expected observations
                'subjectivity_factor': 0.15
            }
        )
        
        return uied_match
    
    def _convert_openstarlab_to_uied(self, raw_data: Dict[str, Any]) -> UIEDMatch:
        """Convert OpenStarLab processed data to UIED format."""
        events = []
        
        # OpenStarLab data is already well-structured
        openstarlab_events = raw_data.get('events', [])
        
        for raw_event in openstarlab_events:
            # Map event type
            event_type_str = raw_event.get('event_type', '')
            try:
                event_type = UIEDEventType(event_type_str.lower())
            except ValueError:
                continue
            
            coordinates = UIEDCoordinates(
                x=raw_event.get('coordinates', {}).get('x', 50.0),
                y=raw_event.get('coordinates', {}).get('y', 50.0),
                z=raw_event.get('coordinates', {}).get('z')
            )
            
            players_involved = []
            for player_data in raw_event.get('players_involved', []):
                player = UIEDPlayer(
                    player_id=player_data.get('player_id', ''),
                    jersey_number=player_data.get('jersey_number', 0),
                    position=player_data.get('position', 'CM'),
                    team=player_data.get('team', 'home'),
                    name=player_data.get('name', '')
                )
                players_involved.append(player)
            
            uied_event = UIEDEvent(
                event_id=raw_event.get('id', f"osl_event_{uuid.uuid4().hex[:8]}"),
                timestamp=raw_event.get('timestamp', 0.0),
                event_type=event_type,
                coordinates=coordinates,
                players_involved=players_involved,
                team=raw_event.get('team', 'home'),
                confidence=raw_event.get('confidence', 0.85),
                outcome=raw_event.get('outcome'),
                context=raw_event.get('contextual_features', {}),
                source=UIEDDataSource.OPENSTARLAB,
                source_confidence=raw_event.get('accuracy_score', 0.85),
                processing_metadata=raw_event.get('processing_metadata', {})
            )
            events.append(uied_event)
        
        match_info = raw_data.get('match_info', {})
        uied_match = UIEDMatch(
            match_id=str(match_info.get('match_id', uuid.uuid4().hex[:8])),
            events=events,
            metadata=raw_data.get('metadata', {}),
            home_team=match_info.get('home_team', 'Home'),
            away_team=match_info.get('away_team', 'Away'),
            competition=match_info.get('competition', 'Unknown'),
            season=match_info.get('season', '2023-24'),
            match_date=self._parse_match_date(match_info.get('date')),
            processing_timestamp=datetime.now(),
            data_sources=[UIEDDataSource.OPENSTARLAB],
            quality_metrics=raw_data.get('quality_metrics', {
                'processing_accuracy': 0.85,
                'event_completeness': 0.90
            })
        )
        
        return uied_match
    
    def merge_uied_data(self, uied_matches: List[UIEDMatch]) -> UIEDMatch:
        """
        Merge multiple UIED datasets from different sources.
        
        Args:
            uied_matches: List of UIED match data from different sources
            
        Returns:
            Merged UIED match with combined intelligence
        """
        if not uied_matches:
            raise ValueError("No UIED matches provided for merging")
        
        if len(uied_matches) == 1:
            return uied_matches[0]
        
        logger.info(f"Merging {len(uied_matches)} UIED datasets")
        
        # Use first match as base
        base_match = uied_matches[0]
        merged_events = list(base_match.events)
        merged_sources = list(base_match.data_sources)
        merged_quality_metrics = dict(base_match.quality_metrics)
        
        # Merge events from other sources
        for match in uied_matches[1:]:
            # Add events from this source
            merged_events.extend(match.events)
            
            # Merge data sources
            for source in match.data_sources:
                if source not in merged_sources:
                    merged_sources.append(source)
            
            # Merge quality metrics
            for metric, value in match.quality_metrics.items():
                if metric in merged_quality_metrics:
                    # Average the metric values
                    merged_quality_metrics[metric] = (merged_quality_metrics[metric] + value) / 2
                else:
                    merged_quality_metrics[metric] = value
        
        # Remove duplicate events (same timestamp and type)
        merged_events = self._deduplicate_events(merged_events)
        
        # Create merged match
        merged_match = UIEDMatch(
            match_id=base_match.match_id,
            events=merged_events,
            metadata={
                **base_match.metadata,
                'merged_sources': len(uied_matches),
                'merge_timestamp': datetime.now().isoformat()
            },
            home_team=base_match.home_team,
            away_team=base_match.away_team,
            competition=base_match.competition,
            season=base_match.season,
            match_date=base_match.match_date,
            processing_timestamp=datetime.now(),
            data_sources=merged_sources,
            quality_metrics=merged_quality_metrics
        )
        
        logger.info(f"Merged UIED data: {len(merged_events)} events from {len(merged_sources)} sources")
        return merged_match
    
    def _deduplicate_events(self, events: List[UIEDEvent]) -> List[UIEDEvent]:
        """Remove duplicate events based on timestamp and type similarity."""
        deduplicated = []
        time_threshold = 2.0  # 2 second window for considering events as duplicates
        
        events_sorted = sorted(events, key=lambda e: e.timestamp)
        
        for event in events_sorted:
            is_duplicate = False
            
            for existing_event in deduplicated:
                # Check if events are similar (same type, similar time, similar location)
                time_diff = abs(event.timestamp - existing_event.timestamp)
                location_diff = abs(event.coordinates.x - existing_event.coordinates.x) + \
                               abs(event.coordinates.y - existing_event.coordinates.y)
                
                if (event.event_type == existing_event.event_type and 
                    time_diff <= time_threshold and 
                    location_diff <= 10.0):  # Within 10 units of field position
                    
                    # Keep the event with higher confidence
                    if event.confidence and existing_event.confidence:
                        if event.confidence > existing_event.confidence:
                            # Replace existing event
                            deduplicated[deduplicated.index(existing_event)] = event
                    
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(event)
        
        return deduplicated
    
    def export_uied_json(self, uied_match: UIEDMatch) -> str:
        """Export UIED match data to JSON format."""
        
        def convert_to_dict(obj):
            """Convert dataclass objects to dictionaries."""
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [convert_to_dict(item) for item in value]
                    elif isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, datetime):
                        result[key] = value.isoformat()
                    elif hasattr(value, '__dict__'):
                        result[key] = convert_to_dict(value)
                    else:
                        result[key] = value
                return result
            return obj
        
        uied_dict = convert_to_dict(uied_match)
        return json.dumps(uied_dict, indent=2, ensure_ascii=False)
    
    # Helper methods for event type mapping and normalization
    
    def _map_statsbomb_event_type(self, event_name: str) -> Optional[UIEDEventType]:
        """Map StatsBomb event names to UIED event types."""
        mapping = {
            'Pass': UIEDEventType.PASS,
            'Shot': UIEDEventType.SHOT,
            'Goal': UIEDEventType.GOAL,
            'Duel': UIEDEventType.TACKLE,
            'Foul Committed': UIEDEventType.FOUL,
            'Offside': UIEDEventType.OFFSIDE,
            'Corner': UIEDEventType.CORNER_KICK,
            'Throw-in': UIEDEventType.THROW_IN,
            'Free Kick': UIEDEventType.FREE_KICK,
            'Penalty': UIEDEventType.PENALTY,
            'Yellow Card': UIEDEventType.YELLOW_CARD,
            'Red Card': UIEDEventType.RED_CARD,
            'Substitution': UIEDEventType.SUBSTITUTION,
            'Dribble': UIEDEventType.DRIBBLE,
            'Clearance': UIEDEventType.CLEARANCE,
            'Interception': UIEDEventType.INTERCEPTION,
            'Cross': UIEDEventType.CROSS,
            'Header': UIEDEventType.HEADER,
            'Save': UIEDEventType.SAVE,
            'Block': UIEDEventType.BLOCK
        }
        return mapping.get(event_name)
    
    def _map_wyscout_event_type(self, event_name: str) -> Optional[UIEDEventType]:
        """Map Wyscout event names to UIED event types."""
        mapping = {
            'Simple pass': UIEDEventType.PASS,
            'High pass': UIEDEventType.PASS,
            'Shot': UIEDEventType.SHOT,
            'Goal': UIEDEventType.GOAL,
            'Tackle': UIEDEventType.TACKLE,
            'Foul': UIEDEventType.FOUL,
            'Offside': UIEDEventType.OFFSIDE,
            'Corner': UIEDEventType.CORNER_KICK,
            'Throw in': UIEDEventType.THROW_IN,
            'Free kick': UIEDEventType.FREE_KICK,
            'Penalty': UIEDEventType.PENALTY,
            'Yellow card': UIEDEventType.YELLOW_CARD,
            'Red card': UIEDEventType.RED_CARD,
            'Substitution': UIEDEventType.SUBSTITUTION,
            'Dribble': UIEDEventType.DRIBBLE,
            'Clearance': UIEDEventType.CLEARANCE,
            'Interception': UIEDEventType.INTERCEPTION,
            'Cross': UIEDEventType.CROSS,
            'Head': UIEDEventType.HEADER,
            'Save attempt': UIEDEventType.SAVE
        }
        return mapping.get(event_name)
    
    def _map_datastadium_event_type(self, event_name: str) -> Optional[UIEDEventType]:
        """Map DataStadium event names to UIED event types."""
        # DataStadium specific mapping would go here
        return None
    
    def _map_video_analysis_event_type(self, event_name: str) -> Optional[UIEDEventType]:
        """Map video analysis event types to UIED."""
        try:
            return UIEDEventType(event_name.lower())
        except ValueError:
            return None
    
    def _map_scouting_observation_type(self, obs_type: str) -> Optional[UIEDEventType]:
        """Map scouting observation types to UIED events."""
        mapping = {
            'good_pass': UIEDEventType.PASS,
            'shot_attempt': UIEDEventType.SHOT,
            'successful_tackle': UIEDEventType.TACKLE,
            'foul_committed': UIEDEventType.FOUL,
            'skillful_dribble': UIEDEventType.DRIBBLE,
            'key_interception': UIEDEventType.INTERCEPTION,
            'important_clearance': UIEDEventType.CLEARANCE
        }
        return mapping.get(obs_type)
    
    def _normalize_x_coordinate(self, x: float, source: str) -> float:
        """Normalize X coordinate to 0-100 scale."""
        if source == 'statsbomb':
            return max(0.0, min(100.0, (x / 120.0) * 100))  # StatsBomb uses 120x80 field
        elif source == 'wyscout':
            return max(0.0, min(100.0, x))  # Wyscout already uses 0-100
        elif source == 'gps':
            return max(0.0, min(100.0, (x / self.field_dimensions['length']) * 100))
        else:
            return max(0.0, min(100.0, x))
    
    def _normalize_y_coordinate(self, y: float, source: str) -> float:
        """Normalize Y coordinate to 0-100 scale."""
        if source == 'statsbomb':
            return max(0.0, min(100.0, (y / 80.0) * 100))  # StatsBomb uses 120x80 field
        elif source == 'wyscout':
            return max(0.0, min(100.0, y))  # Wyscout already uses 0-100
        elif source == 'gps':
            return max(0.0, min(100.0, (y / self.field_dimensions['width']) * 100))
        else:
            return max(0.0, min(100.0, y))
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position names to standard format."""
        position_mapping = {
            'Goalkeeper': 'GK',
            'Left Center Back': 'CB',
            'Right Center Back': 'CB',
            'Center Back': 'CB',
            'Left Back': 'LB',
            'Right Back': 'RB',
            'Left Wing Back': 'LWB',
            'Right Wing Back': 'RWB',
            'Center Defensive Midfield': 'CDM',
            'Center Midfield': 'CM',
            'Left Center Midfield': 'CM',
            'Right Center Midfield': 'CM',
            'Center Attacking Midfield': 'CAM',
            'Left Midfield': 'LM',
            'Right Midfield': 'RM',
            'Left Wing': 'LW',
            'Right Wing': 'RW',
            'Center Forward': 'CF',
            'Striker': 'ST',
            'Second Striker': 'SS'
        }
        return position_mapping.get(position, position)
    
    def _convert_timestamp(self, timestamp_str: str) -> float:
        """Convert timestamp string to seconds."""
        try:
            if ':' in timestamp_str:
                parts = timestamp_str.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(timestamp_str)
        except (ValueError, IndexError):
            return 0.0
    
    def _parse_match_date(self, date_str: Union[str, None]) -> datetime:
        """Parse match date string to datetime object."""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.now()
    
    def _determine_outcome(self, raw_event: Dict[str, Any]) -> Optional[str]:
        """Determine event outcome from raw event data."""
        # Logic to determine if event was successful, failed, or neutral
        if 'outcome' in raw_event:
            outcome_data = raw_event['outcome']
            if outcome_data.get('name') == 'Complete':
                return 'success'
            elif outcome_data.get('name') in ['Incomplete', 'Out']:
                return 'failure'
        return 'neutral'
    
    def _determine_wyscout_outcome(self, raw_event: Dict[str, Any]) -> Optional[str]:
        """Determine Wyscout event outcome."""
        tags = raw_event.get('tags', [])
        for tag in tags:
            if tag.get('id') == 1801:  # Accurate pass
                return 'success'
            elif tag.get('id') == 1802:  # Inaccurate pass
                return 'failure'
        return 'neutral'
    
    def _extract_statsbomb_context(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context information from StatsBomb event."""
        context = {}
        
        if 'under_pressure' in raw_event:
            context['under_pressure'] = raw_event['under_pressure']
        
        if 'possession' in raw_event:
            context['possession'] = raw_event['possession']
        
        if 'possession_team' in raw_event:
            context['possession_team'] = raw_event['possession_team']['name']
        
        return context
    
    def _extract_wyscout_context(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context information from Wyscout event."""
        context = {}
        
        tags = raw_event.get('tags', [])
        context['tags'] = [tag.get('id') for tag in tags]
        
        if 'matchPeriod' in raw_event:
            context['match_period'] = raw_event['matchPeriod']
        
        return context
    
    def _extract_statsbomb_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from StatsBomb data."""
        return {
            'data_version': raw_data.get('data_version', '1.0'),
            'last_updated': raw_data.get('last_updated', ''),
            'competition_stage': raw_data.get('competition_stage', {}),
            'shot_fidelity_version': raw_data.get('shot_fidelity_version', ''),
            'xy_fidelity_version': raw_data.get('xy_fidelity_version', '')
        }
    
    def _extract_wyscout_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from Wyscout data."""
        return {
            'data_version': '2.0',
            'competition_format': raw_data.get('competition', {}).get('format', ''),
            'season_name': raw_data.get('season', {}).get('name', ''),
            'round_name': raw_data.get('round', {}).get('name', '')
        }
    
    def _calculate_statsbomb_quality_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for StatsBomb data."""
        events = raw_data.get('events', [])
        
        return {
            'completeness': 1.0,  # StatsBomb is typically complete
            'accuracy': 0.95,     # High accuracy for StatsBomb
            'temporal_resolution': 0.1,  # Sub-second precision
            'spatial_resolution': 0.5,   # Half-meter precision
            'event_count': len(events)
        }
    
    def _calculate_wyscout_quality_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for Wyscout data."""
        events = raw_data.get('events', [])
        
        return {
            'completeness': 0.95,  # Very complete
            'accuracy': 0.90,      # Good accuracy
            'temporal_resolution': 1.0,   # Second precision
            'spatial_resolution': 1.0,    # Meter precision
            'event_count': len(events)
        }


class UIEDAnalyzer:
    """
    Analyzer for UIED format data to extract insights and quality metrics.
    
    Provides analysis capabilities for unified event data to support
    intelligence processing and quality assessment.
    """
    
    def __init__(self):
        """Initialize UIED analyzer."""
        self.analyzer_version = "UIED-Analyzer-v1.0.0"
        logger.info("Initialized UIED analyzer")
    
    def analyze_uied_quality(self, uied_match: UIEDMatch) -> Dict[str, Any]:
        """
        Analyze the quality of UIED data.
        
        Args:
            uied_match: UIED match data to analyze
            
        Returns:
            Quality analysis results
        """
        events = uied_match.events
        
        quality_analysis = {
            'event_count': len(events),
            'temporal_coverage': self._analyze_temporal_coverage(events),
            'spatial_coverage': self._analyze_spatial_coverage(events),
            'event_type_distribution': self._analyze_event_distribution(events),
            'confidence_metrics': self._analyze_confidence_metrics(events),
            'data_source_coverage': self._analyze_data_sources(uied_match),
            'completeness_score': self._calculate_completeness_score(events),
            'consistency_score': self._calculate_consistency_score(events),
            'overall_quality_score': 0.0
        }
        
        # Calculate overall quality score
        quality_factors = [
            quality_analysis['completeness_score'],
            quality_analysis['consistency_score'],
            min(1.0, len(events) / 100),  # Event density factor
            np.mean([e.confidence for e in events if e.confidence]) if events else 0.0
        ]
        
        quality_analysis['overall_quality_score'] = np.mean(quality_factors)
        
        return quality_analysis
    
    def _analyze_temporal_coverage(self, events: List[UIEDEvent]) -> Dict[str, float]:
        """Analyze temporal coverage of events."""
        if not events:
            return {'coverage_percentage': 0.0, 'event_density': 0.0}
        
        match_duration = 90 * 60  # 90 minutes in seconds
        timestamps = [e.timestamp for e in events]
        
        # Calculate coverage (percentage of match with events)
        time_bins = np.arange(0, match_duration, 60)  # 1-minute bins
        event_bins = np.histogram(timestamps, bins=time_bins)[0]
        coverage_percentage = np.sum(event_bins > 0) / len(time_bins)
        
        # Calculate event density (events per minute)
        event_density = len(events) / (match_duration / 60)
        
        return {
            'coverage_percentage': coverage_percentage,
            'event_density': event_density,
            'temporal_gaps': self._identify_temporal_gaps(timestamps)
        }
    
    def _analyze_spatial_coverage(self, events: List[UIEDEvent]) -> Dict[str, float]:
        """Analyze spatial coverage of events."""
        if not events:
            return {'field_coverage': 0.0}
        
        # Divide field into grid and check coverage
        grid_size = 10
        x_bins = np.linspace(0, 100, grid_size)
        y_bins = np.linspace(0, 100, grid_size)
        
        x_coords = [e.coordinates.x for e in events]
        y_coords = [e.coordinates.y for e in events]
        
        spatial_histogram = np.histogram2d(x_coords, y_coords, bins=[x_bins, y_bins])[0]
        field_coverage = np.sum(spatial_histogram > 0) / (grid_size * grid_size)
        
        return {
            'field_coverage': field_coverage,
            'spatial_distribution': {
                'mean_x': np.mean(x_coords),
                'mean_y': np.mean(y_coords),
                'std_x': np.std(x_coords),
                'std_y': np.std(y_coords)
            }
        }
    
    def _analyze_event_distribution(self, events: List[UIEDEvent]) -> Dict[str, int]:
        """Analyze distribution of event types."""
        event_counts = {}
        
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return event_counts
    
    def _analyze_confidence_metrics(self, events: List[UIEDEvent]) -> Dict[str, float]:
        """Analyze confidence metrics across events."""
        confidences = [e.confidence for e in events if e.confidence is not None]
        
        if not confidences:
            return {'mean_confidence': 0.0, 'min_confidence': 0.0, 'low_confidence_events': 0}
        
        return {
            'mean_confidence': np.mean(confidences),
            'std_confidence': np.std(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'low_confidence_events': len([c for c in confidences if c < 0.5])
        }
    
    def _analyze_data_sources(self, uied_match: UIEDMatch) -> Dict[str, Any]:
        """Analyze data source coverage and distribution."""
        source_distribution = {}
        
        for event in uied_match.events:
            if event.source:
                source = event.source.value
                source_distribution[source] = source_distribution.get(source, 0) + 1
        
        return {
            'sources_used': len(uied_match.data_sources),
            'source_distribution': source_distribution,
            'multi_source_coverage': len(uied_match.data_sources) > 1
        }
    
    def _calculate_completeness_score(self, events: List[UIEDEvent]) -> float:
        """Calculate completeness score based on expected event counts."""
        if not events:
            return 0.0
        
        # Expected event counts for a typical 90-minute match
        expected_events = {
            'pass': 500,
            'shot': 20,
            'tackle': 30,
            'foul': 25,
            'throw_in': 15,
            'corner_kick': 8,
            'free_kick': 12
        }
        
        actual_counts = {}
        for event in events:
            event_type = event.event_type.value
            actual_counts[event_type] = actual_counts.get(event_type, 0) + 1
        
        completeness_scores = []
        for event_type, expected_count in expected_events.items():
            actual_count = actual_counts.get(event_type, 0)
            completeness_scores.append(min(1.0, actual_count / expected_count))
        
        return np.mean(completeness_scores)
    
    def _calculate_consistency_score(self, events: List[UIEDEvent]) -> float:
        """Calculate consistency score based on event patterns."""
        if len(events) < 10:
            return 0.5
        
        # Check temporal consistency (events should be reasonably spaced)
        timestamps = sorted([e.timestamp for e in events])
        time_diffs = np.diff(timestamps)
        
        # Check for unrealistic time gaps (>5 minutes with no events)
        large_gaps = len([diff for diff in time_diffs if diff > 300])
        gap_penalty = large_gaps / len(time_diffs)
        
        # Check spatial consistency (events shouldn't jump erratically)
        spatial_consistency = self._calculate_spatial_consistency(events)
        
        # Check confidence consistency
        confidences = [e.confidence for e in events if e.confidence is not None]
        confidence_consistency = 1.0 - np.std(confidences) if confidences else 0.5
        
        consistency_score = np.mean([
            1.0 - gap_penalty,
            spatial_consistency,
            confidence_consistency
        ])
        
        return max(0.0, min(1.0, consistency_score))
    
    def _calculate_spatial_consistency(self, events: List[UIEDEvent]) -> float:
        """Calculate spatial consistency of events."""
        if len(events) < 5:
            return 0.5
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Calculate spatial jumps between consecutive events
        spatial_jumps = []
        for i in range(1, len(sorted_events)):
            prev_event = sorted_events[i-1]
            curr_event = sorted_events[i]
            
            # Calculate Euclidean distance
            distance = np.sqrt(
                (curr_event.coordinates.x - prev_event.coordinates.x)**2 +
                (curr_event.coordinates.y - prev_event.coordinates.y)**2
            )
            spatial_jumps.append(distance)
        
        # Penalize very large spatial jumps (>50 field units in short time)
        large_jumps = 0
        for i, jump in enumerate(spatial_jumps):
            if i < len(sorted_events) - 1:
                time_diff = sorted_events[i+1].timestamp - sorted_events[i].timestamp
                if jump > 50 and time_diff < 5:  # Large jump in <5 seconds
                    large_jumps += 1
        
        jump_penalty = large_jumps / len(spatial_jumps) if spatial_jumps else 0
        return max(0.0, 1.0 - jump_penalty)
    
    def _identify_temporal_gaps(self, timestamps: List[float]) -> List[Dict[str, float]]:
        """Identify significant temporal gaps in event coverage."""
        if len(timestamps) < 2:
            return []
        
        sorted_timestamps = sorted(timestamps)
        gaps = []
        
        for i in range(1, len(sorted_timestamps)):
            gap_duration = sorted_timestamps[i] - sorted_timestamps[i-1]
            if gap_duration > 300:  # Gaps longer than 5 minutes
                gaps.append({
                    'start_time': sorted_timestamps[i-1],
                    'end_time': sorted_timestamps[i],
                    'duration': gap_duration
                })
        
        return gaps