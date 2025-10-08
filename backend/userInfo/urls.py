from django.urls import path, include
from rest_framework import routers
from .views import DocumentTypeViewSet, GenderViewSet

router = routers.DefaultRouter()
router.register(r"documentType", DocumentTypeViewSet, basename="documentType")
router.register(r"gender", GenderViewSet, basename="gender")
urlpatterns = [
    path("api/v1/", include(router.urls)),
]