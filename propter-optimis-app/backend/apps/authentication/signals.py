"""
Authentication signals for Propter-Optimis Sports Analytics Platform.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created."""
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
            logger.info(f"Profile created for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.email}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.email}: {e}")
