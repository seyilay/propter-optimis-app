"""
Analytics URLs for Propter-Optimis Sports Analytics Platform.
"""
from django.urls import path

from .views import (
    AnalysisListCreateView,
    AnalysisDetailView,
    AnalysisResultsView,
    AnalysisComparisonView,
    analysis_progress,
    retry_analysis,
    cancel_analysis,
    analysis_statistics
)

app_name = 'analytics'

urlpatterns = [
    # Analysis CRUD operations
    path('analyses/', AnalysisListCreateView.as_view(), name='analysis_list_create'),
    path('analyses/<uuid:pk>/', AnalysisDetailView.as_view(), name='analysis_detail'),
    
    # Analysis operations
    path('<uuid:analysis_id>/progress/', analysis_progress, name='analysis_progress'),
    path('<uuid:analysis_id>/retry/', retry_analysis, name='retry_analysis'),
    path('<uuid:analysis_id>/cancel/', cancel_analysis, name='cancel_analysis'),
    path('<uuid:analysis_id>/results/', AnalysisResultsView.as_view(), name='analysis_results'),
    
    # Analysis utilities
    path('compare/', AnalysisComparisonView.as_view(), name='analysis_comparison'),
    path('statistics/', analysis_statistics, name='analysis_statistics'),
]
