from django.shortcuts import render
from rest_framework import viewsets
from .serializer import DocumentTypeSerializer
from .models import DocumentType

class DocumentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()