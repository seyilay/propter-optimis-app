"""
Authentication views for Propter-Optimis Sports Analytics Platform.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer
)
from apps.core.utils import create_error_response, create_success_response


logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """Handle user registration."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Add custom claims
                access_token['email'] = user.email
                access_token['team_name'] = user.team_name
                access_token['user_id'] = str(user.id)
                
                response_data = {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }
                }
                
                logger.info(f"User registered successfully: {user.email}")
                return create_success_response(
                    'User registered successfully',
                    response_data,
                    status.HTTP_201_CREATED
                )
                
            except Exception as e:
                logger.error(f"Error during user registration: {e}")
                return create_error_response(
                    'Registration failed',
                    {'error': str(e)},
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return create_error_response(
            'Invalid registration data',
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view."""
    
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Obtain JWT token pair."""
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info(f"User logged in successfully: {request.data.get('email')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return create_error_response(
                'Login failed',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLogoutView(APIView):
    """Handle user logout."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            logger.info(f"User logged out successfully: {request.user.email}")
            
            return create_success_response('Logged out successfully')
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return create_error_response(
                'Logout failed',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """Handle user profile operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user profile."""
        try:
            user = request.user
            serializer = UserSerializer(user)
            
            return create_success_response(
                'Profile retrieved successfully',
                serializer.data
            )
            
        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return create_error_response(
                'Failed to retrieve profile',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request):
        """Update user profile."""
        try:
            user = request.user
            user_serializer = UserSerializer(user, data=request.data, partial=True)
            
            # Handle profile data separately
            profile_data = request.data.get('profile', {})
            profile_serializer = UserProfileSerializer(
                user.profile, 
                data=profile_data, 
                partial=True
            )
            
            if user_serializer.is_valid() and profile_serializer.is_valid():
                user_serializer.save()
                profile_serializer.save()
                
                updated_user = UserSerializer(user).data
                
                logger.info(f"User profile updated: {user.email}")
                return create_success_response(
                    'Profile updated successfully',
                    updated_user
                )
            
            errors = {}
            if not user_serializer.is_valid():
                errors.update(user_serializer.errors)
            if not profile_serializer.is_valid():
                errors['profile'] = profile_serializer.errors
            
            return create_error_response(
                'Invalid profile data',
                errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return create_error_response(
                'Failed to update profile',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordChangeView(APIView):
    """Handle password change."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change user password."""
        try:
            serializer = PasswordChangeSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                
                logger.info(f"Password changed for user: {request.user.email}")
                return create_success_response('Password changed successfully')
            
            return create_error_response(
                'Invalid password data',
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return create_error_response(
                'Failed to change password',
                {'error': str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """Request password reset."""
    try:
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Here you would typically send a password reset email
            # For now, we'll just log the request
            logger.info(f"Password reset requested for: {email}")
            
            return create_success_response(
                'If an account with this email exists, you will receive a password reset link.'
            )
        
        return create_error_response(
            'Invalid email',
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f"Error processing password reset request: {e}")
        return create_error_response(
            'Failed to process password reset request',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """Verify JWT token validity."""
    try:
        user = request.user
        user_data = UserSerializer(user).data
        
        return create_success_response(
            'Token is valid',
            {'user': user_data}
        )
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return create_error_response(
            'Token verification failed',
            {'error': str(e)},
            status.HTTP_401_UNAUTHORIZED
        )
