"""
Authentication models for Propter-Optimis Sports Analytics Platform.

Integrates with existing Supabase users table:
- id (uuid, primary key)
- email (varchar)
- password_hash (varchar)
- team_name (varchar, nullable)
- created_at (timestamp)
- referral_source (varchar, nullable)
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for Supabase users table."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    """Custom user model that maps to Supabase users table."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')  # Maps to Supabase password_hash
    last_login = models.DateTimeField(blank=True, null=True, db_column='last_login')  # Required by AbstractBaseUser
    team_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(
        max_length=20, 
        choices=[('admin', 'Admin'), ('analyst', 'Analyst'), ('coach', 'Coach')],
        default='analyst'
    )
    subscription_tier = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')],
        default='free'
    )
    referral_source = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Additional fields for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'  # Map to existing Supabase table
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        """Set password using Django's standard method."""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password using Django's standard method."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    def has_perm(self, perm, obj=None):
        """Return True if user has the specified permission."""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """Return True if user has permissions to view the app."""
        return self.is_superuser
    
    def get_full_name(self):
        """Return the user's full name."""
        return self.full_name or self.team_name or self.email
    
    @property
    def short_name(self):
        """Return the user's short name."""
        return self.email.split('@')[0]


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(default=dict)
    subscription_tier = models.CharField(
        max_length=20, 
        choices=[
            ('free', 'Free'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise')
        ],
        default='free'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"
