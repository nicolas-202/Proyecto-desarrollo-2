from django.urls import path, include
from rest_framework import routers
from .views import CountryViewSet, StateViewSet, CityViewSet

router = routers.DefaultRouter()
router.register(r"state", StateViewSet, basename="state")
router.register(r"country", CountryViewSet, basename="country")
router.register(r"city", CityViewSet, basename="city")
urlpatterns = [
    path("api/v1/", include(router.urls)),
]