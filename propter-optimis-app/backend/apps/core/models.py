"""
Core models for Propter-Optimis Sports Analytics Platform.
"""
from django.db import models
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """Abstract base class with timestamp fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class AnalysisStatus(models.TextChoices):
    """Choices for analysis status."""
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class VideoStatus(models.TextChoices):
    """Choices for video status."""
    UPLOADED = 'uploaded', 'Uploaded'
    PROCESSING = 'processing', 'Processing'
    READY = 'ready', 'Ready'
    ERROR = 'error', 'Error'


class AnalysisIntent(models.TextChoices):
    """Choices for analysis intent types."""
    INDIVIDUAL_PLAYER = 'individual_player', 'Individual Player Performance'
    TACTICAL_PHASE = 'tactical_phase', 'Tactical Phase Analysis'
    OPPOSITION_SCOUTING = 'opposition_scouting', 'Opposition Scouting'
    SET_PIECE = 'set_piece', 'Set Piece Analysis'
    FULL_MATCH = 'full_match', 'Full Match Review'


class ExportType(models.TextChoices):
    """Choices for export types."""
    PDF_REPORT = 'pdf_report', 'PDF Report'
    CSV_DATA = 'csv_data', 'CSV Data'
    VIDEO_CLIPS = 'video_clips', 'Video Clips'
    FULL_ANALYSIS = 'full_analysis', 'Full Analysis Package'
