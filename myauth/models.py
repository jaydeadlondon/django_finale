from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def user_avatar_path(instance, filename):
    """Функция для генерации пути к аватарке"""
    return f'avatars/user_{instance.user.pk}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()