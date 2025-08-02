"""
Configuration settings for OpenStarLab Intelligence Processing.

This module contains configuration settings for all OpenStarLab processors
and intelligence components as specified in the platform requirements.
"""
from typing import Dict, Any, List
import os
from django.conf import settings


class OpenStarLabConfig:
    """Configuration class for OpenStarLab intelligence processing."""
    
    # Model Versions and Configurations
    LEM3_CONFIG = {
        'model_version': 'LEM3-v1.2.0',
        'confidence_threshold': 0.65,
        'accuracy_target': 0.67,
        'supported_events': [
            'pass', 'shot', 'goal', 'tackle', 'foul', 'offside',
            'corner_kick', 'throw_in', 'free_kick', 'penalty',
            'yellow_card', 'red_card', 'substitution', 'dribble',
            'clearance', 'interception', 'cross', 'header'
        ],
        'processing_timeout': 900,  # 15 minutes
        'batch_size': 32,
        'use_gpu': getattr(settings, 'OPENSTARLAB_USE_GPU', False)
    }
    
    NMSTPP_CONFIG = {
        'model_version': 'NMSTPP-v2.1.0',
        'formation_confidence_threshold': 0.8,
        'tactical_analysis_depth': 'advanced',
        'hpus_calculation_enabled': True,
        'possession_analysis_enabled': True,
        'formation_detection_enabled': True,
        'strategic_insights_enabled': True
    }
    
    RLEARN_CONFIG = {
        'model_version': 'RLearn-MultiAgent-v1.5.0',
        'q_value_threshold': 0.3,
        'multi_agent_evaluation': True,
        'player_tracking_enabled': True,
        'team_cohesion_analysis': True,
        'performance_benchmarking': True,
        'clutch_performance_analysis': True
    }
    
    PREDICTIVE_CONFIG = {
        'model_version': 'PredictiveEngine-v1.3.0',
        'confidence_threshold': 0.7,
        'match_outcome_prediction': True,
        'tactical_scenario_prediction': True,
        'player_performance_prediction': True,
        'formation_effectiveness_prediction': True,
        'prediction_horizon_minutes': 30
    }
    
    # UIED Format Configuration
    UIED_CONFIG = {
        'converter_version': 'UIED-Converter-v2.0.0',
        'supported_sources': [
            'statsbomb', 'wyscout', 'datastadium', 
            'gps_tracking', 'video_analysis', 'manual_scouting'
        ],
        'field_dimensions': {
            'length': 100,  # meters
            'width': 64,    # meters
            'coordinate_system': 'normalized'  # 0-100 scale
        },
        'quality_thresholds': {
            'completeness_minimum': 0.7,
            'accuracy_minimum': 0.8,
            'consistency_minimum': 0.75
        },
        'deduplication_enabled': True,
        'temporal_tolerance': 2.0,  # seconds
        'spatial_tolerance': 10.0   # field units
    }
    
    # Processing Pipeline Configuration
    PIPELINE_CONFIG = {
        'pipeline_version': 'OpenStarLab-Intelligence-v1.0.0',
        'processing_stages': [
            'preprocessing',
            'event_detection',
            'tactical_analysis', 
            'player_evaluation',
            'predictive_modeling',
            'postprocessing'
        ],
        'parallel_processing': getattr(settings, 'OPENSTARLAB_PARALLEL_PROCESSING', True),
        'max_workers': getattr(settings, 'OPENSTARLAB_MAX_WORKERS', 4),
        'memory_limit_mb': getattr(settings, 'OPENSTARLAB_MEMORY_LIMIT', 2048),
        'processing_timeout': getattr(settings, 'OPENSTARLAB_PROCESSING_TIMEOUT', 900)
    }
    
    # Quality Assurance Configuration
    QUALITY_CONFIG = {
        'validation_enabled': True,
        'benchmark_comparison': True,
        'accuracy_validation_threshold': 0.65,
        'processing_time_target': 900,  # 15 minutes
        'confidence_validation_enabled': True,
        'error_detection_enabled': True,
        'quality_reporting_enabled': True
    }
    
    # Analysis Intent Configurations
    ANALYSIS_INTENT_CONFIG = {
        'full_match': {
            'event_detection_scope': 'comprehensive',
            'tactical_analysis_depth': 'full',
            'player_evaluation_scope': 'all_players',
            'prediction_scope': 'complete',
            'processing_priority': 'standard'
        },
        'individual_player': {
            'event_detection_scope': 'player_focused',
            'tactical_analysis_depth': 'player_context',
            'player_evaluation_scope': 'target_player',
            'prediction_scope': 'player_performance',
            'processing_priority': 'fast'
        },
        'tactical_phase': {
            'event_detection_scope': 'tactical_events',
            'tactical_analysis_depth': 'comprehensive',
            'player_evaluation_scope': 'tactical_roles',
            'prediction_scope': 'tactical_scenarios',
            'processing_priority': 'standard'
        },
        'opposition_scouting': {
            'event_detection_scope': 'opponent_focused',
            'tactical_analysis_depth': 'opponent_patterns',
            'player_evaluation_scope': 'opponent_players',
            'prediction_scope': 'opponent_weaknesses',
            'processing_priority': 'thorough'
        },
        'set_piece': {
            'event_detection_scope': 'set_piece_events',
            'tactical_analysis_depth': 'set_piece_patterns',
            'player_evaluation_scope': 'set_piece_roles',
            'prediction_scope': 'set_piece_effectiveness',
            'processing_priority': 'fast'
        }
    }
    
    @classmethod
    def get_processor_config(cls, processor_type: str) -> Dict[str, Any]:
        """
        Get configuration for specific processor type.
        
        Args:
            processor_type: Type of processor ('lem3', 'nmstpp', 'rlearn', 'predictive', 'uied')
            
        Returns:
            Configuration dictionary for the processor
        """
        config_map = {
            'lem3': cls.LEM3_CONFIG,
            'nmstpp': cls.NMSTPP_CONFIG,
            'rlearn': cls.RLEARN_CONFIG,
            'predictive': cls.PREDICTIVE_CONFIG,
            'uied': cls.UIED_CONFIG
        }
        
        return config_map.get(processor_type, {})
    
    @classmethod
    def get_analysis_intent_config(cls, intent: str) -> Dict[str, Any]:
        """
        Get configuration for specific analysis intent.
        
        Args:
            intent: Analysis intent type
            
        Returns:
            Configuration dictionary for the intent
        """
        return cls.ANALYSIS_INTENT_CONFIG.get(intent, cls.ANALYSIS_INTENT_CONFIG['full_match'])
    
    @classmethod
    def get_performance_targets(cls) -> Dict[str, Any]:
        """
        Get performance targets for OpenStarLab processing.
        
        Returns:
            Dictionary of performance targets
        """
        return {
            'processing_time_target': 900,  # 15 minutes
            'accuracy_target': 0.67,        # LEM3 accuracy target
            'confidence_target': 0.85,      # Overall confidence target
            'event_detection_rate': 0.95,   # Event detection completeness
            'tactical_analysis_depth': 0.90, # Tactical analysis completeness
            'player_evaluation_coverage': 0.95, # Player evaluation coverage
            'prediction_accuracy': 0.75     # Prediction accuracy target
        }
    
    @classmethod
    def get_resource_limits(cls) -> Dict[str, Any]:
        """
        Get resource limits for processing.
        
        Returns:
            Dictionary of resource limits
        """
        return {
            'max_memory_mb': getattr(settings, 'OPENSTARLAB_MEMORY_LIMIT', 2048),
            'max_processing_time': getattr(settings, 'OPENSTARLAB_PROCESSING_TIMEOUT', 900),
            'max_concurrent_analyses': getattr(settings, 'OPENSTARLAB_MAX_CONCURRENT', 5),
            'max_video_size_mb': getattr(settings, 'OPENSTARLAB_MAX_VIDEO_SIZE', 2048),
            'max_events_per_analysis': 1000,
            'max_insights_per_analysis': 50
        }
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """
        Validate OpenStarLab configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required settings
            required_settings = [
                'LEM3_CONFIG',
                'NMSTPP_CONFIG', 
                'RLEARN_CONFIG',
                'PREDICTIVE_CONFIG',
                'UIED_CONFIG'
            ]
            
            for setting in required_settings:
                if not hasattr(cls, setting):
                    return False
            
            # Validate confidence thresholds
            if cls.LEM3_CONFIG['confidence_threshold'] < 0.0 or cls.LEM3_CONFIG['confidence_threshold'] > 1.0:
                return False
            
            # Validate processing timeout
            if cls.PIPELINE_CONFIG['processing_timeout'] <= 0:
                return False
            
            return True
            
        except Exception:
            return False


class DataSourceConfig:
    """Configuration for different data sources."""
    
    STATSBOMB_CONFIG = {
        'api_version': 'v1',
        'coordinate_system': 'statsbomb',
        'field_dimensions': {'length': 120, 'width': 80},
        'confidence_level': 0.95,
        'temporal_resolution': 0.1,  # Sub-second precision
        'spatial_resolution': 0.5    # Half-meter precision
    }
    
    WYSCOUT_CONFIG = {
        'api_version': 'v2',
        'coordinate_system': 'wyscout',
        'field_dimensions': {'length': 100, 'width': 100},
        'confidence_level': 0.90,
        'temporal_resolution': 1.0,  # Second precision
        'spatial_resolution': 1.0    # Meter precision
    }
    
    GPS_TRACKING_CONFIG = {
        'sampling_rate': 25,  # Hz
        'coordinate_system': 'gps',
        'confidence_level': 0.95,  # High GPS accuracy
        'event_inference_confidence': 0.70,  # Lower for inferred events
        'positional_accuracy': 0.1  # 10cm accuracy
    }
    
    VIDEO_ANALYSIS_CONFIG = {
        'frame_rate': 25,
        'resolution_requirements': {'min_width': 1280, 'min_height': 720},
        'confidence_threshold': 0.75,
        'detection_models': ['yolo', 'detectron2'],
        'tracking_enabled': True
    }


class EnvironmentConfig:
    """Environment-specific configuration settings."""
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment."""
        return getattr(settings, 'ENVIRONMENT', 'development')
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production."""
        return cls.get_environment() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development."""
        return cls.get_environment() == 'development'
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get appropriate log level for environment."""
        if cls.is_production():
            return 'INFO'
        else:
            return 'DEBUG'
    
    @classmethod
    def get_performance_mode(cls) -> str:
        """Get performance mode based on environment."""
        if cls.is_production():
            return 'optimized'
        else:
            return 'standard'


# Export main configuration class
__all__ = ['OpenStarLabConfig', 'DataSourceConfig', 'EnvironmentConfig']