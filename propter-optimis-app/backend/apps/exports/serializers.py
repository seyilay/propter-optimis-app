"""
Exports serializers for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Export, ExportTemplate, ExportCustomization, ExportShare
from apps.core.models import ExportType
from apps.analytics.models import Analysis
import secrets


class ExportCustomizationSerializer(serializers.ModelSerializer):
    """Serializer for export customization."""
    
    class Meta:
        model = ExportCustomization
        fields = [
            'include_charts', 'include_heatmaps', 'include_timeline',
            'include_player_stats', 'include_tactical_analysis',
            'clip_duration', 'include_audio', 'video_quality',
            'include_raw_data', 'include_calculated_metrics', 'timestamp_format',
            'custom_title', 'custom_description', 'include_branding'
        ]


class ExportShareSerializer(serializers.ModelSerializer):
    """Serializer for export sharing."""
    
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ExportShare
        fields = [
            'id', 'share_token', 'shared_with_email', 'access_level',
            'expires_at', 'accessed_count', 'last_accessed_at',
            'is_active', 'is_expired', 'created_at'
        ]
        read_only_fields = [
            'id', 'share_token', 'accessed_count', 'last_accessed_at', 'created_at'
        ]


class ExportSerializer(serializers.ModelSerializer):
    """Serializer for export model."""
    
    analysis_video_filename = serializers.CharField(
        source='analysis.video.filename', 
        read_only=True
    )
    customization = ExportCustomizationSerializer(read_only=True)
    shares = ExportShareSerializer(many=True, read_only=True)
    formatted_file_size = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    is_processing = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Export
        fields = [
            'id', 'analysis', 'analysis_video_filename', 'export_type', 
            'file_url', 'status', 'file_size', 'formatted_file_size',
            'error_message', 'download_count', 'expires_at', 'created_at',
            'is_completed', 'is_failed', 'is_processing', 'is_expired',
            'customization', 'shares'
        ]
        read_only_fields = [
            'id', 'file_url', 'status', 'file_size', 'error_message',
            'download_count', 'created_at'
        ]


class ExportCreateSerializer(serializers.Serializer):
    """Serializer for creating exports."""
    
    analysis_id = serializers.UUIDField()
    export_type = serializers.ChoiceField(choices=ExportType.choices)
    customization = ExportCustomizationSerializer(required=False)
    
    def validate_analysis_id(self, value):
        """Validate analysis exists and belongs to user."""
        try:
            analysis = Analysis.objects.get(
                id=value,
                video__user=self.context['request'].user
            )
            
            # Check if analysis is completed
            if not analysis.is_completed:
                raise serializers.ValidationError(
                    f'Analysis is not completed yet. Status: {analysis.status}'
                )
            
            return value
            
        except Analysis.DoesNotExist:
            raise serializers.ValidationError(
                'Analysis not found or access denied.'
            )
    
    def create(self, validated_data):
        """Create export instance."""
        analysis = Analysis.objects.get(id=validated_data['analysis_id'])
        customization_data = validated_data.pop('customization', {})
        
        # Create export
        export = Export.objects.create(
            analysis=analysis,
            export_type=validated_data['export_type'],
            status='pending'
        )
        
        # Create customization if provided
        if customization_data:
            ExportCustomization.objects.create(
                export=export,
                **customization_data
            )
        
        return export


class ExportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for export templates."""
    
    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'name', 'export_type', 'template_config',
            'is_default', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ExportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for export list view."""
    
    analysis_video_filename = serializers.CharField(
        source='analysis.video.filename', 
        read_only=True
    )
    formatted_file_size = serializers.ReadOnlyField()
    
    class Meta:
        model = Export
        fields = [
            'id', 'analysis_video_filename', 'export_type', 'status',
            'formatted_file_size', 'download_count', 'created_at', 'expires_at'
        ]


class ExportShareCreateSerializer(serializers.Serializer):
    """Serializer for creating export shares."""
    
    export_id = serializers.UUIDField()
    shared_with_email = serializers.EmailField(required=False)
    access_level = serializers.ChoiceField(
        choices=[('view', 'View Only'), ('download', 'View and Download')],
        default='view'
    )
    expires_in_days = serializers.IntegerField(
        min_value=1, 
        max_value=30, 
        default=7
    )
    
    def validate_export_id(self, value):
        """Validate export exists and belongs to user."""
        try:
            export = Export.objects.get(
                id=value,
                analysis__video__user=self.context['request'].user
            )
            
            # Check if export is completed
            if not export.is_completed:
                raise serializers.ValidationError(
                    'Export is not completed yet.'
                )
            
            return value
            
        except Export.DoesNotExist:
            raise serializers.ValidationError(
                'Export not found or access denied.'
            )
    
    def create(self, validated_data):
        """Create export share."""
        export = Export.objects.get(id=validated_data['export_id'])
        expires_in_days = validated_data.pop('expires_in_days')
        
        # Generate unique share token
        share_token = secrets.token_urlsafe(32)
        
        # Calculate expiration date
        expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        
        # Create share
        share = ExportShare.objects.create(
            export=export,
            share_token=share_token,
            expires_at=expires_at,
            **validated_data
        )
        
        return share


class ExportStatsSerializer(serializers.Serializer):
    """Serializer for export statistics."""
    
    total_exports = serializers.IntegerField()
    pdf_exports = serializers.IntegerField()
    csv_exports = serializers.IntegerField()
    video_exports = serializers.IntegerField()
    completed_exports = serializers.IntegerField()
    failed_exports = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    total_shares = serializers.IntegerField()
    active_shares = serializers.IntegerField()
    storage_used_mb = serializers.FloatField()
    
    class Meta:
        fields = [
            'total_exports', 'pdf_exports', 'csv_exports', 'video_exports',
            'completed_exports', 'failed_exports', 'total_downloads',
            'total_shares', 'active_shares', 'storage_used_mb'
        ]
