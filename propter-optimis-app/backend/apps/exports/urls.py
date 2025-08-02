"""
Exports URLs for Propter-Optimis Sports Analytics Platform.
"""
from django.urls import path

from .views import (
    ExportListCreateView,
    ExportDetailView,
    ExportShareView,
    download_export,
    shared_export_view,
    export_templates,
    export_statistics,
    retry_export
)

app_name = 'exports'

urlpatterns = [
    # Export CRUD operations
    path('', ExportListCreateView.as_view(), name='export_list_create'),
    path('<uuid:pk>/', ExportDetailView.as_view(), name='export_detail'),
    
    # Export operations
    path('<uuid:export_id>/download/', download_export, name='download_export'),
    path('<uuid:export_id>/retry/', retry_export, name='retry_export'),
    
    # Export sharing
    path('shares/', ExportShareView.as_view(), name='export_shares'),
    path('shared/<str:share_token>/', shared_export_view, name='shared_export'),
    
    # Export utilities
    path('templates/', export_templates, name='export_templates'),
    path('statistics/', export_statistics, name='export_statistics'),
]
