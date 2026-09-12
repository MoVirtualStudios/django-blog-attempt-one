from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "website",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
