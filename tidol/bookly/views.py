from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Book, Author
from .serializers import BookSerializer, BookDetailSerializer

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
    