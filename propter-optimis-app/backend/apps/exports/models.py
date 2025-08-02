"""
Exports models for Propter-Optimis Sports Analytics Platform.

Integrates with existing Supabase exports table:
- id (uuid, primary key)
- analysis_id (uuid, foreign key to analyses)
- export_type (varchar)
- file_url (text, nullable)
- created_at (timestamp)
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimestampedModel, ExportType
from apps.analytics.models import Analysis
import uuid


class Export(models.Model):
    """Export model that maps to Supabase exports table."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(
        Analysis, 
        on_delete=models.CASCADE, 
        related_name='exports',
        db_column='analysis_id'  # Map to Supabase column name
    )
    export_type = models.CharField(
        max_length=50, 
        choices=ExportType.choices
    )
    file_url = models.TextField(blank=True, null=True)  # URL to file in storage
    created_at = models.DateTimeField(default=timezone.now)
    
    # Additional fields not in Supabase
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    file_size = models.BigIntegerField(blank=True, null=True)  # File size in bytes
    error_message = models.TextField(blank=True, null=True)
    download_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(blank=True, null=True)  # Expiration date
    
    class Meta:
        db_table = 'exports'  # Map to existing Supabase table
        verbose_name = 'Export'
        verbose_name_plural = 'Exports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_export_type_display()} - {self.analysis.video.filename}"
    
    @property
    def is_completed(self):
        """Check if export is completed."""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if export failed."""
        return self.status == 'failed'
    
    @property
    def is_processing(self):
        """Check if export is currently processing."""
        return self.status == 'processing'
    
    @property
    def is_expired(self):
        """Check if export has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def formatted_file_size(self):
        """Format file size in human readable format."""
        if not self.file_size:
            return 'Unknown'
        
        from apps.core.utils import format_file_size
        return format_file_size(self.file_size)
    
    def mark_completed(self, file_url, file_size=None):
        """Mark export as completed."""
        self.status = 'completed'
        self.file_url = file_url
        
        if file_size:
            self.file_size = file_size
        
        # Set expiration date (30 days from now)
        self.expires_at = timezone.now() + timezone.timedelta(days=30)
        
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark export as failed."""
        self.status = 'failed'
        
        if error_message:
            self.error_message = error_message
        
        self.save()
    
    def increment_download_count(self):
        """Increment download counter."""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class ExportTemplate(TimestampedModel):
    """Templates for generating exports."""
    
    name = models.CharField(max_length=100)
    export_type = models.CharField(
        max_length=50, 
        choices=ExportType.choices
    )
    template_config = models.JSONField(default=dict)  # Template configuration
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Export Template'
        verbose_name_plural = 'Export Templates'
        unique_together = ['name', 'export_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_export_type_display()})"


class ExportCustomization(TimestampedModel):
    """User customizations for exports."""
    
    export = models.OneToOneField(
        Export, 
        on_delete=models.CASCADE, 
        related_name='customization'
    )
    
    # PDF customizations
    include_charts = models.BooleanField(default=True)
    include_heatmaps = models.BooleanField(default=True)
    include_timeline = models.BooleanField(default=True)
    include_player_stats = models.BooleanField(default=True)
    include_tactical_analysis = models.BooleanField(default=True)
    
    # Video clip customizations
    clip_duration = models.IntegerField(default=10)  # Seconds before/after event
    include_audio = models.BooleanField(default=True)
    video_quality = models.CharField(
        max_length=20,
        choices=[
            ('720p', '720p HD'),
            ('1080p', '1080p Full HD'),
            ('original', 'Original Quality')
        ],
        default='1080p'
    )
    
    # CSV customizations
    include_raw_data = models.BooleanField(default=False)
    include_calculated_metrics = models.BooleanField(default=True)
    timestamp_format = models.CharField(
        max_length=20,
        choices=[
            ('seconds', 'Seconds'),
            ('minutes', 'MM:SS'),
            ('full', 'HH:MM:SS')
        ],
        default='minutes'
    )
    
    # General customizations
    custom_title = models.CharField(max_length=200, blank=True, null=True)
    custom_description = models.TextField(blank=True, null=True)
    include_branding = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Export Customization'
        verbose_name_plural = 'Export Customizations'
    
    def __str__(self):
        return f"Customization for {self.export}"


class ExportShare(TimestampedModel):
    """Track export sharing and access."""
    
    export = models.ForeignKey(
        Export, 
        on_delete=models.CASCADE, 
        related_name='shares'
    )
    share_token = models.CharField(max_length=64, unique=True)  # Unique sharing token
    shared_with_email = models.EmailField(blank=True, null=True)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View Only'),
            ('download', 'View and Download'),
            ('full', 'Full Access')
        ],
        default='view'
    )
    expires_at = models.DateTimeField(blank=True, null=True)
    accessed_count = models.IntegerField(default=0)
    last_accessed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Export Share'
        verbose_name_plural = 'Export Shares'
    
    def __str__(self):
        return f"Share for {self.export} - {self.share_token[:8]}..."
    
    @property
    def is_expired(self):
        """Check if share has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def record_access(self):
        """Record an access to this share."""
        self.accessed_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['accessed_count', 'last_accessed_at'])
    
    def generate_share_url(self, base_url):
        """Generate shareable URL."""
        return f"{base_url}/shared/exports/{self.share_token}"
