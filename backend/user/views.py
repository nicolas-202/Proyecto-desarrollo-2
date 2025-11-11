from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializer import (RegisterUserSerializer, UserProfileSerializer, UserUpdateSerializer, UserBasicSerializer,
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

# Vista pública para listar información básica de usuarios
class UserBasicListViewSet(generics.ListAPIView):
    """
    Vista pública para listar información básica de usuarios
    - Acceso sin autenticación
    - Solo información no sensible
    - Útil para mostrar participantes en rifas, etc.
    """
    queryset = User.objects.filter(is_active=True)  # Solo usuarios activos
    serializer_class = UserBasicSerializer
    permission_classes = [AllowAny]  # Acceso público
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']  # Búsqueda por nombre o email

    def get_queryset(self):
        """
        Filtrar usuarios activos y ordenar por nombre
        - Solo usuarios activos y no administradores para proteger privacidad
        """
        return User.objects.filter(
            is_active=True,
            is_admin=False  # No mostrar admins en la lista pública
        ).select_related(
            # Optimización: no necesitamos relaciones para info básica
        ).order_by('first_name', 'last_name')
    
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
        """
        Actualizar usuario como administrador
        - Registra cambios importantes
        - Maneja errores apropiadamente
        - No permite que un admin se desactive a sí mismo
        """
        # Prevenir que un admin se desactive a sí mismo
        if (serializer.instance == self.request.user and 
            'is_active' in serializer.validated_data and 
            not serializer.validated_data['is_active']):
            raise serializer.ValidationError("No puedes desactivar tu propia cuenta como administrador")
        
        old_data = {
            'is_admin': serializer.instance.is_admin, 
            'is_active': serializer.instance.is_active
        }
        serializer.save()
        
        # Registrar cambios importantes
        changes = []
        if old_data['is_admin'] != serializer.instance.is_admin:
            changes.append(f"is_admin cambiado a {serializer.instance.is_admin}")
        if old_data['is_active'] != serializer.instance.is_active:
            changes.append(f"is_active cambiado a {serializer.instance.is_active}")
        
        # Nota: perform_update no debe retornar Response, eso se maneja en el GenericAPIView
        

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
    """
    Vista para que un usuario desactive su propia cuenta
    - Solo usuarios no-admin pueden desactivar su cuenta
    - Requiere confirmación por contraseña
    """
    serializer_class = DeleteAccountSerializer
    permission_classes = [IsAuthenticated, IsNotAdminUser]

    def post(self, request, *args, **kwargs):
        # Verificar que el usuario no tenga rifas activas como organizador
        if hasattr(request.user, 'organized_raffles') and request.user.organized_raffles.filter(status='active').exists():
            return Response({
                "error": "No puedes desactivar tu cuenta mientras tengas rifas activas como organizador"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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