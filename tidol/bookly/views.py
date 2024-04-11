from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict
from rest_framework import status
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Author, Book, Chapter
from .serializers import BookSerializer, BookDetailSerializer, ChapterSerializer

class Test(APIView):
    def get(self, request, format=None):
        return Response({'message': 'Hello, World!'})
    
def find_or_create_author(author_data):
    if isinstance(author_data, int):
        try:
            author = Author.objects.get(id=author_data)
        except ObjectDoesNotExist:
            return None, {'error': 'Author with given ID does not exist.'}, status.HTTP_400_BAD_REQUEST
    elif isinstance(author_data, str):
        author = Author.objects.create(name=author_data)
    else:
        return None, {'error': 'Invalid author data.'}, status.HTTP_400_BAD_REQUEST

    return author, None, None

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return BookDetailSerializer
        return BookSerializer


    # POST
    def create(self, request, *args, **kwargs):
        author_data = request.data.get('author')
        author, error, status_code = find_or_create_author(author_data)

        if error is not None:
            return Response(error, status=status_code)

        book_data = QueryDict('', mutable=True)
        book_data.update(request.data)
        book_data['author'] = author.id
        
        serializer = BookSerializer(data=book_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #GET
    def retrieve(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = BookDetailSerializer(book)
        return Response(serializer.data)
    
    #PUT
    def update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    #PATCH
    def partial_update(self, request, *args, **kwargs):
        book = self.get_object()
        author_data = request.data.get('author')
        if author_data is not None:
            author, error, status_code = find_or_create_author(author_data)
            if error is not None:
                return Response(error, status=status_code)
            book_data = QueryDict('', mutable=True)
            book_data.update(request.data)
            book_data['author'] = author.id
        else:
            book_data = request.data

        serializer = BookSerializer(book, data=book_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #DELETE
    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    
    serializer_class = ChapterSerializer
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, *args, **kwargs):
        if 'book' in request.data and request.data['book'] != self.get_object().book.id:
            raise serializers.ValidationError({'error': 'The book which this chapter belongs to cannot be changed after creation.'})
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
            
    

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
    