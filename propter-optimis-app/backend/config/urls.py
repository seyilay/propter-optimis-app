"""
URL configuration for Propter-Optimis Sports Analytics Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({
        'status': 'healthy',
        'message': 'Propter-Optimis Sports Analytics API is running',
        'version': '1.0.0'
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API v1
    path('api/auth/', include('apps.authentication.urls')),
    path('api/videos/', include('apps.videos.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/exports/', include('apps.exports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin
admin.site.site_header = 'Propter-Optimis Sports Analytics'
admin.site.site_title = 'Propter-Optimis Admin'
admin.site.index_title = 'Sports Analytics Administration'
