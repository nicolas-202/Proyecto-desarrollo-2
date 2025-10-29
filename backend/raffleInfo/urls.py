from django.urls import path, include
from rest_framework import routers
from .views import PrizeTypeViewSet, StateRaffleViewSet


router = routers.DefaultRouter()
router.register(r"prizetype", PrizeTypeViewSet, basename="prize-type")
router.register(r"staterife", StateRaffleViewSet, basename="state-raffle")

urlpatterns = [
    path("", include(router.urls)),
]