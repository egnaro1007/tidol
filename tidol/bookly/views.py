from rest_framework import views
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict
from django.shortcuts import get_object_or_404

from .models import Author, Book, Chapter, Comment, Review, Bookmark, CustomUser, Follow, History
from .permissions import IsAuthor, IsAuthorOf
from .serializers import AuthorSerializer, BookSerializer, BookDetailSerializer, ChapterSerializer, CommentSerializer, ReviewSerializer, BookmarkSerializer, FollowSerializer, HistorySerializer


class Test(views.APIView):
    def get(self, request, format=None):
        return Response({'message': 'Hello, World!'})


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    pagination_class=PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return BookDetailSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'list', ]:
            return [permissions.AllowAny(), ]
        elif self.action == 'create':
            return [IsAuthor(), ]
        return [IsAuthorOf(), ]

    # POST
    def create(self, request, *args, **kwargs):
        user = request.user

        try:
            author = Author.objects.get(user=user)
        except Author.DoesNotExist:
            return Response({'error': 'Not an author'}, status=status.HTTP_404_NOT_FOUND)

        book_data = QueryDict('', mutable=True)
        book_data.update(request.data)
        book_data['author'] = author.id

        serializer = BookSerializer(data=book_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # PUT
    def update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # PATCH
    def partial_update(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # GET
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()

    serializer_class = ChapterSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.AllowAny(), ]
        elif self.action == 'create':
            return [IsAuthor(), ]
        return [IsAuthorOf(), ]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                history_record = History(user=user, chapter=self.get_object())
                history_record.save() 
            except History.DoesNotExist:
                History.objects.create(user=user, chapter=self.get_object())
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        if 'book' in request.data and request.data['book'] != self.get_object().book.id:
            raise serializers.ValidationError(
                {'error': 'The book which this chapter belongs to cannot be changed after creation.'})
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'create', ]:
            return [permissions.IsAuthenticated(), ]
        elif self.action in ['list', 'destroy', ]:
            return [IsAuthorOf(), ]
        return [permissions.IsAdminUser(), ]

    def create(self, request, *args, **kwargs):
        user = request.user
        chapter_id = request.data.get('chapter')
        chapter = get_object_or_404(Chapter, pk=chapter_id)
        page = request.data.get('page')

        if page is None:
            page = 0
        elif page < 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        bookmark = Bookmark.objects.create(user=user, chapter=chapter, page=page)
        serializers = BookmarkSerializer(bookmark)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user = request.user
        bookmarks = Bookmark.objects.filter(user=user)

        serializers = BookmarkSerializer(bookmarks, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    # PUT
    def update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = request.user

        try:
            user = CustomUser.objects.get(user=user)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Not an user'}, status=status.HTTP_404_NOT_FOUND)

        # if user is not request.user:
        #     return Response({'User f{user.id} is not the user who bookmarked'}, status=status.HTTP_403_FORBIDDEN)
        
        bookmark_data = QueryDict('', mutable=True)
        bookmark_data.update(request.data)
        bookmark_data['user'] = user.id

        serializer = BookmarkSerializer(data=bookmark_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    # PATCH
    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.data['user'] == self.get_object().user.id:
            raise serializers.ValidationError(
                {'error': 'The user is different from the user bookmarked the chapter.'})
        if request.data['chapter'] != self.get_object().chapter.id:
            raise serializers.ValidationError(
                {'error': 'The chapter id is different from the chapter recorded.'})
    
    # DELETE
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentView(views.APIView):
    # Send comment
    def post(self, request, id, format=None):
        chapter_id = id
        user = request.user
        parrent_comment_id = request.data.get('parent_comment', None)
        text = request.data.get('text')

        try:
            chapter = Chapter.objects.get(pk=chapter_id)
            if parrent_comment_id:
                parent_comment = Comment.objects.get(pk=parrent_comment_id)
        except Chapter.DoesNotExist:
            return Response({'error': 'Chapter not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            parent_comment = None

        comment = Comment.objects.create(chapter=chapter, user=user, parent_comment=parent_comment, text=text)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Delete comment
    def delete(self, request, id, format=None):
        user = request.user
        comment_id = id
        
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Retrieve comments
    def get(self, request, id, format=None):
        chapter_id = id
        
        try:
            comments = Comment.objects.filter(chapter=chapter_id)
        except Chapter.DoesNotExist:
            chapter = get_object_or_404(Chapter, pk=chapter_id)
            return Response([], status=status.HTTP_200_OK)
        
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), ]
        elif self.request.method == 'DELETE':
            return [IsAuthorOf(), ]
        elif self.request.method == 'GET':
            return [permissions.AllowAny(), ]
        return super().get_permissions()
    
    # User review a book
    def post(self, request, id, format=None):
        book_id = id
        user = request.user
        score = request.data.get('score')
        comment = request.data.get('comment', None)
        
        # Check if the book is exist
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Check if the score is valid
        if score not in range(1, 6):
            return Response({'error': 'Invalid score.'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = Review.objects.create(book=book, user=user, score=score, comment=comment)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # User delete their review
    def delete(self, request, id, format=None):
        user = request.user
        review_id = id
        
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if review.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    # Retrieve reviews
    def get(self, request, id, format=None):
        book_id = id
        
        try:
            reviews = Review.objects.filter(book=book_id)
        except Book.DoesNotExist:
            book = get_object_or_404(Book, pk=book_id)
            return Response([], status=status.HTTP_200_OK)
    
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'GET':
            return [permissions.IsAuthenticated(), ] 
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            return [IsAuthorOf(), ]
        return super().get_permissions()
    
    def post(self, request, id, format=None):
        user = request.user
        book_id = request.data.get('book_id')
        # book = Book.objects.get()
        
        try:
            # TODO: Get book object when user interact with web interface instead of using pk=book_id
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book in the query does not exit'}, status=status.HTTP_400_BAD_REQUEST)
        
        book_following = Follow.objects.create(user=user, book=book)
        serializers = FollowSerializer(book_following)
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, id, format=None):
        try:
            follows = Follow.objects.filter(user=request.user)
        except Follow.DoesNotExist or not follows.exists():
            return Response({'error': 'User f{user_id} is not following any books at the moment'}, status=status.HTTP_204_NO_CONTENT)
        
        if request.user != CustomUser.objects.get(pk=id):
            return Response({'error': 'Wrong user id declared'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializers = FollowSerializer(follows, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        user = request.user
        book = request.data.get('book')
        # following_id = id

        following_book = get_object_or_404(Follow, user=user, book=book)
        
        if following_book is None:
            return Response({'error': 'This user does not follow this book'})
        
        if following_book.user != user:
            return Response({'error': 'You are not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        following_book.delete()
        return Response({'status': 'Deleted'}, status=status.HTTP_200_OK)
    
    def update(self, request, id, format=None):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, id, format=None):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
   
   
class HistoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    
    def get(self, request, format=None):
        user = request.user
        histories = History.objects.filter(user=user).order_by('-timestamp')
        serializer = HistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    
class QueryAuthorView(views.APIView):
    def get(self, request, format=None):
        query = request.query_params.get('q')
        authors = Author.objects.filter(name__icontains=query)
        if authors.count() == 0:
            return Response({'error': 'No authors found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)


class QueryBookView(views.APIView):
    def get(self, request, format=None):
        query = request.query_params.get('q')
        books = Book.objects.filter(title__icontains=query)
        if books.count() == 0:
            return Response({'error': 'No books found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class QueryView(views.APIView):
    def get(self, request, format=None):
        query = request.query_params.get('q')
        books = Book.objects.filter(title__icontains=query)
        authors = Author.objects.filter(name__icontains=query)
        if books.count() == 0 and authors.count() == 0:
            return Response({'error': 'No books or authors found.'}, status=status.HTTP_404_NOT_FOUND)
        book_serializer = BookSerializer(books, many=True)
        author_serializer = AuthorSerializer(authors, many=True)
        return Response({'books': book_serializer.data, 'authors': author_serializer.data}, status=status.HTTP_200_OK)


class GetRecentUpdatesView(views.APIView):
    def get(self, request, format=None):
        books = []

        chapters = Chapter.objects.all().order_by('-lastupdated')
        for chapter in chapters:
            if chapter.book not in books:
                books.append(chapter.book)
            if len(books) >= 10:
                break

        book_serializer = BookSerializer(books, many=True)
        return Response(book_serializer.data, status=status.HTTP_200_OK)

# class BookCreate(APIView):
#     def post(self, request, format=None):
#         author_data = request.data.get('author')
#         author, error, status_code = find_or_create_author(author_data)

#         if error is not None:
#             return Response(error, status=status_code)

#         book_data = QueryDict('', mutable=True)
#         book_data.update(request.data)
#         book_data['author'] = author.id
#         serializer = BookSerializer(data=book_data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BookInfo(APIView):
#     def get(self, request, book_id, format=None):
#         try:
#             book = Book.objects.get(id=book_id)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Book with given ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = BookDetailSerializer(book)
#         return Response(serializer.data)

#     def patch(self, request, book_id, format=None):
#         try:
#             book = Book.objects.get(id=book_id)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Book with given ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

#         author_data = request.data.get('author')
#         if author_data is not None:
#             author, error, status_code = find_or_create_author(author_data)
#             if error is not None:
#                 return Response(error, status=status_code)
#             book_data = QueryDict('', mutable=True)
#             book_data.update(request.data)
#             book_data['author'] = author.id
#         else:
#             book_data = request.data

#         serializer = BookSerializer(book, data=book_data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, book_id, format=None):
#         try:
#             book = Book.objects.get(id=book_id)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Book with given ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
