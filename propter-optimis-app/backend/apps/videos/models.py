"""
Video models for Propter-Optimis Sports Analytics Platform.

Integrates with existing Supabase videos table:
- id (uuid, primary key)
- user_id (uuid, foreign key to users)
- filename (varchar)
- s3_url (text, nullable)
- duration (integer, nullable)
- status (varchar, default 'uploaded')
- analysis_intent (varchar, nullable)
- created_at (timestamp)
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimestampedModel, VideoStatus, AnalysisIntent
from apps.authentication.models import User
import uuid


class Video(models.Model):
    """Video model that maps to Supabase videos table."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='videos',
        db_column='user_id'  # Map to Supabase column name
    )
    filename = models.CharField(max_length=500)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    s3_url = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=50, 
        choices=VideoStatus.choices, 
        default=VideoStatus.UPLOADED
    )
    analysis_intent = models.CharField(
        max_length=100,
        choices=AnalysisIntent.choices,
        blank=True,
        null=True
    )
    upload_progress = models.IntegerField(default=0)  # 0-100 percentage
    processing_priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('standard', 'Standard'),
            ('high', 'High'),
            ('enterprise', 'Enterprise')
        ],
        default='standard'
    )
    file_size = models.BigIntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'videos'  # Map to existing Supabase table
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.user.email}"
    
    @property
    def is_processed(self):
        """Check if video has been processed."""
        return self.status in [VideoStatus.READY]
    
    @property
    def can_analyze(self):
        """Check if video can be analyzed."""
        return (self.upload_progress == 100 and 
                self.status == VideoStatus.READY and 
                self.analysis_intent)
    
    def calculate_processing_priority(self):
        """Calculate processing priority based on user tier and intent."""
        if self.user.subscription_tier == 'enterprise':
            return 'enterprise'
        elif self.analysis_intent == 'opposition_scouting':
            return 'high'
        elif self.user.subscription_tier == 'pro':
            return 'high'
        return 'standard'
    
    def update_processing_priority(self):
        """Update processing priority and save."""
        self.processing_priority = self.calculate_processing_priority()
        self.save(update_fields=['processing_priority'])
    
    @property
    def formatted_duration(self):
        """Format duration in human readable format."""
        if not self.duration:
            return 'Unknown'
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @property
    def formatted_file_size(self):
        """Format file size in human readable format."""
        if not self.file_size:
            return 'Unknown'
        
        from apps.core.utils import format_file_size
        return format_file_size(self.file_size)
    
    def get_analysis_intent_display_name(self):
        """Get human readable analysis intent."""
        if self.analysis_intent:
            return dict(AnalysisIntent.choices)[self.analysis_intent]
        return 'Not selected'


class VideoUploadSession(TimestampedModel):
    """Track video upload sessions for progress monitoring."""
    
    video = models.OneToOneField(
        Video, 
        on_delete=models.CASCADE, 
        related_name='upload_session'
    )
    upload_id = models.CharField(max_length=255, unique=True)  # Unique upload identifier
    total_chunks = models.IntegerField(default=1)
    uploaded_chunks = models.IntegerField(default=0)
    chunk_size = models.BigIntegerField(default=1024*1024*5)  # 5MB chunks
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    failed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Video Upload Session'
        verbose_name_plural = 'Video Upload Sessions'
    
    def __str__(self):
        return f"Upload session for {self.video.filename}"
    
    @property
    def progress_percentage(self):
        """Calculate upload progress percentage."""
        if self.total_chunks == 0:
            return 0
        return int((self.uploaded_chunks / self.total_chunks) * 100)
    
    @property
    def is_completed(self):
        """Check if upload is completed."""
        return self.completed_at is not None
    
    @property
    def is_failed(self):
        """Check if upload failed."""
        return self.failed_at is not None
    
    def mark_completed(self):
        """Mark upload as completed."""
        self.completed_at = timezone.now()
        self.uploaded_chunks = self.total_chunks
        self.save()
    
    def mark_failed(self):
        """Mark upload as failed."""
        self.failed_at = timezone.now()
        self.save()


class VideoMetadata(TimestampedModel):
    """Store additional video metadata and processing information."""
    
    video = models.OneToOneField(
        Video, 
        on_delete=models.CASCADE, 
        related_name='metadata'
    )
    
    # Video technical details
    resolution = models.CharField(max_length=20, blank=True, null=True)  # e.g., "1920x1080"
    frame_rate = models.FloatField(blank=True, null=True)
    bitrate = models.BigIntegerField(blank=True, null=True)
    codec = models.CharField(max_length=50, blank=True, null=True)
    
    # Sports-specific metadata
    match_date = models.DateTimeField(blank=True, null=True)
    home_team = models.CharField(max_length=100, blank=True, null=True)
    away_team = models.CharField(max_length=100, blank=True, null=True)
    competition = models.CharField(max_length=100, blank=True, null=True)
    venue = models.CharField(max_length=100, blank=True, null=True)
    
    # Processing metadata
    extracted_frames = models.IntegerField(default=0)
    processing_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Video Metadata'
        verbose_name_plural = 'Video Metadata'
    
    def __str__(self):
        return f"Metadata for {self.video.filename}"
    
    @property
    def match_description(self):
        """Generate match description string."""
        if self.home_team and self.away_team:
            return f"{self.home_team} vs {self.away_team}"
        return 'Match details not available'
