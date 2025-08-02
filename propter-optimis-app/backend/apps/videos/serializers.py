"""
Video serializers for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import serializers
from django.conf import settings
from .models import Video, VideoUploadSession, VideoMetadata
from apps.core.models import AnalysisIntent, VideoStatus
from apps.core.utils import validate_file_size, validate_file_type
import os


class VideoMetadataSerializer(serializers.ModelSerializer):
    """Serializer for video metadata."""
    
    match_description = serializers.ReadOnlyField()
    
    class Meta:
        model = VideoMetadata
        fields = [
            'resolution', 'frame_rate', 'bitrate', 'codec',
            'match_date', 'home_team', 'away_team', 'competition', 'venue',
            'extracted_frames', 'processing_notes', 'match_description'
        ]


class VideoUploadSessionSerializer(serializers.ModelSerializer):
    """Serializer for video upload session."""
    
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    
    class Meta:
        model = VideoUploadSession
        fields = [
            'upload_id', 'total_chunks', 'uploaded_chunks', 'chunk_size',
            'progress_percentage', 'is_completed', 'is_failed',
            'started_at', 'completed_at', 'failed_at'
        ]
        read_only_fields = ['started_at', 'completed_at', 'failed_at']


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for video model."""
    
    metadata = VideoMetadataSerializer(read_only=True)
    upload_session = VideoUploadSessionSerializer(read_only=True)
    formatted_duration = serializers.ReadOnlyField()
    formatted_file_size = serializers.ReadOnlyField()
    is_processed = serializers.ReadOnlyField()
    can_analyze = serializers.ReadOnlyField()
    analysis_intent_display = serializers.CharField(
        source='get_analysis_intent_display_name', 
        read_only=True
    )
    
    class Meta:
        model = Video
        fields = [
            'id', 'filename', 's3_url', 'duration', 'status', 'analysis_intent',
            'created_at', 'file_size', 'content_type', 'upload_progress',
            'error_message', 'formatted_duration', 'formatted_file_size',
            'is_processed', 'can_analyze', 'analysis_intent_display',
            'metadata', 'upload_session'
        ]
        read_only_fields = [
            'id', 'created_at', 's3_url', 'duration', 'file_size', 
            'content_type', 'upload_progress'
        ]


class VideoUploadSerializer(serializers.Serializer):
    """Serializer for video upload."""
    
    file = serializers.FileField()
    analysis_intent = serializers.ChoiceField(
        choices=AnalysisIntent.choices,
        required=False
    )
    
    # Optional metadata
    match_date = serializers.DateTimeField(required=False)
    home_team = serializers.CharField(max_length=100, required=False)
    away_team = serializers.CharField(max_length=100, required=False)
    competition = serializers.CharField(max_length=100, required=False)
    venue = serializers.CharField(max_length=100, required=False)
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size
        if not validate_file_size(value, settings.MAX_FILE_SIZE):
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f'File size exceeds maximum allowed size of {max_size_mb:.0f}MB.'
            )
        
        # Check file type
        allowed_types = ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
        if not validate_file_type(value, allowed_types):
            raise serializers.ValidationError(
                f'File type not supported. Allowed types: {", ".join(allowed_types)}'
            )
        
        return value
    
    def create(self, validated_data):
        """Create video instance with upload data."""
        file = validated_data.pop('file')
        user = self.context['request'].user
        
        # Extract metadata
        metadata_fields = [
            'match_date', 'home_team', 'away_team', 'competition', 'venue'
        ]
        metadata = {field: validated_data.pop(field, None) for field in metadata_fields}
        
        # Create video instance
        video = Video.objects.create(
            user=user,
            filename=file.name,
            file_size=file.size,
            content_type=file.content_type,
            status=VideoStatus.UPLOADED,
            **validated_data
        )
        
        # Create metadata if any provided
        if any(metadata.values()):
            VideoMetadata.objects.create(video=video, **metadata)
        
        return video


class VideoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating video information."""
    
    class Meta:
        model = Video
        fields = ['analysis_intent', 'status']
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed status transitions
            allowed_transitions = {
                VideoStatus.UPLOADED: [VideoStatus.PROCESSING, VideoStatus.ERROR],
                VideoStatus.PROCESSING: [VideoStatus.READY, VideoStatus.ERROR],
                VideoStatus.ERROR: [VideoStatus.PROCESSING],
                VideoStatus.READY: [VideoStatus.PROCESSING]  # Allow reprocessing
            }
            
            if current_status in allowed_transitions:
                if value not in allowed_transitions[current_status]:
                    raise serializers.ValidationError(
                        f'Cannot transition from {current_status} to {value}'
                    )
        
        return value


class VideoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for video list view."""
    
    formatted_duration = serializers.ReadOnlyField()
    formatted_file_size = serializers.ReadOnlyField()
    analysis_intent_display = serializers.CharField(
        source='get_analysis_intent_display_name', 
        read_only=True
    )
    upload_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'filename', 'status', 'analysis_intent', 
            'analysis_intent_display', 'created_at', 'formatted_duration',
            'formatted_file_size', 'upload_progress'
        ]


class ChunkedUploadSerializer(serializers.Serializer):
    """Serializer for chunked file upload."""
    
    chunk = serializers.FileField()
    chunk_number = serializers.IntegerField(min_value=0)
    total_chunks = serializers.IntegerField(min_value=1)
    upload_id = serializers.CharField(max_length=255)
    filename = serializers.CharField(max_length=255)
    
    def validate(self, attrs):
        """Validate chunk upload data."""
        if attrs['chunk_number'] >= attrs['total_chunks']:
            raise serializers.ValidationError(
                'Chunk number must be less than total chunks'
            )
        
        return attrs
