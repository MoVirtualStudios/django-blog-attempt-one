from django.conf import settings
from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    bio = models.TextField(
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
    