"""
Core serializers for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import serializers
from django.utils import timezone


class TimestampedSerializer(serializers.ModelSerializer):
    """Base serializer for timestamped models."""
    
    class Meta:
        fields = ['id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnalysisProgressSerializer(serializers.Serializer):
    """Serializer for analysis progress updates."""
    status = serializers.CharField()
    progress_percentage = serializers.IntegerField(min_value=0, max_value=100)
    current_step = serializers.CharField()
    estimated_completion = serializers.DateTimeField(required=False)
    message = serializers.CharField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success responses."""
    message = serializers.CharField()
    data = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)
