from django.urls import path, include
from rest_framework import routers
from .views import CountryViewSet

router = routers.DefaultRouter()
router.register(r"country", CountryViewSet)
urlpatterns = [
    path("api/v1/", include(router.urls)),
]