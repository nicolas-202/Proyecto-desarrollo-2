from django.urls import include, path
from rest_framework import routers

from .views import CityViewSet, CountryViewSet, StateViewSet

router = routers.DefaultRouter()
router.register(r"states", StateViewSet, basename="state")
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"cities", CityViewSet, basename="city")
urlpatterns = [
    path("", include(router.urls)),
]
