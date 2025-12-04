from django.urls import include, path
from rest_framework import routers

from .views import PrizeTypeViewSet, StateRaffleViewSet

router = routers.DefaultRouter()
router.register(r"prizetype", PrizeTypeViewSet, basename="prize-type")
router.register(r"stateraffle", StateRaffleViewSet, basename="state-raffle")

urlpatterns = [
    path("", include(router.urls)),
]
