from django.shortcuts import render
from rest_framework import viewsets
from .serializer import DocumentTypeSerializer, GenderSerializer, PaymentMethodTypeSerializer
from .models import DocumentType, Gender, PaymentMethodType

class DocumentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()

class GenderViewSet(viewsets.ModelViewSet):
    serializer_class = GenderSerializer
    queryset = Gender.objects.all()

class PaymentMethodTypeViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodTypeSerializer
    queryset = PaymentMethodType.objects.all()