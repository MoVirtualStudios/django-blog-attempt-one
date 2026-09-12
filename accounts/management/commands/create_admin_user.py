import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create a production superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Admin user environment variables are missing. Skipping admin user creation."
                )
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()

            Profile.objects.get_or_create(
                user=user,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created superuser: {username}"
                )
            )
            return

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.save()

        Profile.objects.get_or_create(
            user=user,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser already exists. Permissions checked for: {username}"
            )
        )