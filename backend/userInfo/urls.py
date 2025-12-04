from django.urls import include, path
from rest_framework import routers

from .views import (
    DocumentTypeViewSet,
    GenderViewSet,
    PaymentMethodTypeViewSet,
    PaymentMethodViewSet,
)

router = routers.DefaultRouter()
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")
router.register(r"genders", GenderViewSet, basename="gender")
router.register(
    r"payment-method-types", PaymentMethodTypeViewSet, basename="payment-method-type"
)
router.register(r"payment-methods", PaymentMethodViewSet, basename="payment-method")

urlpatterns = [
    path("", include(router.urls)),
]
