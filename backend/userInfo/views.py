from django.shortcuts import render
from rest_framework import viewsets
from .serializer import DocumentTypeSerializer, GenderSerializer
from .models import DocumentType, Gender

class DocumentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()

class GenderViewSet(viewsets.ModelViewSet):
    serializer_class = GenderSerializer
    queryset = Gender.objects.all()