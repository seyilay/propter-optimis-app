"""
Analytics views for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import logging

from .models import Analysis, AnalysisTask, AnalysisInsight, AnalysisMetrics
from .serializers import (
    AnalysisSerializer,
    AnalysisCreateSerializer,
    AnalysisListSerializer,
    AnalysisProgressSerializer,
    AnalysisResultsSerializer,
    AnalysisComparisonSerializer
)
from apps.core.utils import create_error_response, create_success_response
from apps.core.models import AnalysisStatus
from apps.videos.models import Video


logger = logging.getLogger(__name__)


class AnalysisListCreateView(generics.ListCreateAPIView):
    """List analyses and create new analysis requests."""
    
    permission_classes = [permissions.AllowAny] if settings.DEBUG else [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get analyses for current user's videos."""
        if settings.DEBUG and not self.request.user.is_authenticated:
            # Local development fallback - get test user's analyses
            from apps.authentication.models import User
            try:
                test_user = User.objects.get(email='test@example.com')
                return Analysis.objects.filter(
                    video__user=test_user
                ).select_related('video').prefetch_related('tasks', 'insights')
            except User.DoesNotExist:
                return Analysis.objects.none()
        else:
            return Analysis.objects.filter(
                video__user=self.request.user
            ).select_related('video').prefetch_related('tasks', 'insights')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == 'POST':
            return AnalysisCreateSerializer
        return AnalysisListSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new analysis request."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    analysis = serializer.save()
                    
                    # Trigger OpenStar Lab analysis
                    from .tasks import start_openstarlab_analysis
                    start_openstarlab_analysis.delay(analysis.id)
                    
                    logger.info(f"Analysis created: {analysis.id} for video {analysis.video.filename}")
                    
                    response_data = AnalysisSerializer(analysis).data
                    return create_success_response(
                        'Analysis started successfully',
                        response_data,
                        status.HTTP_201_CREATED
                    )
            
            return create_error_response(
                'Invalid analysis request',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error creating analysis: {e}")
            return create_error_response(
                'Failed to start analysis',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalysisDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an analysis."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnalysisSerializer
    
    def get_queryset(self):
        """Get analyses for current user's videos."""
        return Analysis.objects.filter(
            video__user=self.request.user
        ).select_related('video', 'metrics').prefetch_related(
            'tasks', 'insights'
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete analysis and associated data."""
        try:
            analysis = self.get_object()
            
            # Cancel analysis if still processing
            if analysis.is_processing:
                # TODO: Cancel OpenStar Lab analysis task
                pass
            
            analysis_id = analysis.id
            analysis.delete()
            
            logger.info(f"Analysis deleted: {analysis_id}")
            
            return create_success_response('Analysis deleted successfully')
            
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            return create_error_response(
                'Failed to delete analysis',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analysis_progress(request, analysis_id):
    """Get real-time analysis progress."""
    try:
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            video__user=request.user
        )
        
        progress_data = {
            'analysis_id': str(analysis.id),
            'status': analysis.status,
            'progress_percentage': analysis.progress_percentage,
            'current_step': analysis.current_step,
            'started_at': analysis.started_at,
            'estimated_completion': None,  # TODO: Calculate based on progress
            'error_message': analysis.error_message
        }
        
        return create_success_response(
            'Analysis progress retrieved',
            progress_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analysis progress: {e}")
        return create_error_response(
            'Failed to retrieve analysis progress',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_analysis(request, analysis_id):
    """Retry failed analysis."""
    try:
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            video__user=request.user
        )
        
        if not analysis.is_failed:
            return create_error_response(
                'Analysis is not in failed state',
                {'current_status': analysis.status},
                status.HTTP_400_BAD_REQUEST
            )
        
        # Reset analysis state
        analysis.status = AnalysisStatus.PENDING
        analysis.error_message = None
        analysis.progress_percentage = 0
        analysis.current_step = None
        analysis.started_at = None
        analysis.completed_at = None
        analysis.save()
        
        # Trigger OpenStar Lab analysis retry
        from .tasks import start_openstarlab_analysis
        start_openstarlab_analysis.delay(analysis.id)
        
        logger.info(f"Analysis retry initiated: {analysis.id}")
        
        return create_success_response(
            'Analysis retry initiated',
            AnalysisSerializer(analysis).data
        )
        
    except Exception as e:
        logger.error(f"Error retrying analysis: {e}")
        return create_error_response(
            'Failed to retry analysis',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_analysis(request, analysis_id):
    """Cancel running analysis."""
    try:
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            video__user=request.user
        )
        
        if not analysis.is_processing:
            return create_error_response(
                'Analysis is not currently processing',
                {'current_status': analysis.status},
                status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel analysis
        analysis.status = AnalysisStatus.CANCELLED
        analysis.completed_at = timezone.now()
        analysis.save()
        
        # TODO: Cancel OpenStar Lab analysis task
        
        logger.info(f"Analysis cancelled: {analysis.id}")
        
        return create_success_response(
            'Analysis cancelled successfully',
            AnalysisSerializer(analysis).data
        )
        
    except Exception as e:
        logger.error(f"Error cancelling analysis: {e}")
        return create_error_response(
            'Failed to cancel analysis',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AnalysisResultsView(APIView):
    """Get formatted analysis results."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, analysis_id):
        """Get analysis results summary."""
        try:
            analysis = get_object_or_404(
                Analysis,
                id=analysis_id,
                video__user=request.user
            )
            
            if not analysis.is_completed:
                return create_error_response(
                    'Analysis is not completed yet',
                    {'current_status': analysis.status},
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Format results for frontend consumption
            results_data = {
                'events_detected': 0,
                'key_moments': [],
                'tactical_insights': [],
                'player_statistics': {},
                'processing_time': analysis.processing_time or 0,
                'accuracy_score': 0.95,  # Mock data
                'confidence_level': 'High',
                'total_insights': analysis.insights.count(),
                'high_priority_insights': analysis.insights.filter(
                    importance_level__in=['high', 'critical']
                ).count(),
                'recommendations': []
            }
            
            # Parse OpenStar Lab results if available
            if analysis.openstarlab_results:
                openstar_data = analysis.openstarlab_results
                results_data.update({
                    'events_detected': openstar_data.get('events_detected', 0),
                    'key_moments': openstar_data.get('key_moments', []),
                    'tactical_insights': openstar_data.get('tactical_insights', []),
                    'player_statistics': openstar_data.get('player_statistics', {})
                })
            
            # Add AI insights
            if analysis.ai_insights:
                ai_data = analysis.ai_insights
                results_data['recommendations'] = ai_data.get('recommendations', [])
            
            return create_success_response(
                'Analysis results retrieved',
                results_data
            )
            
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return create_error_response(
                'Failed to retrieve analysis results',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalysisComparisonView(APIView):
    """Compare multiple analyses."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Compare analyses."""
        try:
            serializer = AnalysisComparisonSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                analysis_ids = serializer.validated_data['analysis_ids']
                comparison_type = serializer.validated_data['comparison_type']
                
                analyses = Analysis.objects.filter(
                    id__in=analysis_ids,
                    video__user=request.user,
                    status=AnalysisStatus.COMPLETED
                ).select_related('video', 'metrics').prefetch_related('insights')
                
                # Generate comparison data based on type
                comparison_data = self._generate_comparison(analyses, comparison_type)
                
                return create_success_response(
                    'Analysis comparison generated',
                    comparison_data
                )
            
            return create_error_response(
                'Invalid comparison request',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error generating analysis comparison: {e}")
            return create_error_response(
                'Failed to generate comparison',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_comparison(self, analyses, comparison_type):
        """Generate comparison data based on type."""
        comparison_data = {
            'comparison_type': comparison_type,
            'analyses_compared': len(analyses),
            'generated_at': timezone.now().isoformat(),
            'results': []
        }
        
        for analysis in analyses:
            analysis_summary = {
                'analysis_id': str(analysis.id),
                'video_filename': analysis.video.filename,
                'created_at': analysis.created_at.isoformat(),
                'processing_time': analysis.processing_time,
                'insights_count': analysis.insights.count()
            }
            
            if comparison_type == 'performance':
                if hasattr(analysis, 'metrics'):
                    analysis_summary.update({
                        'events_detected': analysis.metrics.events_detected,
                        'players_tracked': analysis.metrics.players_tracked,
                        'accuracy_score': analysis.metrics.accuracy_score
                    })
            
            elif comparison_type == 'tactical':
                # Add tactical-specific comparison data
                analysis_summary['tactical_patterns'] = []
                if analysis.openstarlab_results:
                    analysis_summary['tactical_patterns'] = analysis.openstarlab_results.get(
                        'tactical_insights', []
                    )
            
            comparison_data['results'].append(analysis_summary)
        
        return comparison_data


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analysis_statistics(request):
    """Get user's analysis statistics."""
    try:
        user_analyses = Analysis.objects.filter(video__user=request.user)
        
        stats = {
            'total_analyses': user_analyses.count(),
            'completed_analyses': user_analyses.filter(
                status=AnalysisStatus.COMPLETED
            ).count(),
            'processing_analyses': user_analyses.filter(
                status=AnalysisStatus.PROCESSING
            ).count(),
            'failed_analyses': user_analyses.filter(
                status=AnalysisStatus.FAILED
            ).count(),
            'average_processing_time': 0,
            'total_insights_generated': 0,
            'most_used_analysis_intent': None
        }
        
        # Calculate average processing time
        completed_analyses = user_analyses.filter(
            status=AnalysisStatus.COMPLETED,
            processing_time__isnull=False
        )
        
        if completed_analyses.exists():
            avg_time = completed_analyses.aggregate(
                avg_time=models.Avg('processing_time')
            )['avg_time']
            stats['average_processing_time'] = int(avg_time) if avg_time else 0
        
        # Count total insights
        total_insights = AnalysisInsight.objects.filter(
            analysis__video__user=request.user
        ).count()
        stats['total_insights_generated'] = total_insights
        
        # Find most used analysis intent
        from django.db.models import Count
        intent_counts = user_analyses.filter(
            video__analysis_intent__isnull=False
        ).values('video__analysis_intent').annotate(
            count=Count('video__analysis_intent')
        ).order_by('-count').first()
        
        if intent_counts:
            stats['most_used_analysis_intent'] = intent_counts['video__analysis_intent']
        
        return create_success_response(
            'Analysis statistics retrieved',
            stats
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analysis statistics: {e}")
        return create_error_response(
            'Failed to retrieve statistics',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
