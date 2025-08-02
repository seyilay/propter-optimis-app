"""
Core admin configuration for Propter-Optimis Sports Analytics Platform.
"""
from django.contrib import admin


class TimestampedModelAdmin(admin.ModelAdmin):
    """Base admin class for timestamped models."""
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_display = ['id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    ordering = ['-created_at']
