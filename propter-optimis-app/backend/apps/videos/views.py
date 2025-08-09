"""
Video views for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import logging
import uuid
import os

from .models import Video, VideoUploadSession, VideoMetadata
from .serializers import (
    VideoSerializer,
    VideoUploadSerializer,
    VideoUpdateSerializer,
    VideoListSerializer,
    ChunkedUploadSerializer,
    VideoUploadSessionSerializer
)
from apps.core.utils import (
    create_error_response, 
    create_success_response, 
    storage_client,
    generate_unique_filename,
    validate_file_size,
    validate_file_type,
    sanitize_filename
)
from apps.core.models import VideoStatus, AnalysisIntent


logger = logging.getLogger(__name__)


class VideoListCreateView(generics.ListCreateAPIView):
    """List videos and handle video upload."""
    
    permission_classes = [permissions.AllowAny] if settings.DEBUG else [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Get videos for current user."""
        if settings.DEBUG:
            # Local development - show all videos for test user
            test_user_id = "550e8400-e29b-41d4-a716-446655440000"
            return Video.objects.filter(user_id=test_user_id)
        else:
            # Production - TODO: Extract user_id from Supabase token
            user_id = "550e8400-e29b-41d4-a716-446655440000"  # Placeholder
            return Video.objects.filter(user_id=user_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == 'POST':
            return VideoUploadSerializer
        return VideoListSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle video upload."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    # Create video instance
                    video = serializer.save()
                    
                    # Generate unique filename for storage
                    file = request.FILES['file']
                    storage_filename = generate_unique_filename(
                        file.name, 
                        f"videos/{request.user.id}/"
                    )
                    
                    # Upload to Supabase Storage
                    upload_result = storage_client.upload_file(file, storage_filename)
                    
                    if upload_result['success']:
                        # Update video with storage URL
                        video.s3_url = upload_result['public_url']
                        video.status = VideoStatus.PROCESSING
                        video.upload_progress = 100
                        video.save()
                        
                        # TODO: Trigger video processing task
                        # process_video_task.delay(video.id)
                        
                        logger.info(f"Video uploaded successfully: {video.filename} by {request.user.email}")
                        
                        response_data = VideoSerializer(video).data
                        return create_success_response(
                            'Video uploaded successfully',
                            response_data,
                            status.HTTP_201_CREATED
                        )
                    else:
                        # Upload failed, update video status
                        video.status = VideoStatus.ERROR
                        video.error_message = upload_result.get('error', 'Upload failed')
                        video.save()
                        
                        return create_error_response(
                            'Failed to upload video to storage',
                            {'error': upload_result.get('error')},
                            status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            
            return create_error_response(
                'Invalid upload data',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return create_error_response(
                'Video upload failed',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a video."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VideoSerializer
    
    def get_queryset(self):
        """Get videos for current user."""
        return Video.objects.filter(user=self.request.user).select_related(
            'metadata', 'upload_session'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method in ['PUT', 'PATCH']:
            return VideoUpdateSerializer
        return VideoSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Delete video and associated files."""
        try:
            video = self.get_object()
            
            # Delete from storage if exists
            if video.s3_url:
                # Extract file path from URL
                file_path = video.s3_url.split('/')[-1]
                storage_client.delete_file(file_path)
            
            # Delete video record
            video_filename = video.filename
            video.delete()
            
            logger.info(f"Video deleted: {video_filename} by {request.user.email}")
            
            return create_success_response('Video deleted successfully')
            
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return create_error_response(
                'Failed to delete video',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChunkedUploadView(APIView):
    """Handle chunked file upload for large files."""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Handle chunk upload."""
        try:
            serializer = ChunkedUploadSerializer(data=request.data)
            
            if serializer.is_valid():
                chunk_data = serializer.validated_data
                
                # Get or create upload session
                upload_session, created = VideoUploadSession.objects.get_or_create(
                    upload_id=chunk_data['upload_id'],
                    defaults={
                        'total_chunks': chunk_data['total_chunks'],
                        'video': None  # Will be set when first chunk is processed
                    }
                )
                
                # Create video instance on first chunk
                if created and chunk_data['chunk_number'] == 0:
                    video = Video.objects.create(
                        user=request.user,
                        filename=chunk_data['filename'],
                        status=VideoStatus.UPLOADED,
                        upload_progress=0
                    )
                    upload_session.video = video
                    upload_session.save()
                
                # Process chunk
                chunk_file = chunk_data['chunk']
                chunk_number = chunk_data['chunk_number']
                
                # Store chunk temporarily
                # In production, you would upload chunks to storage
                # and combine them when all chunks are received
                
                upload_session.uploaded_chunks = max(
                    upload_session.uploaded_chunks, 
                    chunk_number + 1
                )
                upload_session.save()
                
                # Update video progress
                if upload_session.video:
                    progress = upload_session.progress_percentage
                    upload_session.video.upload_progress = progress
                    upload_session.video.save()
                
                # Check if all chunks are uploaded
                if upload_session.uploaded_chunks >= upload_session.total_chunks:
                    upload_session.mark_completed()
                    
                    # Combine chunks and upload to storage
                    # This is a simplified version - in production you'd
                    # implement proper chunk combining
                    if upload_session.video:
                        upload_session.video.status = VideoStatus.PROCESSING
                        upload_session.video.save()
                        
                        # TODO: Trigger video processing
                        logger.info(f"Chunked upload completed: {upload_session.video.filename}")
                
                response_data = VideoUploadSessionSerializer(upload_session).data
                return create_success_response(
                    'Chunk uploaded successfully',
                    response_data
                )
            
            return create_error_response(
                'Invalid chunk data',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error uploading chunk: {e}")
            return create_error_response(
                'Chunk upload failed',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def video_upload_progress(request, upload_id):
    """Get upload progress for a specific upload session."""
    try:
        upload_session = get_object_or_404(
            VideoUploadSession, 
            upload_id=upload_id,
            video__user=request.user
        )
        
        serializer = VideoUploadSessionSerializer(upload_session)
        
        return create_success_response(
            'Upload progress retrieved',
            serializer.data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving upload progress: {e}")
        return create_error_response(
            'Failed to retrieve upload progress',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_video_processing(request, video_id):
    """Retry video processing for failed videos."""
    try:
        video = get_object_or_404(
            Video, 
            id=video_id, 
            user=request.user
        )
        
        if video.status != VideoStatus.ERROR:
            return create_error_response(
                'Video is not in error state',
                {'current_status': video.status},
                status.HTTP_400_BAD_REQUEST
            )
        
        # Reset video status
        video.status = VideoStatus.PROCESSING
        video.error_message = None
        video.save()
        
        # TODO: Trigger video processing task
        # process_video_task.delay(video.id)
        
        logger.info(f"Video processing retry initiated: {video.filename}")
        
        return create_success_response(
            'Video processing retry initiated',
            VideoSerializer(video).data
        )
        
    except Exception as e:
        logger.error(f"Error retrying video processing: {e}")
        return create_error_response(
            'Failed to retry video processing',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def video_analysis_intents(request):
    """Get available analysis intent options."""
    try:
        intents = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in AnalysisIntent.choices
        ]
        
        return create_success_response(
            'Analysis intents retrieved',
            {'analysis_intents': intents}
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analysis intents: {e}")
        return create_error_response(
            'Failed to retrieve analysis intents',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny] if settings.DEBUG else [permissions.IsAuthenticated])  # Allow any for local dev
def simple_upload_video(request):
    """Simple video upload endpoint for frontend compatibility."""
    try:
        logger.info(f"Upload request received - Content-Type: {request.content_type}")
        logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
        logger.info(f"Request data keys: {list(request.data.keys())}")
        
        # Get file and form data
        file = request.FILES.get('file')
        title = request.data.get('title')
        description = request.data.get('description', '')
        analysis_intent = request.data.get('analysis_intent')
        
        if not file:
            return create_error_response(
                'No file provided',
                {'received_files': list(request.FILES.keys())},
                status.HTTP_400_BAD_REQUEST
            )
        
        if not title:
            return create_error_response(
                'Title is required',
                status.HTTP_400_BAD_REQUEST
            )
        
        # Get user ID from Supabase token or use test ID for local development
        if settings.DEBUG:
            # Local development - use test user ID
            user_id = "550e8400-e29b-41d4-a716-446655440000"  # Fixed test UUID
        else:
            # Production - extract from Supabase JWT token
            # TODO: Implement proper token validation
            user_id = "550e8400-e29b-41d4-a716-446655440000"  # Placeholder
        
        # Validate file
        if not validate_file_size(file):
            return create_error_response(
                'File too large',
                {'max_size': f'{settings.MAX_FILE_SIZE / (1024*1024):.0f}MB'},
                status.HTTP_400_BAD_REQUEST
            )
        
        allowed_types = ['.mp4', '.mov', '.avi', '.mkv']
        if not validate_file_type(file, allowed_types):
            return create_error_response(
                'Invalid file type',
                {'allowed_types': allowed_types},
                status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Create video record
            video = Video.objects.create(
                user_id=user_id,  # Direct Supabase user ID
                filename=file.name,
                title=title,
                description=description,
                file_size=file.size,
                content_type=file.content_type,
                status=VideoStatus.UPLOADED,
                analysis_intent=analysis_intent,
                upload_progress=0
            )
            
            # Choose storage method based on settings
            use_supabase = getattr(settings, 'USE_SUPABASE_STORAGE', True)
            
            if use_supabase:
                # Upload to Supabase Storage
                storage_filename = generate_unique_filename(
                    file.name, 
                    f"videos/{user_id}/"
                )
                
                upload_result = storage_client.upload_file(file, storage_filename)
                
                if upload_result['success']:
                    video.s3_url = upload_result['public_url']
                    video.status = VideoStatus.PROCESSING
                    video.upload_progress = 100
                    video.save()
                    
                    logger.info(f"Video uploaded to Supabase: {video.filename}")
                else:
                    video.status = VideoStatus.ERROR
                    video.error_message = upload_result.get('error', 'Upload failed')
                    video.save()
                    
                    return create_error_response(
                        'Supabase upload failed',
                        {'error': upload_result.get('error')},
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # Save to local storage
                upload_dir = f'media/uploads/videos/{user_id}'
                os.makedirs(upload_dir, exist_ok=True)
                
                safe_filename = sanitize_filename(file.name)
                file_path = os.path.join(upload_dir, safe_filename)
                
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                video.s3_url = f'/media/uploads/videos/{user_id}/{safe_filename}'
                video.status = VideoStatus.PROCESSING
                video.upload_progress = 100
                video.save()
                
                logger.info(f"Video uploaded locally: {video.filename}")
            
            # Return success response
            response_data = {
                'id': str(video.id),
                'video_id': str(video.id),
                'filename': video.filename,
                'status': video.status,
                'upload_progress': video.upload_progress
            }
            
            return create_success_response(
                'Video uploaded successfully',
                response_data,
                status.HTTP_201_CREATED
            )
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return create_error_response(
            'Upload failed',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )