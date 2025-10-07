from django.urls import path, include
from rest_framework import routers
from .views import DocumentTypeViewSet

router = routers.DefaultRouter()
router.register(r"documentType", DocumentTypeViewSet, basename="documentType")
urlpatterns = [
    path("api/v1/", include(router.urls)),
]