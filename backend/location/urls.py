from django.urls import path, include
from rest_framework import routers
from .views import CountryViewSet, StateViewSet, CityViewSet

router = routers.DefaultRouter()
router.register(r"states", StateViewSet, basename="state")
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"cities", CityViewSet, basename="city")
urlpatterns = [
    path("", include(router.urls)),
]