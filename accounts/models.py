"""
Models for user accounts, profiles, and follow relationships.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extended user profile.
    Each User has one Profile created automatically.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='نبذة عني')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'الملف الشخصي'
        verbose_name_plural = 'الملفات الشخصية'

    def __str__(self):
        return f'ملف {self.user.username}'

    @property
    def followers_count(self):
        """Number of users following this user."""
        return self.user.followers.count()

    @property
    def following_count(self):
        """Number of users this user follows."""
        return self.user.following.count()


class Follow(models.Model):
    """
    Follow relationship between users.
    follower follows following.
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='المتابِع'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='المتابَع'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'متابعة'
        verbose_name_plural = 'المتابعات'
        unique_together = ('follower', 'following')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower.username} يتابع {self.following.username}'


# Signal to create Profile automatically when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
