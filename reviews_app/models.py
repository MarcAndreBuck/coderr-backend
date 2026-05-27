from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    """
    Model representing a review written by a user for a business user.
    """
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="written_reviews",
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_reviews",
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Ensure that each reviewer can only review a business user once.
        """
        unique_together = ["reviewer", "business_user"]

    def __str__(self):
        """
        Return string representation of the review.
        """
        return f"{self.reviewer.username} -> {self.business_user.username} ({self.rating}/5)"