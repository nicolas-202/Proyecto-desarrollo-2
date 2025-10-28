from django.urls import path, include
from rest_framework import routers
from .views import PrizeTypeSerializer, StateRaffleSerializer


router = routers.DefaultRouter()
router.register(r"prizetype", PrizeTypeSerializer, basename="prize-type")
router.register(r"staterife", StateRaffleSerializer, basename="state-raffle")
urlpatterns = [
    path("", include(router.urls)),
]