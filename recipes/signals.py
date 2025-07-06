from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Check if profile exists first
        #if hasattr(instance, 'profile_users'):
         #   instance.profile_users.save()
        UserProfile.objects.get_or_create(user=instance)
        instance.profile_users.save()  # This assumes related_name='profile_users'


