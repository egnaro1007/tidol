from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterUserAPIView, CheckUsernameAPIView

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', RegisterUserAPIView.as_view(), name='register'),
    path('checkUsername', CheckUsernameAPIView.as_view(), name='check_username'),
]