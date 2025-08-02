"""
Exports views for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.db import transaction
from django.db.models import Sum, Count, Q
import logging

from .models import Export, ExportTemplate, ExportCustomization, ExportShare
from .serializers import (
    ExportSerializer,
    ExportCreateSerializer,
    ExportListSerializer,
    ExportTemplateSerializer,
    ExportShareCreateSerializer,
    ExportShareSerializer,
    ExportStatsSerializer
)
from apps.core.utils import create_error_response, create_success_response
from apps.core.models import ExportType
from apps.analytics.models import Analysis


logger = logging.getLogger(__name__)


class ExportListCreateView(generics.ListCreateAPIView):
    """List exports and create new export requests."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get exports for current user's analyses."""
        return Export.objects.filter(
            analysis__video__user=self.request.user
        ).select_related('analysis', 'analysis__video').prefetch_related(
            'customization', 'shares'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == 'POST':
            return ExportCreateSerializer
        return ExportListSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new export request."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    export = serializer.save()
                    
                    # TODO: Trigger export generation task
                    # generate_export_task.delay(export.id)
                    
                    logger.info(f"Export created: {export.id} ({export.export_type})")
                    
                    response_data = ExportSerializer(export).data
                    return create_success_response(
                        'Export generation started',
                        response_data,
                        status.HTTP_201_CREATED
                    )
            
            return create_error_response(
                'Invalid export request',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error creating export: {e}")
            return create_error_response(
                'Failed to start export generation',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an export."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExportSerializer
    
    def get_queryset(self):
        """Get exports for current user's analyses."""
        return Export.objects.filter(
            analysis__video__user=self.request.user
        ).select_related('analysis', 'analysis__video').prefetch_related(
            'customization', 'shares'
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete export and associated files."""
        try:
            export = self.get_object()
            
            # Delete from storage if exists
            if export.file_url:
                # TODO: Delete file from Supabase Storage
                pass
            
            export_id = export.id
            export.delete()
            
            logger.info(f"Export deleted: {export_id}")
            
            return create_success_response('Export deleted successfully')
            
        except Exception as e:
            logger.error(f"Error deleting export: {e}")
            return create_error_response(
                'Failed to delete export',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_export(request, export_id):
    """Download export file."""
    try:
        export = get_object_or_404(
            Export,
            id=export_id,
            analysis__video__user=request.user
        )
        
        if not export.is_completed:
            return create_error_response(
                'Export is not ready for download',
                {'status': export.status},
                status.HTTP_400_BAD_REQUEST
            )
        
        if export.is_expired:
            return create_error_response(
                'Export has expired',
                {},
                status.HTTP_410_GONE
            )
        
        if not export.file_url:
            return create_error_response(
                'Export file not found',
                {},
                status.HTTP_404_NOT_FOUND
            )
        
        # Increment download count
        export.increment_download_count()
        
        # TODO: Generate signed URL for Supabase Storage
        # For now, redirect to the file URL
        logger.info(f"Export downloaded: {export.id} by {request.user.email}")
        
        return create_success_response(
            'Download URL generated',
            {
                'download_url': export.file_url,
                'filename': f"{export.analysis.video.filename}_{export.get_export_type_display()}",
                'file_size': export.formatted_file_size
            }
        )
        
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        return create_error_response(
            'Failed to download export',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExportShareView(APIView):
    """Handle export sharing operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a new export share."""
        try:
            serializer = ExportShareCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                share = serializer.save()
                
                # Generate share URL
                base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
                share_url = share.generate_share_url(base_url)
                
                response_data = ExportShareSerializer(share).data
                response_data['share_url'] = share_url
                
                logger.info(f"Export share created: {share.id} for export {share.export.id}")
                
                return create_success_response(
                    'Export share created',
                    response_data,
                    status.HTTP_201_CREATED
                )
            
            return create_error_response(
                'Invalid share request',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error creating export share: {e}")
            return create_error_response(
                'Failed to create export share',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """List user's export shares."""
        try:
            shares = ExportShare.objects.filter(
                export__analysis__video__user=request.user
            ).select_related('export', 'export__analysis', 'export__analysis__video')
            
            serializer = ExportShareSerializer(shares, many=True)
            
            return create_success_response(
                'Export shares retrieved',
                serializer.data
            )
            
        except Exception as e:
            logger.error(f"Error retrieving export shares: {e}")
            return create_error_response(
                'Failed to retrieve export shares',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow public access
def shared_export_view(request, share_token):
    """View shared export (public access)."""
    try:
        share = get_object_or_404(
            ExportShare,
            share_token=share_token,
            is_active=True
        )
        
        if share.is_expired:
            raise Http404("This share has expired")
        
        # Record access
        share.record_access()
        
        # Return export information based on access level
        export_data = {
            'export_id': str(share.export.id),
            'export_type': share.export.get_export_type_display(),
            'video_filename': share.export.analysis.video.filename,
            'created_at': share.export.created_at,
            'file_size': share.export.formatted_file_size,
            'access_level': share.access_level
        }
        
        # Include download URL if user has download access
        if share.access_level in ['download', 'full'] and share.export.file_url:
            export_data['download_url'] = share.export.file_url
        
        return create_success_response(
            'Shared export retrieved',
            export_data
        )
        
    except Http404:
        return create_error_response(
            'Shared export not found or expired',
            {},
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error accessing shared export: {e}")
        return create_error_response(
            'Failed to access shared export',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_templates(request):
    """Get available export templates."""
    try:
        templates = ExportTemplate.objects.filter(is_active=True)
        serializer = ExportTemplateSerializer(templates, many=True)
        
        return create_success_response(
            'Export templates retrieved',
            serializer.data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving export templates: {e}")
        return create_error_response(
            'Failed to retrieve export templates',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_statistics(request):
    """Get user's export statistics."""
    try:
        user_exports = Export.objects.filter(
            analysis__video__user=request.user
        )
        
        stats = {
            'total_exports': user_exports.count(),
            'pdf_exports': user_exports.filter(
                export_type=ExportType.PDF_REPORT
            ).count(),
            'csv_exports': user_exports.filter(
                export_type=ExportType.CSV_DATA
            ).count(),
            'video_exports': user_exports.filter(
                export_type=ExportType.VIDEO_CLIPS
            ).count(),
            'completed_exports': user_exports.filter(
                status='completed'
            ).count(),
            'failed_exports': user_exports.filter(
                status='failed'
            ).count(),
            'total_downloads': user_exports.aggregate(
                total=Sum('download_count')
            )['total'] or 0,
            'total_shares': ExportShare.objects.filter(
                export__analysis__video__user=request.user
            ).count(),
            'active_shares': ExportShare.objects.filter(
                export__analysis__video__user=request.user,
                is_active=True
            ).count(),
            'storage_used_mb': 0  # TODO: Calculate actual storage usage
        }
        
        # Calculate storage usage
        storage_bytes = user_exports.filter(
            status='completed',
            file_size__isnull=False
        ).aggregate(total=Sum('file_size'))['total'] or 0
        
        stats['storage_used_mb'] = round(storage_bytes / (1024 * 1024), 2)
        
        return create_success_response(
            'Export statistics retrieved',
            stats
        )
        
    except Exception as e:
        logger.error(f"Error retrieving export statistics: {e}")
        return create_error_response(
            'Failed to retrieve export statistics',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_export(request, export_id):
    """Retry failed export."""
    try:
        export = get_object_or_404(
            Export,
            id=export_id,
            analysis__video__user=request.user
        )
        
        if not export.is_failed:
            return create_error_response(
                'Export is not in failed state',
                {'current_status': export.status},
                status.HTTP_400_BAD_REQUEST
            )
        
        # Reset export state
        export.status = 'pending'
        export.error_message = None
        export.file_url = None
        export.file_size = None
        export.save()
        
        # TODO: Trigger export generation task
        # generate_export_task.delay(export.id)
        
        logger.info(f"Export retry initiated: {export.id}")
        
        return create_success_response(
            'Export retry initiated',
            ExportSerializer(export).data
        )
        
    except Exception as e:
        logger.error(f"Error retrying export: {e}")
        return create_error_response(
            'Failed to retry export',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
