"""
Core utilities for Propter-Optimis Sports Analytics Platform.
"""
import os
import uuid
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger(__name__)


def generate_unique_filename(original_filename: str, prefix: str = '') -> str:
    """Generate a unique filename with UUID."""
    ext = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}{ext}"


def validate_file_size(file, max_size: int = None) -> bool:
    """Validate file size against maximum allowed size."""
    if max_size is None:
        max_size = settings.MAX_FILE_SIZE
    
    if file.size > max_size:
        return False
    return True


def validate_file_type(file, allowed_types: list) -> bool:
    """Validate file type against allowed types."""
    file_ext = os.path.splitext(file.name)[1].lower()
    return file_ext in allowed_types


def create_error_response(message: str, details: Dict[str, Any] = None, 
                         status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """Create standardized error response."""
    error_data = {
        'error': 'ValidationError' if status_code == 400 else 'ServerError',
        'message': message
    }
    
    if details:
        error_data['details'] = details
    
    return Response(error_data, status=status_code)


def create_success_response(message: str, data: Dict[str, Any] = None,
                          status_code: int = status.HTTP_200_OK) -> Response:
    """Create standardized success response."""
    success_data = {
        'message': message
    }
    
    if data:
        success_data['data'] = data
    
    return Response(success_data, status=status_code)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def calculate_video_duration(video_path: str) -> Optional[int]:
    """Calculate video duration in seconds using OpenCV."""
    try:
        import cv2
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        if fps > 0:
            duration = int(frame_count / fps)
            cap.release()
            return duration
        
        cap.release()
        return None
        
    except Exception as e:
        logger.error(f"Error calculating video duration: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit filename length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}{ext}"


class SupabaseStorageClient:
    """Client for interacting with Supabase Storage."""
    
    def __init__(self):
        self.bucket_name = 'propter-optimis-videos'
        self.supabase_url = settings.SUPABASE_URL
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY
    
    def upload_file(self, file, file_path: str) -> Dict[str, Any]:
        """Upload file to Supabase Storage."""
        try:
            # This would integrate with Supabase Storage API
            # For now, we'll simulate the upload
            logger.info(f"Uploading file to Supabase Storage: {file_path}")
            
            # Simulate successful upload
            return {
                'success': True,
                'file_path': file_path,
                'public_url': f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{file_path}",
                'file_size': file.size
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to Supabase Storage: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase Storage."""
        try:
            logger.info(f"Deleting file from Supabase Storage: {file_path}")
            # Implement actual deletion logic
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from Supabase Storage: {e}")
            return False


# Global instance
storage_client = SupabaseStorageClient()
