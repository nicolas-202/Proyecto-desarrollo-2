from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterUserViewSet, UserProfileViewSet, UserUpdateViewSet, AdminListViewSet,
                    UserBasicListViewSet, AdminUpdateViewSet, TokenObtainPairView, ChangePasswordViewSet, DeleteAccountViewSet)


urlpatterns = [
    path('register/', RegisterUserViewSet.as_view(), name='user_register'), 
    path('me/', UserProfileViewSet.as_view(), name='user_profile'),
    path('update_me/', UserUpdateViewSet.as_view(), name='user_update'),
    path('admin/users/', AdminListViewSet.as_view(), name='admin_list'),
    path('admin/users/<int:pk>/', AdminUpdateViewSet.as_view(), name='admin_update'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordViewSet.as_view(), name='change_password'),
    path('delete-account/', DeleteAccountViewSet.as_view(), name='delete_account'),
    path('list/', UserBasicListViewSet.as_view(), name='user_basic_list'),  # Nueva URL pública
]