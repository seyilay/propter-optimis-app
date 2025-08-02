"""
Exports admin configuration for Propter-Optimis Sports Analytics Platform.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Export, ExportTemplate, ExportCustomization, ExportShare
from apps.core.admin import TimestampedModelAdmin


class ExportCustomizationInline(admin.StackedInline):
    """Inline admin for export customization."""
    model = ExportCustomization
    can_delete = False
    verbose_name_plural = 'Customization'
    fields = [
        ('include_charts', 'include_heatmaps', 'include_timeline'),
        ('include_player_stats', 'include_tactical_analysis'),
        ('clip_duration', 'include_audio', 'video_quality'),
        ('include_raw_data', 'include_calculated_metrics', 'timestamp_format'),
        ('custom_title', 'custom_description', 'include_branding')
    ]


class ExportShareInline(admin.TabularInline):
    """Inline admin for export shares."""
    model = ExportShare
    extra = 0
    readonly_fields = ['share_token', 'accessed_count', 'last_accessed_at', 'is_expired']
    fields = [
        'share_token', 'shared_with_email', 'access_level',
        'expires_at', 'accessed_count', 'is_active'
    ]


@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    """Admin configuration for Export model."""
    
    inlines = [ExportCustomizationInline, ExportShareInline]
    
    list_display = [
        'analysis', 'export_type', 'status_display', 'formatted_file_size',
        'download_count', 'shares_count', 'created_at', 'expires_at'
    ]
    list_filter = [
        'export_type', 'status', 'created_at', 'expires_at'
    ]
    search_fields = [
        'analysis__video__filename', 'analysis__video__user__email'
    ]
    readonly_fields = [
        'id', 'created_at', 'formatted_file_size', 'status_display',
        'shares_count', 'download_link'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('analysis', 'export_type', 'status', 'status_display')
        }),
        ('File Details', {
            'fields': (
                'file_url', 'download_link', 'file_size', 'formatted_file_size'
            )
        }),
        ('Usage Statistics', {
            'fields': ('download_count', 'shares_count', 'expires_at')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def shares_count(self, obj):
        """Display number of shares."""
        count = obj.shares.count()
        if count > 0:
            url = reverse('admin:exports_exportshare_changelist')
            return format_html(
                '<a href="{}?export__id__exact={}">{} shares</a>',
                url, obj.id, count
            )
        return '0 shares'
    shares_count.short_description = 'Shares'
    
    def download_link(self, obj):
        """Display download link if available."""
        if obj.file_url and obj.is_completed:
            return format_html(
                '<a href="{}" target="_blank">Download File</a>',
                obj.file_url
            )
        return 'Not available'
    download_link.short_description = 'Download'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'analysis', 'analysis__video', 'analysis__video__user'
        ).prefetch_related('shares')


@admin.register(ExportTemplate)
class ExportTemplateAdmin(TimestampedModelAdmin):
    """Admin configuration for ExportTemplate model."""
    
    list_display = [
        'name', 'export_type', 'is_default', 'is_active', 'created_at'
    ]
    list_filter = ['export_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['name']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'export_type', 'is_default', 'is_active')
        }),
        ('Configuration', {
            'fields': ('template_config',)
        })
    )


@admin.register(ExportCustomization)
class ExportCustomizationAdmin(TimestampedModelAdmin):
    """Admin configuration for ExportCustomization model."""
    
    list_display = [
        'export', 'custom_title', 'include_charts', 'include_branding'
    ]
    list_filter = [
        'include_charts', 'include_heatmaps', 'include_branding', 'video_quality'
    ]
    search_fields = [
        'export__analysis__video__filename', 'custom_title'
    ]
    
    fieldsets = (
        ('Export Reference', {
            'fields': ('export',)
        }),
        ('PDF Options', {
            'fields': (
                'include_charts', 'include_heatmaps', 'include_timeline',
                'include_player_stats', 'include_tactical_analysis'
            )
        }),
        ('Video Options', {
            'fields': ('clip_duration', 'include_audio', 'video_quality')
        }),
        ('CSV Options', {
            'fields': (
                'include_raw_data', 'include_calculated_metrics', 'timestamp_format'
            )
        }),
        ('General Options', {
            'fields': ('custom_title', 'custom_description', 'include_branding')
        })
    )


@admin.register(ExportShare)
class ExportShareAdmin(TimestampedModelAdmin):
    """Admin configuration for ExportShare model."""
    
    list_display = [
        'export', 'share_token_display', 'shared_with_email', 'access_level',
        'accessed_count', 'is_active', 'is_expired', 'created_at'
    ]
    list_filter = [
        'access_level', 'is_active', 'created_at', 'expires_at'
    ]
    search_fields = [
        'share_token', 'shared_with_email', 'export__analysis__video__filename'
    ]
    readonly_fields = [
        'share_token', 'accessed_count', 'last_accessed_at', 'is_expired'
    ]
    
    fieldsets = (
        ('Share Information', {
            'fields': ('export', 'share_token', 'shared_with_email', 'access_level')
        }),
        ('Access Control', {
            'fields': ('expires_at', 'is_active', 'is_expired')
        }),
        ('Usage Statistics', {
            'fields': ('accessed_count', 'last_accessed_at')
        })
    )
    
    def share_token_display(self, obj):
        """Display truncated share token."""
        return f"{obj.share_token[:8]}..."
    share_token_display.short_description = 'Token'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'export', 'export__analysis', 'export__analysis__video'
        )
