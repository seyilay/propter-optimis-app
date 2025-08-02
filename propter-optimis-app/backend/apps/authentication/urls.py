"""
Authentication URLs for Propter-Optimis Sports Analytics Platform.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    password_reset_request,
    verify_token
)

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', verify_token, name='verify_token'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', password_reset_request, name='password_reset'),
]
