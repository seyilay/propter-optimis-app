# Django Debug Helper for Video Upload

## Quick Tests to Debug Upload Issue

### 1. Test if Django server is running
```bash
curl http://localhost:8000/
```

### 2. Test the upload endpoint exists
```bash
curl -X POST http://localhost:8000/api/videos/upload/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Test with FormData (simulating frontend)
```bash
curl -X POST http://localhost:8000/api/videos/upload/ \
  -F "title=Test Video" \
  -F "analysis_intent=individual_player_performance" \
  -F "file=@/path/to/test/video.mp4"
```

## Likely Issues & Solutions

### Issue 1: URL Pattern Not Found
**Error**: `404 Not Found`
**Solution**: Add to your Django `urls.py`:

```python
# backend/urls.py (main)
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/videos/', include('apps.videos.urls')),  # Add this
]

# backend/apps/videos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),  # This creates /api/videos/upload/
]
```

### Issue 2: CORS Headers Missing
**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`
**Solution**: Install and configure django-cors-headers:

```bash
pip install django-cors-headers
```

```python
# settings.py
INSTALLED_APPS = [
    'corsheaders',  # Add this
    # ... other apps
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# Allow frontend origin
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]

# For development only
CORS_ALLOW_ALL_ORIGINS = True  # Remove in production
```

### Issue 3: Missing CSRF Token
**Error**: `403 Forbidden - CSRF token missing`
**Solution**: Add CSRF exemption for API or use proper CSRF handling:

```python
# views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@csrf_exempt  # Add this for API endpoints
@api_view(['POST'])
def upload_video(request):
    # ... your view code
```

### Issue 4: JSON vs FormData Content Type
**Error**: `mime type application/json is not supported`
**Solution**: Your Django view should handle multipart/form-data:

```python
@api_view(['POST'])
def upload_video(request):
    try:
        # Access form data, not JSON
        file = request.FILES.get('file')  # Files from FormData
        title = request.data.get('title')  # Data from FormData
        analysis_intent = request.data.get('analysis_intent')
        
        if not file:
            return Response({'error': 'No file provided'}, 
                          status=status.HTTP_400_BAD_REQUEST)
                          
        # ... rest of processing
    except Exception as e:
        return Response({'error': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## Quick Fix for Your Current Error

The "mime type application/json is not supported" error suggests Django is trying to parse JSON but receiving FormData. 

Add this to your Django upload view:

```python
@csrf_exempt
@api_view(['POST'])
def upload_video(request):
    print(f"Content-Type: {request.content_type}")  # Debug line
    print(f"Request data keys: {list(request.data.keys())}")  # Debug line
    print(f"Request FILES keys: {list(request.FILES.keys())}")  # Debug line
    
    try:
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file in request'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        # ... rest of your code
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Debug line
        return Response({'error': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

This will help you see what Django is actually receiving.