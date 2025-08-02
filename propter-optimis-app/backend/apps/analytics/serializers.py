"""
Analytics serializers for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Analysis, AnalysisTask, AnalysisInsight, AnalysisMetrics
from apps.videos.serializers import VideoListSerializer
from apps.core.models import AnalysisStatus, AnalysisIntent


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """Serializer for analysis tasks."""
    
    class Meta:
        model = AnalysisTask
        fields = [
            'id', 'task_name', 'task_type', 'status', 'started_at', 
            'completed_at', 'duration', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnalysisInsightSerializer(serializers.ModelSerializer):
    """Serializer for analysis insights."""
    
    class Meta:
        model = AnalysisInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'confidence_score',
            'importance_level', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnalysisMetricsSerializer(serializers.ModelSerializer):
    """Serializer for analysis metrics."""
    
    total_processing_time = serializers.ReadOnlyField()
    events_per_minute = serializers.ReadOnlyField()
    
    class Meta:
        model = AnalysisMetrics
        fields = [
            'total_frames_processed', 'events_detected', 'players_tracked',
            'accuracy_score', 'preprocessing_time', 'analysis_time',
            'postprocessing_time', 'total_processing_time', 'cpu_time_used',
            'memory_peak_mb', 'events_per_minute'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer for analysis model."""
    
    video = VideoListSerializer(read_only=True)
    tasks = AnalysisTaskSerializer(many=True, read_only=True)
    insights = AnalysisInsightSerializer(many=True, read_only=True)
    metrics = AnalysisMetricsSerializer(read_only=True)
    formatted_processing_time = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    is_processing = serializers.ReadOnlyField()
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'video', 'openstarlab_results', 'ai_insights', 'status',
            'processing_time', 'formatted_processing_time', 'created_at',
            'started_at', 'completed_at', 'error_message', 'progress_percentage',
            'current_step', 'is_completed', 'is_failed', 'is_processing',
            'tasks', 'insights', 'metrics'
        ]
        read_only_fields = [
            'id', 'created_at', 'started_at', 'completed_at', 
            'processing_time', 'openstarlab_results', 'ai_insights'
        ]


class AnalysisCreateSerializer(serializers.Serializer):
    """Serializer for creating new analysis."""
    
    video_id = serializers.UUIDField()
    analysis_intent = serializers.ChoiceField(
        choices=AnalysisIntent.choices,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')],
        default='normal'
    )
    
    def validate_video_id(self, value):
        """Validate video exists and belongs to user."""
        from apps.videos.models import Video
        
        try:
            video = Video.objects.get(
                id=value, 
                user=self.context['request'].user
            )
            
            # Check if video is ready for analysis
            if not video.can_analyze:
                raise serializers.ValidationError(
                    f'Video is not ready for analysis. Status: {video.status}'
                )
            
            return value
            
        except Video.DoesNotExist:
            raise serializers.ValidationError('Video not found or access denied.')
    
    def create(self, validated_data):
        """Create analysis instance."""
        from apps.videos.models import Video
        
        video = Video.objects.get(id=validated_data['video_id'])
        
        # Update video analysis intent if provided
        if 'analysis_intent' in validated_data:
            video.analysis_intent = validated_data['analysis_intent']
            video.save()
        
        # Create analysis
        analysis = Analysis.objects.create(
            video=video,
            status=AnalysisStatus.PENDING
        )
        
        return analysis


class AnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for analysis list view."""
    
    video_filename = serializers.CharField(source='video.filename', read_only=True)
    video_duration = serializers.CharField(source='video.formatted_duration', read_only=True)
    analysis_intent = serializers.CharField(source='video.get_analysis_intent_display_name', read_only=True)
    formatted_processing_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'video_filename', 'video_duration', 'analysis_intent',
            'status', 'progress_percentage', 'current_step',
            'formatted_processing_time', 'created_at', 'completed_at'
        ]


class AnalysisProgressSerializer(serializers.Serializer):
    """Serializer for analysis progress updates."""
    
    analysis_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=AnalysisStatus.choices)
    progress_percentage = serializers.IntegerField(min_value=0, max_value=100)
    current_step = serializers.CharField(max_length=100, required=False)
    estimated_completion = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)
    
    class Meta:
        fields = [
            'analysis_id', 'status', 'progress_percentage', 'current_step',
            'estimated_completion', 'error_message'
        ]


class AnalysisResultsSerializer(serializers.Serializer):
    """Serializer for analysis results summary."""
    
    # OpenStar Lab results summary
    events_detected = serializers.IntegerField()
    key_moments = serializers.ListField(child=serializers.DictField())
    tactical_insights = serializers.ListField(child=serializers.DictField())
    player_statistics = serializers.DictField()
    
    # Performance metrics
    processing_time = serializers.IntegerField()
    accuracy_score = serializers.FloatField()
    confidence_level = serializers.CharField()
    
    # Insights summary
    total_insights = serializers.IntegerField()
    high_priority_insights = serializers.IntegerField()
    recommendations = serializers.ListField(child=serializers.DictField())


class AnalysisComparisonSerializer(serializers.Serializer):
    """Serializer for comparing multiple analyses."""
    
    analysis_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2,
        max_length=5
    )
    comparison_type = serializers.ChoiceField(
        choices=[
            ('performance', 'Performance Comparison'),
            ('tactical', 'Tactical Comparison'),
            ('temporal', 'Temporal Comparison')
        ]
    )
    
    def validate_analysis_ids(self, value):
        """Validate all analyses exist and belong to user."""
        user = self.context['request'].user
        
        analyses = Analysis.objects.filter(
            id__in=value,
            video__user=user,
            status=AnalysisStatus.COMPLETED
        )
        
        if len(analyses) != len(value):
            raise serializers.ValidationError(
                'One or more analyses not found or not completed.'
            )
        
        return value
