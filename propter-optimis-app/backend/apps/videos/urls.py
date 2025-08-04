"""
Video URLs for Propter-Optimis Sports Analytics Platform.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Video CRUD operations
    path('', views.VideoListCreateView.as_view(), name='video_list_create'),
    path('simple-upload/', views.simple_upload_video, name='simple_upload_video'),
    path('<uuid:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    
    # Upload operations
    path('upload/chunked/', views.ChunkedUploadView.as_view(), name='chunked_upload'),
    path('upload/progress/<str:upload_id>/', views.video_upload_progress, name='upload_progress'),
    
    # Video processing
    path('<uuid:video_id>/retry/', views.retry_video_processing, name='retry_processing'),
    
    # Analysis intents
    path('analysis-intents/', views.video_analysis_intents, name='analysis_intents'),
]
