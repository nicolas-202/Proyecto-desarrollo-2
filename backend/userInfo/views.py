from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import (
    DocumentTypeSerializer, GenderSerializer, 
    PaymentMethodTypeSerializer, PaymentMethodSerializer
)
from .models import DocumentType, Gender, PaymentMethodType, PaymentMethod
from permissions.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

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

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para métodos de pago con restricciones de seguridad
    El saldo NO es accesible a través de la API
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Filtrar métodos de pago según el usuario
        """
        if self.request.user.is_admin:
            # Los administradores pueden ver todos los métodos de pago
            return PaymentMethod.objects.filter(payment_method_is_active=True)
        else:
            # Los usuarios solo ven sus propios métodos de pago
            return PaymentMethod.objects.filter(
                user=self.request.user,
                payment_method_is_active=True
            )

    def perform_create(self, serializer):
        """Asignar el usuario actual al crear"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """
        Desactivar método de pago (soft delete)
        PATCH /api/userinfo/payment-methods/{id}/deactivate/
        """
        payment_method = self.get_object()
        payment_method.payment_method_is_active = False
        payment_method.save()
        
        return Response({
            'message': 'Método de pago desactivado correctamente'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def verify_card(self, request, pk=None):
        """
        Verificar número de tarjeta
        POST /api/userinfo/payment-methods/{id}/verify_card/
        Body: {"card_number": "1234567890123456"}
        """
        payment_method = self.get_object()
        card_number = request.data.get('card_number', '')
        
        if not card_number:
            return Response(
                {'error': 'Se requiere el número de tarjeta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid = payment_method.check_card_number(card_number)
        
        return Response({
            'is_valid': is_valid,
            'message': 'Número válido' if is_valid else 'Número inválido'
        })

    @action(detail=True, methods=['post'])
    def check_balance(self, request, pk=None):
        """
        Verificar si hay saldo suficiente para un monto
        POST /api/userinfo/payment-methods/{id}/check_balance/
        Body: {"amount": "100.50"}
        """
        payment_method = self.get_object()
        
        try:
            amount = float(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Monto inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_sufficient = payment_method.has_sufficient_balance(amount)
        
        return Response({
            'has_sufficient_balance': has_sufficient,
            'message': 'Saldo suficiente' if has_sufficient else 'Saldo insuficiente'
            # NOTA: No devolvemos el saldo real por seguridad
        })