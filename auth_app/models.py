from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Model representing a user profile with additional information.
    """
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=30, blank=True, default="")
    last_name = models.CharField(max_length=30, blank=True, default="")
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, default="")
    tel = models.CharField(max_length=15, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        """
        Return string representation of the user profile.
        """
        return f"{self.user.username} - {self.user_type}"
