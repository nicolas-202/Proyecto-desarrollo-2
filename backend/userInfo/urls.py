from django.urls import path, include
from rest_framework import routers
from .views import DocumentTypeViewSet, GenderViewSet, PaymentMethodTypeViewSet

router = routers.DefaultRouter()
router.register(r"documentType", DocumentTypeViewSet, basename="documentType")
router.register(r"gender", GenderViewSet, basename="gender")
router.register(r"paymentMethodType", PaymentMethodTypeViewSet, basename="paymentMethodType")
urlpatterns = [
    path("api/v1/", include(router.urls)),
]