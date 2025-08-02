# Django Models for Local Development

To test the end-to-end workflow locally, you need these Django models in your backend:

## Video Model (`backend/apps/videos/models.py`)

```python
from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    ANALYSIS_INTENT_CHOICES = [
        ('individual_player_performance', 'Individual Player Performance'),
        ('tactical_phase_analysis', 'Tactical Phase Analysis'),
        ('opposition_scouting', 'Opposition Scouting'),
        ('set_piece_analysis', 'Set Piece Analysis'),
        ('full_match_review', 'Full Match Review'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500)  # Path to uploaded file
    file_size = models.BigIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    analysis_intent = models.CharField(max_length=50, choices=ANALYSIS_INTENT_CHOICES)
    upload_date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in seconds
    
    def __str__(self):
        return self.title
```

## Analysis Model (`backend/apps/analytics/models.py`)

```python
from django.db import models
from apps.videos.models import Video
import uuid

class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='analyses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_time = models.IntegerField(null=True, blank=True)  # Time in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # OpenStarLab Results (JSON field for complex AI data)
    openstarlab_results = models.JSONField(null=True, blank=True)
    
    # AI Insights (JSON field for structured insights)
    ai_insights = models.JSONField(null=True, blank=True)
    
    # Manual annotations
    manual_annotations = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Analysis for {self.video.title}"
```

## Required API Endpoints

### Video Upload Endpoint (`backend/apps/videos/views.py`)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .models import Video
from .serializers import VideoSerializer

@api_view(['POST'])
def upload_video(request):
    try:
        file = request.FILES.get('file')
        title = request.data.get('title')
        description = request.data.get('description', '')
        analysis_intent = request.data.get('analysis_intent')
        
        if not file or not title or not analysis_intent:
            return Response({'error': 'Missing required fields'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Save file
        file_path = default_storage.save(f'videos/{file.name}', file)
        
        # Create video record
        video = Video.objects.create(
            title=title,
            description=description,
            file_path=file_path,
            file_size=file.size,
            uploaded_by=request.user,
            analysis_intent=analysis_intent,
            status='processing'
        )
        
        # Trigger analysis processing here
        # from apps.analytics.tasks import start_analysis
        # start_analysis.delay(video.id)
        
        serializer = VideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_videos(request):
    videos = Video.objects.filter(uploaded_by=request.user).order_by('-upload_date')
    serializer = VideoSerializer(videos, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
def get_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id, uploaded_by=request.user)
        serializer = VideoSerializer(video)
        return Response(serializer.data)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
```

### Analysis Endpoints (`backend/apps/analytics/views.py`)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Analysis
from .serializers import AnalysisSerializer

@api_view(['GET'])
def list_analyses(request):
    analyses = Analysis.objects.filter(
        video__uploaded_by=request.user
    ).select_related('video').order_by('-created_at')
    
    serializer = AnalysisSerializer(analyses, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
def get_analysis(request, analysis_id):
    try:
        analysis = Analysis.objects.select_related('video').get(
            id=analysis_id, 
            video__uploaded_by=request.user
        )
        serializer = AnalysisSerializer(analysis)
        return Response(serializer.data)
    except Analysis.DoesNotExist:
        return Response({'error': 'Analysis not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
```

## URL Configuration

Add these to your `urls.py`:

```python
# backend/apps/videos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('', views.list_videos, name='list_videos'),
    path('<uuid:video_id>/', views.get_video, name='get_video'),
]

# backend/apps/analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('analyses/', views.list_analyses, name='list_analyses'),
    path('analyses/<uuid:analysis_id>/', views.get_analysis, name='get_analysis'),
]

# backend/urls.py (main)
urlpatterns = [
    path('api/videos/', include('apps.videos.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]
```

## Frontend Configuration

Your frontend is already configured for local mode. Make sure these environment variables are set in `app/.env.local`:

```env
VITE_AUTH_MODE=local
VITE_API_URL=http://localhost:8000
```

## Testing the Workflow

1. **Start Django backend**: `python manage.py runserver`
2. **Start React frontend**: `npm run dev`
3. **Login with any credentials** (mock user will be created)
4. **Upload a video** from the Upload page
5. **View analysis results** once processing completes

The frontend will use the Django backend for all operations when `VITE_AUTH_MODE=local`.