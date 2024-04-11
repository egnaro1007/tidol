from rest_framework import serializers
from .models import Author, Book, Chapter

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description']
        
class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'chapters']

    class ChapterSerializer(serializers.ModelSerializer):
        class Meta:
            model = Chapter
            fields = ['id', 'title', 'chapter_number', 'lastupdated']

    chapters = ChapterSerializer(many=True, read_only=True)
    
    
class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'chapter_number', 'book', 'content', 'created', 'lastupdated']
        read_only_fields = ['created', 'lastupdated']
        
        