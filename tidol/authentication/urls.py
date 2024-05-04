from django.urls import path
from rest_framework_simplejwt.views import  TokenRefreshView, TokenVerifyView

from .views import CustomTokenObtainPairView
from .views import AuthorProfileAPIView
from .views import RegisterUserAPIView, CheckUsernameAPIView

urlpatterns = [
    path('token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('register', RegisterUserAPIView.as_view(), name='register'),
    path('checkUsername', CheckUsernameAPIView.as_view(), name='check_username'),

    path('author-profile', AuthorProfileAPIView.as_view(), name='author_profile'),
]
