"""
Analytics admin configuration for Propter-Optimis Sports Analytics Platform.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count

from .models import Analysis, AnalysisTask, AnalysisInsight, AnalysisMetrics
from apps.core.admin import TimestampedModelAdmin


class AnalysisTaskInline(admin.TabularInline):
    """Inline admin for analysis tasks."""
    model = AnalysisTask
    extra = 0
    readonly_fields = ['started_at', 'completed_at', 'duration']
    fields = [
        'task_name', 'task_type', 'status', 'started_at', 
        'completed_at', 'duration', 'error_message'
    ]


class AnalysisInsightInline(admin.TabularInline):
    """Inline admin for analysis insights."""
    model = AnalysisInsight
    extra = 0
    readonly_fields = ['created_at']
    fields = [
        'insight_type', 'title', 'importance_level', 
        'confidence_score', 'created_at'
    ]


class AnalysisMetricsInline(admin.StackedInline):
    """Inline admin for analysis metrics."""
    model = AnalysisMetrics
    can_delete = False
    readonly_fields = ['total_processing_time', 'events_per_minute']
    fields = [
        ('total_frames_processed', 'events_detected', 'players_tracked'),
        ('accuracy_score', 'total_processing_time', 'events_per_minute'),
        ('preprocessing_time', 'analysis_time', 'postprocessing_time'),
        ('cpu_time_used', 'memory_peak_mb')
    ]


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    """Admin configuration for Analysis model."""
    
    inlines = [AnalysisTaskInline, AnalysisInsightInline, AnalysisMetricsInline]
    
    list_display = [
        'video', 'status', 'progress_bar', 'formatted_processing_time',
        'insights_count', 'created_at', 'completed_at'
    ]
    list_filter = [
        'status', 'video__analysis_intent', 'created_at', 'completed_at'
    ]
    search_fields = [
        'video__filename', 'video__user__email', 'video__user__team_name'
    ]
    readonly_fields = [
        'id', 'created_at', 'formatted_processing_time', 'progress_bar',
        'insights_count', 'results_preview'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('video', 'status', 'progress_percentage', 'progress_bar')
        }),
        ('Processing Details', {
            'fields': (
                'started_at', 'completed_at', 'processing_time', 
                'formatted_processing_time', 'current_step'
            )
        }),
        ('Results', {
            'fields': ('insights_count', 'results_preview', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('openstarlab_results', 'ai_insights'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def progress_bar(self, obj):
        """Display progress as a visual bar."""
        progress = obj.progress_percentage
        
        if obj.status == 'failed':
            color = 'red'
        elif obj.status == 'completed':
            color = 'green'
        elif obj.status == 'processing':
            color = 'blue'
        else:
            color = 'gray'
        
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; border-radius:3px;">'  
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; text-align:center; color:white; font-size:12px; line-height:20px;">'  
            '{}%</div></div>',
            progress, color, progress
        )
    progress_bar.short_description = 'Progress'
    
    def insights_count(self, obj):
        """Display number of insights generated."""
        count = obj.insights.count()
        if count > 0:
            url = reverse('admin:analytics_analysisinsight_changelist')
            return format_html(
                '<a href="{}?analysis__id__exact={}">{} insights</a>',
                url, obj.id, count
            )
        return '0 insights'
    insights_count.short_description = 'Insights'
    
    def results_preview(self, obj):
        """Display preview of analysis results."""
        if obj.openstarlab_results:
            results = obj.openstarlab_results
            preview = f"Events: {results.get('events_detected', 0)}<br>"
            preview += f"Key Moments: {len(results.get('key_moments', []))}<br>"
            preview += f"Tactical Insights: {len(results.get('tactical_insights', []))}"
            return format_html(preview)
        return 'No results available'
    results_preview.short_description = 'Results Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'video', 'video__user'
        ).prefetch_related('insights', 'tasks')


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(TimestampedModelAdmin):
    """Admin configuration for AnalysisTask model."""
    
    list_display = [
        'analysis', 'task_name', 'task_type', 'status', 
        'duration_display', 'started_at', 'completed_at'
    ]
    list_filter = ['task_type', 'status', 'started_at']
    search_fields = [
        'task_name', 'analysis__video__filename', 
        'analysis__video__user__email'
    ]
    readonly_fields = ['duration']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('analysis', 'task_name', 'task_type', 'status')
        }),
        ('Execution Details', {
            'fields': ('started_at', 'completed_at', 'duration', 'error_message')
        }),
        ('Results', {
            'fields': ('result_data',),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        """Display duration in human readable format."""
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return '-'
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'analysis', 'analysis__video', 'analysis__video__user'
        )


@admin.register(AnalysisInsight)
class AnalysisInsightAdmin(TimestampedModelAdmin):
    """Admin configuration for AnalysisInsight model."""
    
    list_display = [
        'title', 'analysis', 'insight_type', 'importance_level',
        'confidence_score', 'created_at'
    ]
    list_filter = [
        'insight_type', 'importance_level', 'confidence_score', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'analysis__video__filename',
        'analysis__video__user__email'
    ]
    
    fieldsets = (
        ('Insight Information', {
            'fields': ('analysis', 'insight_type', 'title', 'description')
        }),
        ('Scoring', {
            'fields': ('importance_level', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'analysis', 'analysis__video', 'analysis__video__user'
        )


@admin.register(AnalysisMetrics)
class AnalysisMetricsAdmin(TimestampedModelAdmin):
    """Admin configuration for AnalysisMetrics model."""
    
    list_display = [
        'analysis', 'events_detected', 'players_tracked', 'accuracy_score',
        'total_processing_time_display', 'events_per_minute'
    ]
    list_filter = ['accuracy_score', 'created_at']
    search_fields = [
        'analysis__video__filename', 'analysis__video__user__email'
    ]
    readonly_fields = ['total_processing_time', 'events_per_minute']
    
    fieldsets = (
        ('Analysis Reference', {
            'fields': ('analysis',)
        }),
        ('Performance Metrics', {
            'fields': (
                'total_frames_processed', 'events_detected', 
                'players_tracked', 'accuracy_score'
            )
        }),
        ('Processing Time', {
            'fields': (
                'preprocessing_time', 'analysis_time', 'postprocessing_time',
                'total_processing_time'
            )
        }),
        ('Resource Usage', {
            'fields': ('cpu_time_used', 'memory_peak_mb')
        }),
        ('Calculated Metrics', {
            'fields': ('events_per_minute',),
            'classes': ('collapse',)
        })
    )
    
    def total_processing_time_display(self, obj):
        """Display total processing time in human readable format."""
        total_time = obj.total_processing_time
        if total_time:
            minutes = total_time // 60
            seconds = total_time % 60
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return '-'
    total_processing_time_display.short_description = 'Total Processing Time'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'analysis', 'analysis__video', 'analysis__video__user'
        )
