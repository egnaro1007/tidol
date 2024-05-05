from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import Test, BookViewSet, ChapterViewSet, BookmarkViewSet, CommentView, ReviewView, QueryView, QueryAuthorView, QueryBookView, HistoryView, GetRecentUpdatesView, FollowView

router = SimpleRouter()
router.register(r'book', BookViewSet, basename='book')
router.register(r'chapter', ChapterViewSet, basename='chapter')
router.register(r'bookmark', BookmarkViewSet, basename='bookmark')

urlpatterns = [
                  path('test', Test.as_view(), name='test'),
                  path('search', QueryView.as_view(), name='search'),
                  path('search/author', QueryAuthorView.as_view(), name='search-author'),
                  path('search/book', QueryBookView.as_view(), name='search-book'),
                  
                  path('comment/<int:id>/', CommentView.as_view(), name='comment'),
                  path('review/<int:id>/', ReviewView.as_view(), name='review'),

                  path('history/', HistoryView.as_view(), name='history'),
                  path('follow/', FollowView.as_view(), name='follow'),
                  path('recentUpdates/', GetRecentUpdatesView.as_view(), name='recent-updates'),
              ] + router.urls
