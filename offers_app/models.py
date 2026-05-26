from django.contrib.auth.models import User
from django.db import models


class Offer(models.Model):
    """
    Model representing a business offer.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="offer_images/",
        null=True,
        blank=True,
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return string representation of the offer.
        """
        return self.title


class OfferDetail(models.Model):
    """
    Model representing a pricing tier for an offer.
    """
    OFFER_TYPE_CHOICES = (
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    )

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(
        max_length=20,
        choices=OFFER_TYPE_CHOICES,
    )

    def __str__(self):
        """
        Return string representation of the offer detail.
        """
        return f"{self.offer.title} - {self.offer_type}"
