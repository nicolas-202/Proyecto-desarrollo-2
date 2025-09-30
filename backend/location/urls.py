from django.urls import path, include
from rest_framework import routers
from .views import PaisViewSet

router = routers.DefaultRouter()
router.register(r"pais", PaisViewSet)
urlpatterns = [
    path("api/v1/", include(router.urls)),
]