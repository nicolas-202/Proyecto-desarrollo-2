from django.shortcuts import render
from rest_framework import viewsets
from .serializer import DocumentTypeSerializer, GenderSerializer, PaymentMethodTypeSerializer
from .models import DocumentType, Gender, PaymentMethodType
from permissions.permissions import IsAdminOrReadOnly

class BaseUserInfoViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        # Aplicar IsAdminOrReadOnly para todas las acciones
        return [IsAdminOrReadOnly()]

class DocumentTypeViewSet(BaseUserInfoViewSet):
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()

class GenderViewSet(BaseUserInfoViewSet):
    serializer_class = GenderSerializer
    queryset = Gender.objects.all()

class PaymentMethodTypeViewSet(BaseUserInfoViewSet):
    serializer_class = PaymentMethodTypeSerializer
    queryset = PaymentMethodType.objects.all()