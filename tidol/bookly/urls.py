from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import Test, BookViewSet, ChapterViewSet

router = SimpleRouter()
router.register(r'book', BookViewSet, basename='book')
router.register(r'chapter', ChapterViewSet, basename='chapter')

urlpatterns = [
    path('test', Test.as_view(), name='test'),
] + router.urls
