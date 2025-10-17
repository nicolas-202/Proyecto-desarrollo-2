from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializer import (RegisterUserSerializer, UserProfileSerializer, UserUpdateSerializer,
                        AdminUpdateSerializer, CustomTokenObtainPairSerializer, ChangePasswordSerializer, DeleteAccountSerializer)
from permissions.permissions import IsAdminUser, IsNotAdminUser, IsNotAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.

#Vista para crear usuarios (registro)
class RegisterUserViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [IsNotAuthenticated]  # Cualquiera puede registrarse
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {
            "message": "Usuario registrado exitosamente",
            "user": serializer.data
        }
        return Response(response_data, 
                        status=status.HTTP_201_CREATED,
                        headers=headers
        )

#Vista para obtener el perfil del usuario autenticado
class UserProfileViewSet(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
#Vista para actualizar el perfil del usuario autenticado
class UserUpdateViewSet(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
#Vista para que el admin pueda listar usuarios y buscar por email, id o document_number
class AdminListViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'id', 'document_number']

    def get_queryset(self):
        return User.objects.all().order_by('id')

#Vista para que el admin pueda actualizar usuarios
class AdminUpdateViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_update(self, serializer):
        try:
            old_data = {'is_admin': serializer.instance.is_admin, 'is_active': serializer.instance.is_active}
            serializer.save()
            changes = []
            if old_data['is_admin'] != serializer.instance.is_admin:
                changes.append(f"is_admin cambiado a {serializer.instance.is_admin}")
            if old_data['is_active'] != serializer.instance.is_active:
                changes.append(f"is_active cambiado a {serializer.instance.is_active}")
            return Response({
                "message": f"Usuario actualizado (ID: {serializer.instance.id}). Cambios: {', '.join(changes) if changes else 'ninguno'}",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except serializer.ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#Vista para que el usuario autenticado pueda cambiar su contraseña
class ChangePasswordViewSet(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Contraseña actualizada exitosamente"
        }, status=status.HTTP_200_OK)
    
class DeleteAccountViewSet(generics.GenericAPIView):
    serializer_class = DeleteAccountSerializer
    permission_classes = [IsAuthenticated, IsNotAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Cuenta desactivada exitosamente"
        }, status=status.HTTP_200_OK)
#Vista personalizada para login
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para login
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer