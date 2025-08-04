"""
Analytics models for Propter-Optimis Sports Analytics Platform.

Integrates with existing Supabase analyses table:
- id (uuid, primary key)
- video_id (uuid, foreign key to videos)
- openstarlab_results (jsonb, nullable)
- ai_insights (jsonb, nullable)
- status (varchar, default 'pending')
- processing_time (integer, nullable)
- created_at (timestamp)
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimestampedModel, AnalysisStatus, AnalysisIntent
from apps.videos.models import Video
import uuid
import json


class Analysis(models.Model):
    """Analysis model that maps to Supabase analyses table."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(
        Video, 
        on_delete=models.CASCADE, 
        related_name='analyses',
        db_column='video_id'  # Map to Supabase column name
    )
    openstarlab_results = models.JSONField(blank=True, null=True)
    ai_insights = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=50, 
        choices=AnalysisStatus.choices, 
        default=AnalysisStatus.PENDING
    )
    processing_time = models.IntegerField(blank=True, null=True)  # Time in seconds
    progress_percentage = models.IntegerField(default=0)  # 0-100 percentage
    current_step = models.CharField(max_length=100, blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'analyses'  # Map to existing Supabase table
        verbose_name = 'Analysis'
        verbose_name_plural = 'Analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis for {self.video.filename} - {self.status}"
    
    @property
    def is_completed(self):
        """Check if analysis is completed."""
        return self.status == AnalysisStatus.COMPLETED
    
    @property
    def is_failed(self):
        """Check if analysis failed."""
        return self.status == AnalysisStatus.FAILED
    
    @property
    def is_processing(self):
        """Check if analysis is currently processing."""
        return self.status == AnalysisStatus.PROCESSING
    
    @property
    def formatted_processing_time(self):
        """Format processing time in human readable format."""
        if not self.processing_time:
            return 'Unknown'
        
        minutes = self.processing_time // 60
        seconds = self.processing_time % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def mark_started(self):
        """Mark analysis as started."""
        self.status = AnalysisStatus.PROCESSING
        self.started_at = timezone.now()
        self.save()
    
    def mark_completed(self, results=None, insights=None, processing_time=None):
        """Mark analysis as completed."""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        
        if results:
            self.openstarlab_results = results
        if insights:
            self.ai_insights = insights
        if processing_time:
            self.processing_time = processing_time
        elif self.started_at:
            # Calculate processing time
            duration = self.completed_at - self.started_at
            self.processing_time = int(duration.total_seconds())
        
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark analysis as failed."""
        self.status = AnalysisStatus.FAILED
        self.completed_at = timezone.now()
        
        if error_message:
            self.error_message = error_message
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.processing_time = int(duration.total_seconds())
        
        self.save()
    
    def update_progress(self, percentage, step=None):
        """Update analysis progress."""
        self.progress_percentage = min(100, max(0, percentage))
        
        if step:
            self.current_step = step
        
        self.save()


class AnalysisTask(TimestampedModel):
    """Track individual analysis tasks and steps."""
    
    analysis = models.ForeignKey(
        Analysis, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    task_name = models.CharField(max_length=100)
    task_type = models.CharField(
        max_length=50,
        choices=[
            ('preprocessing', 'Preprocessing'),
            ('event_modeling', 'Event Modeling'),
            ('tactical_analysis', 'Tactical Analysis'),
            ('player_tracking', 'Player Tracking'),
            ('insight_generation', 'Insight Generation'),
            ('postprocessing', 'Postprocessing')
        ]
    )
    status = models.CharField(
        max_length=20, 
        choices=AnalysisStatus.choices, 
        default=AnalysisStatus.PENDING
    )
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)  # Duration in seconds
    result_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Analysis Task'
        verbose_name_plural = 'Analysis Tasks'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.task_name} - {self.status}"
    
    def mark_started(self):
        """Mark task as started."""
        self.status = AnalysisStatus.PROCESSING
        self.started_at = timezone.now()
        self.save()
    
    def mark_completed(self, result_data=None):
        """Mark task as completed."""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = timezone.now()
        
        if result_data:
            self.result_data = result_data
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration = int(duration.total_seconds())
        
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark task as failed."""
        self.status = AnalysisStatus.FAILED
        self.completed_at = timezone.now()
        
        if error_message:
            self.error_message = error_message
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration = int(duration.total_seconds())
        
        self.save()


class AnalysisInsight(TimestampedModel):
    """Store structured insights from analysis."""
    
    analysis = models.ForeignKey(
        Analysis, 
        on_delete=models.CASCADE, 
        related_name='insights'
    )
    insight_type = models.CharField(
        max_length=50,
        choices=[
            ('tactical_pattern', 'Tactical Pattern'),
            ('player_performance', 'Player Performance'),
            ('team_dynamics', 'Team Dynamics'),
            ('key_moments', 'Key Moments'),
            ('statistical_summary', 'Statistical Summary'),
            ('recommendation', 'Recommendation')
        ]
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    importance_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium'
    )
    metadata = models.JSONField(default=dict)  # Additional insight data
    
    class Meta:
        verbose_name = 'Analysis Insight'
        verbose_name_plural = 'Analysis Insights'
        ordering = ['-importance_level', '-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.insight_type})"


class AnalysisMetrics(TimestampedModel):
    """Store analysis performance metrics."""
    
    analysis = models.OneToOneField(
        Analysis, 
        on_delete=models.CASCADE, 
        related_name='metrics'
    )
    
    # Performance metrics
    total_frames_processed = models.IntegerField(default=0)
    events_detected = models.IntegerField(default=0)
    players_tracked = models.IntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0)  # Overall accuracy
    
    # Processing metrics
    preprocessing_time = models.IntegerField(default=0)  # Seconds
    analysis_time = models.IntegerField(default=0)  # Seconds
    postprocessing_time = models.IntegerField(default=0)  # Seconds
    
    # Resource usage
    cpu_time_used = models.FloatField(default=0.0)  # CPU seconds
    memory_peak_mb = models.IntegerField(default=0)  # Peak memory usage in MB
    
    class Meta:
        verbose_name = 'Analysis Metrics'
        verbose_name_plural = 'Analysis Metrics'
    
    def __str__(self):
        return f"Metrics for {self.analysis}"
    
    @property
    def total_processing_time(self):
        """Get total processing time."""
        return self.preprocessing_time + self.analysis_time + self.postprocessing_time
    
    @property
    def events_per_minute(self):
        """Calculate events detected per minute of video."""
        if self.analysis.video.duration and self.analysis.video.duration > 0:
            minutes = self.analysis.video.duration / 60
            return round(self.events_detected / minutes, 2)
        return 0
