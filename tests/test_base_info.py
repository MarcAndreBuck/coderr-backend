from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        average_rating = Review.objects.aggregate(
            average_rating=Avg("rating")
        )["average_rating"]

        rounded_rating = (
            round(average_rating, 1)
            if average_rating
            else 0
        )

        return Response(
            {
                "review_count": Review.objects.count(),
                "average_rating": rounded_rating,
                "business_profile_count": UserProfile.objects.filter(
                    user_type="business"
                ).count(),
                "offer_count": Offer.objects.count(),
            }
        )
