"""
Celery tasks for OpenStarLab intelligence processing.

This module contains background tasks for processing football match
intelligence using the OpenStarLab AI pipeline.
"""
import logging
import time
from typing import Dict, Any, Optional
from celery import shared_task
from django.utils import timezone
from django.core.files.storage import default_storage

from .models import Analysis, AnalysisTask, AnalysisInsight, AnalysisMetrics
from .processors import OpenStarLabIntelligenceProcessor
from .uied_processor import UIEDConverter, UIEDDataSource
from apps.core.models import AnalysisStatus
from apps.videos.models import Video

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def start_openstarlab_analysis(self, analysis_id: str):
    """
    Main task for processing football match intelligence using OpenStarLab.
    
    Args:
        analysis_id: UUID of the analysis to process
    """
    logger.info(f"Starting OpenStarLab analysis for analysis_id: {analysis_id}")
    
    try:
        # Get analysis object
        analysis = Analysis.objects.select_related('video').get(id=analysis_id)
        
        # Initialize progress tracking
        analysis.mark_started()
        analysis.update_progress(5, "Initializing OpenStarLab processing")
        
        # Create analysis tasks for tracking
        create_analysis_tasks(analysis)
        
        # Process the intelligence pipeline
        results = process_intelligence_pipeline(analysis)
        
        # Save results and complete analysis
        save_analysis_results(analysis, results)
        
        # Generate insights
        generate_analysis_insights(analysis, results)
        
        # Calculate final metrics
        calculate_analysis_metrics(analysis, results)
        
        # Mark as completed
        analysis.mark_completed(
            results=results.get('openstarlab_results'),
            insights=results.get('ai_insights')
        )
        
        analysis.update_progress(100, "Analysis completed successfully")
        
        logger.info(f"OpenStarLab analysis completed for analysis_id: {analysis_id}")
        
        return {
            'status': 'completed',
            'analysis_id': str(analysis_id),
            'processing_time': analysis.processing_time,
            'events_detected': len(results.get('events', [])),
            'insights_generated': len(results.get('insights', []))
        }
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis not found: {analysis_id}")
        raise
        
    except Exception as e:
        logger.error(f"OpenStarLab analysis failed for {analysis_id}: {str(e)}")
        
        try:
            analysis = Analysis.objects.get(id=analysis_id)
            analysis.mark_failed(f"Processing failed: {str(e)}")
        except Analysis.DoesNotExist:
            pass
        
        # Retry the task if max retries not reached
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying analysis {analysis_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        raise


def create_analysis_tasks(analysis: Analysis):
    """Create tracking tasks for the analysis pipeline."""
    tasks = [
        {
            'task_name': 'Video Preprocessing',
            'task_type': 'preprocessing',
            'status': AnalysisStatus.PENDING
        },
        {
            'task_name': 'LEM3 Event Detection',
            'task_type': 'event_modeling',
            'status': AnalysisStatus.PENDING
        },
        {
            'task_name': 'NMSTPP Tactical Analysis',
            'task_type': 'tactical_analysis',
            'status': AnalysisStatus.PENDING
        },
        {
            'task_name': 'RLearn Player Evaluation',
            'task_type': 'player_tracking',
            'status': AnalysisStatus.PENDING
        },
        {
            'task_name': 'Predictive Modeling',
            'task_type': 'insight_generation',
            'status': AnalysisStatus.PENDING
        },
        {
            'task_name': 'Results Compilation',
            'task_type': 'postprocessing',
            'status': AnalysisStatus.PENDING
        }
    ]
    
    for task_data in tasks:
        AnalysisTask.objects.create(
            analysis=analysis,
            **task_data
        )


def process_intelligence_pipeline(analysis: Analysis) -> Dict[str, Any]:
    """
    Process the complete OpenStarLab intelligence pipeline.
    
    Args:
        analysis: Analysis object to process
        
    Returns:
        Complete intelligence results
    """
    logger.info(f"Processing intelligence pipeline for analysis {analysis.id}")
    
    # Initialize processors
    intelligence_processor = OpenStarLabIntelligenceProcessor()
    uied_converter = UIEDConverter()
    
    def progress_callback(percentage: int, step: str):
        """Callback for progress updates."""
        analysis.update_progress(percentage, step)
        logger.info(f"Analysis {analysis.id}: {percentage}% - {step}")
    
    try:
        # Step 1: Preprocess video data
        task = analysis.tasks.get(task_type='preprocessing')
        task.mark_started()
        
        progress_callback(10, "Preprocessing video data")
        video_data = preprocess_video_data(analysis.video)
        
        task.mark_completed({'video_metadata': video_data})
        
        # Step 2: Convert to UIED format
        progress_callback(15, "Converting to UIED format")
        uied_data = convert_to_uied_format(video_data, analysis.video.analysis_intent)
        
        # Step 3: Process with OpenStarLab intelligence
        progress_callback(20, "Starting OpenStarLab intelligence processing")
        
        intelligence_results = intelligence_processor.process_match_intelligence(
            video_data=video_data,
            analysis_intent=analysis.video.analysis_intent or 'full_match',
            progress_callback=progress_callback
        )
        
        # Compile results
        results = {
            'openstarlab_results': {
                'events': [event.__dict__ for event in intelligence_results.events],
                'tactical_analysis': intelligence_results.tactical_analysis,
                'player_evaluations': intelligence_results.player_evaluations,
                'predictions': intelligence_results.predictions,
                'confidence_scores': intelligence_results.confidence_scores,
                'processing_metadata': intelligence_results.processing_metadata
            },
            'ai_insights': extract_ai_insights(intelligence_results),
            'uied_data': uied_data,
            'intelligence_results': intelligence_results
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Intelligence pipeline failed: {str(e)}")
        
        # Mark any running tasks as failed
        for task in analysis.tasks.filter(status=AnalysisStatus.PROCESSING):
            task.mark_failed(str(e))
        
        raise


def preprocess_video_data(video: Video) -> Dict[str, Any]:
    """
    Preprocess video data for OpenStarLab analysis.
    
    Args:
        video: Video object to preprocess
        
    Returns:
        Preprocessed video metadata
    """
    logger.info(f"Preprocessing video: {video.filename}")
    
    # Simulate video preprocessing (in production, this would involve actual video processing)
    video_data = {
        'video_id': str(video.id),
        'filename': video.filename,
        'duration': video.duration or 90 * 60,  # Default 90 minutes
        'frame_rate': 25,  # Standard frame rate
        'resolution': {'width': 1920, 'height': 1080},
        'format': 'mp4',
        'file_size': getattr(video, 'file_size', 0),
        's3_url': video.s3_url,
        'analysis_intent': video.analysis_intent,
        'preprocessing_timestamp': timezone.now().isoformat(),
        
        # Simulated video analysis metadata
        'quality_score': 0.85,
        'lighting_conditions': 'good',
        'camera_angles': ['main_camera', 'tactical_camera'],
        'field_visibility': 0.95,
        'player_visibility': 0.90
    }
    
    return video_data


def convert_to_uied_format(video_data: Dict[str, Any], analysis_intent: str) -> Dict[str, Any]:
    """
    Convert video data to UIED format for standardized processing.
    
    Args:
        video_data: Preprocessed video data
        analysis_intent: Type of analysis to perform
        
    Returns:
        UIED formatted data
    """
    logger.info(f"Converting to UIED format with intent: {analysis_intent}")
    
    # Create mock video analysis data for UIED conversion
    mock_video_analysis_data = {
        'match_info': {
            'match_id': video_data['video_id'],
            'home_team': 'Home Team',
            'away_team': 'Away Team',
            'competition': 'League Match',
            'date': timezone.now().isoformat()
        },
        'detected_events': generate_mock_events_for_uied(video_data, analysis_intent),
        'metadata': {
            'analysis_intent': analysis_intent,
            'video_quality': video_data.get('quality_score', 0.85),
            'processing_version': '1.0'
        }
    }
    
    # Convert to UIED format
    converter = UIEDConverter()
    uied_match = converter.convert_to_uied(
        mock_video_analysis_data, 
        UIEDDataSource.VIDEO_ANALYSIS
    )
    
    return {
        'uied_match': uied_match,
        'quality_analysis': analyze_uied_quality(uied_match),
        'conversion_metadata': {
            'source': UIEDDataSource.VIDEO_ANALYSIS.value,
            'conversion_timestamp': timezone.now().isoformat(),
            'events_converted': len(uied_match.events)
        }
    }


def generate_mock_events_for_uied(video_data: Dict[str, Any], analysis_intent: str) -> list:
    """Generate mock events for UIED conversion."""
    import random
    import uuid
    
    duration = video_data.get('duration', 90 * 60)
    
    # Event types and their probabilities
    event_types = [
        'pass', 'shot', 'goal', 'tackle', 'foul', 'dribble',
        'corner_kick', 'throw_in', 'free_kick', 'clearance',
        'interception', 'cross', 'header'
    ]
    
    # Adjust number of events based on analysis intent
    event_count = {
        'full_match': random.randint(80, 120),
        'individual_player': random.randint(20, 40),
        'tactical_phase': random.randint(30, 60),
        'opposition_scouting': random.randint(40, 80),
        'set_piece': random.randint(10, 25)
    }.get(analysis_intent, 80)
    
    events = []
    for i in range(event_count):
        event_time = random.uniform(0, duration)
        
        event = {
            'id': f"mock_event_{uuid.uuid4().hex[:8]}",
            'timestamp': event_time,
            'event_type': random.choice(event_types),
            'coordinates': {
                'x': random.uniform(0, 100),
                'y': random.uniform(0, 100)
            },
            'players_involved': [
                {
                    'player_id': f"player_{random.randint(1, 22):02d}",
                    'jersey_number': random.randint(1, 99),
                    'position': random.choice(['GK', 'CB', 'LB', 'RB', 'CM', 'CAM', 'LW', 'RW', 'ST']),
                    'team': random.choice(['home', 'away']),
                    'name': f"Player {random.randint(1, 22)}"
                }
            ],
            'team': random.choice(['home', 'away']),
            'confidence': random.uniform(0.7, 0.95),
            'context': {
                'phase_of_play': random.choice(['attacking', 'defending', 'transition']),
                'pressure_level': random.choice(['low', 'medium', 'high'])
            }
        }
        
        events.append(event)
    
    return sorted(events, key=lambda e: e['timestamp'])


def analyze_uied_quality(uied_match) -> Dict[str, Any]:
    """Analyze the quality of UIED data."""
    from .uied_processor import UIEDAnalyzer
    
    analyzer = UIEDAnalyzer()
    return analyzer.analyze_uied_quality(uied_match)


def extract_ai_insights(intelligence_results) -> Dict[str, Any]:
    """
    Extract AI insights from intelligence results for storage.
    
    Args:
        intelligence_results: Results from OpenStarLab processing
        
    Returns:
        Formatted AI insights
    """
    tactical_insights = intelligence_results.tactical_analysis.get('strategic_insights', [])
    player_insights = intelligence_results.player_evaluations.get('performance_insights', [])
    
    ai_insights = {
        'tactical_insights': tactical_insights,
        'player_insights': player_insights,
        'key_recommendations': [],
        'performance_summary': {
            'events_detected': len(intelligence_results.events),
            'tactical_patterns_identified': len(tactical_insights),
            'standout_performances': len(player_insights),
            'overall_match_quality': intelligence_results.confidence_scores.get('overall_intelligence_confidence', 0.8)
        },
        'predictive_insights': {
            'match_outcome_predictions': intelligence_results.predictions.get('match_outcomes', {}),
            'tactical_recommendations': intelligence_results.predictions.get('tactical_scenarios', {}),
            'player_performance_predictions': intelligence_results.predictions.get('player_performance', {})
        }
    }
    
    # Generate key recommendations based on insights
    recommendations = []
    
    # Tactical recommendations
    for tactical_insight in tactical_insights:
        if tactical_insight.get('confidence', 0) > 0.8:
            recommendations.append({
                'type': 'tactical',
                'title': tactical_insight.get('title', 'Tactical Insight'),
                'recommendation': tactical_insight.get('actionable_recommendation', ''),
                'priority': 'high' if tactical_insight.get('confidence', 0) > 0.9 else 'medium',
                'confidence': tactical_insight.get('confidence', 0)
            })
    
    # Player performance recommendations
    for player_insight in player_insights:
        if player_insight.get('insight_type') == 'top_performer':
            recommendations.append({
                'type': 'player_performance',
                'title': f"Outstanding Performance: {player_insight.get('player_id', 'Unknown')}",
                'recommendation': f"Continue utilizing this player's exceptional form",
                'priority': 'high',
                'confidence': 0.9
            })
    
    ai_insights['key_recommendations'] = recommendations
    
    return ai_insights


def save_analysis_results(analysis: Analysis, results: Dict[str, Any]):
    """
    Save analysis results to the database.
    
    Args:
        analysis: Analysis object
        results: Complete intelligence results
    """
    logger.info(f"Saving analysis results for analysis {analysis.id}")
    
    try:
        # Update analysis with results
        analysis.openstarlab_results = results['openstarlab_results']
        analysis.ai_insights = results['ai_insights']
        analysis.save()
        
        logger.info(f"Analysis results saved for analysis {analysis.id}")
        
    except Exception as e:
        logger.error(f"Failed to save analysis results: {str(e)}")
        raise


def generate_analysis_insights(analysis: Analysis, results: Dict[str, Any]):
    """
    Generate and save structured insights from analysis results.
    
    Args:
        analysis: Analysis object
        results: Intelligence results
    """
    logger.info(f"Generating insights for analysis {analysis.id}")
    
    try:
        intelligence_results = results['intelligence_results']
        
        # Create tactical insights
        tactical_insights = intelligence_results.tactical_analysis.get('strategic_insights', [])
        for insight_data in tactical_insights:
            AnalysisInsight.objects.create(
                analysis=analysis,
                insight_type='tactical_pattern',
                title=insight_data.get('title', 'Tactical Insight'),
                description=insight_data.get('description', ''),
                confidence_score=insight_data.get('confidence', 0.5),
                importance_level=determine_importance_level(insight_data.get('confidence', 0.5)),
                metadata=insight_data.get('supporting_metrics', {})
            )
        
        # Create player performance insights
        player_insights = intelligence_results.player_evaluations.get('performance_insights', [])
        for insight_data in player_insights:
            AnalysisInsight.objects.create(
                analysis=analysis,
                insight_type='player_performance',
                title=insight_data.get('title', 'Player Performance Insight'),
                description=insight_data.get('description', ''),
                confidence_score=insight_data.get('confidence', 0.5),
                importance_level=determine_importance_level(insight_data.get('confidence', 0.5)),
                metadata={
                    'player_id': insight_data.get('player_id', ''),
                    'performance_score': insight_data.get('performance_score', 0)
                }
            )
        
        # Create key moment insights
        events = intelligence_results.events
        key_events = [e for e in events if e.get('confidence', 0) > 0.9]
        
        for event in key_events[:5]:  # Top 5 key moments
            AnalysisInsight.objects.create(
                analysis=analysis,
                insight_type='key_moments',
                title=f"Key Moment: {event.get('event_type', 'Event').title()}",
                description=f"High-confidence {event.get('event_type', 'event')} at {format_timestamp(event.get('timestamp', 0))}",
                confidence_score=event.get('confidence', 0.5),
                importance_level=determine_importance_level(event.get('confidence', 0.5)),
                metadata={
                    'event_id': event.get('id', ''),
                    'timestamp': event.get('timestamp', 0),
                    'coordinates': event.get('coordinates', {})
                }
            )
        
        logger.info(f"Generated {analysis.insights.count()} insights for analysis {analysis.id}")
        
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}")
        raise


def calculate_analysis_metrics(analysis: Analysis, results: Dict[str, Any]):
    """
    Calculate and save analysis performance metrics.
    
    Args:
        analysis: Analysis object
        results: Intelligence results
    """
    logger.info(f"Calculating metrics for analysis {analysis.id}")
    
    try:
        intelligence_results = results['intelligence_results']
        processing_metadata = intelligence_results.processing_metadata
        
        # Create metrics object
        metrics = AnalysisMetrics.objects.create(
            analysis=analysis,
            total_frames_processed=processing_metadata.get('events_processed', 0) * 25,  # Estimate frames
            events_detected=processing_metadata.get('events_processed', 0),
            players_tracked=processing_metadata.get('players_evaluated', 0),
            accuracy_score=intelligence_results.confidence_scores.get('overall_intelligence_confidence', 0.8),
            preprocessing_time=5,  # Mock preprocessing time
            analysis_time=int(processing_metadata.get('total_processing_time', 0)),
            postprocessing_time=2,  # Mock postprocessing time
            cpu_time_used=processing_metadata.get('total_processing_time', 0) * 1.2,  # Estimate CPU time
            memory_peak_mb=512  # Mock memory usage
        )
        
        logger.info(f"Analysis metrics calculated and saved for analysis {analysis.id}")
        
    except Exception as e:
        logger.error(f"Failed to calculate analysis metrics: {str(e)}")
        raise


def determine_importance_level(confidence_score: float) -> str:
    """Determine importance level based on confidence score."""
    if confidence_score >= 0.9:
        return 'critical'
    elif confidence_score >= 0.8:
        return 'high'
    elif confidence_score >= 0.6:
        return 'medium'
    else:
        return 'low'


def format_timestamp(seconds: float) -> str:
    """Format timestamp in MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


@shared_task
def cleanup_old_analysis_tasks():
    """Clean up old analysis tasks and temporary data."""
    logger.info("Cleaning up old analysis tasks")
    
    try:
        # Delete tasks older than 30 days
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_tasks = AnalysisTask.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_tasks.count()
        old_tasks.delete()
        
        logger.info(f"Cleaned up {deleted_count} old analysis tasks")
        
        return {'deleted_tasks': deleted_count}
        
    except Exception as e:
        logger.error(f"Failed to cleanup old analysis tasks: {str(e)}")
        raise


@shared_task
def generate_analysis_report(analysis_id: str, report_format: str = 'json'):
    """
    Generate comprehensive analysis report.
    
    Args:
        analysis_id: UUID of the analysis
        report_format: Format of the report ('json', 'pdf', 'csv')
    """
    logger.info(f"Generating {report_format} report for analysis {analysis_id}")
    
    try:
        analysis = Analysis.objects.select_related('video', 'metrics').prefetch_related(
            'insights', 'tasks'
        ).get(id=analysis_id)
        
        if not analysis.is_completed:
            raise ValueError("Analysis is not completed yet")
        
        # Generate report data
        report_data = {
            'analysis_summary': {
                'analysis_id': str(analysis.id),
                'video_filename': analysis.video.filename,
                'analysis_intent': analysis.video.analysis_intent,
                'processing_time': analysis.processing_time,
                'status': analysis.status,
                'created_at': analysis.created_at.isoformat(),
                'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None
            },
            'intelligence_results': analysis.openstarlab_results,
            'ai_insights': analysis.ai_insights,
            'performance_metrics': {
                'events_detected': analysis.metrics.events_detected if hasattr(analysis, 'metrics') else 0,
                'players_tracked': analysis.metrics.players_tracked if hasattr(analysis, 'metrics') else 0,
                'accuracy_score': analysis.metrics.accuracy_score if hasattr(analysis, 'metrics') else 0,
                'total_processing_time': analysis.metrics.total_processing_time if hasattr(analysis, 'metrics') else 0
            },
            'insights_summary': [
                {
                    'type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'confidence': insight.confidence_score,
                    'importance': insight.importance_level
                }
                for insight in analysis.insights.all()
            ]
        }
        
        # Format report based on requested format
        if report_format == 'json':
            import json
            report_content = json.dumps(report_data, indent=2, default=str)
        elif report_format == 'csv':
            report_content = generate_csv_report(report_data)
        elif report_format == 'pdf':
            report_content = generate_pdf_report(report_data)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")
        
        logger.info(f"Generated {report_format} report for analysis {analysis_id}")
        
        return {
            'status': 'completed',
            'report_format': report_format,
            'report_size': len(report_content),
            'generation_timestamp': timezone.now().isoformat()
        }
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis not found: {analysis_id}")
        raise
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise


def generate_csv_report(report_data: Dict[str, Any]) -> str:
    """Generate CSV format report."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write analysis summary
    writer.writerow(['Analysis Summary'])
    for key, value in report_data['analysis_summary'].items():
        writer.writerow([key, value])
    
    writer.writerow([])  # Empty row
    
    # Write insights
    writer.writerow(['Insights'])
    writer.writerow(['Type', 'Title', 'Description', 'Confidence', 'Importance'])
    
    for insight in report_data['insights_summary']:
        writer.writerow([
            insight['type'],
            insight['title'],
            insight['description'][:100] + '...' if len(insight['description']) > 100 else insight['description'],
            insight['confidence'],
            insight['importance']
        ])
    
    return output.getvalue()


def generate_pdf_report(report_data: Dict[str, Any]) -> str:
    """Generate PDF format report (placeholder implementation)."""
    # In production, this would use a PDF generation library like ReportLab
    return f"PDF Report for Analysis {report_data['analysis_summary']['analysis_id']} - Generated at {timezone.now()}"