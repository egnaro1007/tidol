from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import Test, BookViewSet

router = SimpleRouter()
router.register(r'book', BookViewSet, basename='book')

urlpatterns = [
    path('test', Test.as_view(), name='test'),
] + router.urls
