from rest_framework import serializers
from .models import Author, Book, Chapter

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
            fields = ['id', 'title', 'chapter_number']

    chapters = ChapterSerializer(many=True, read_only=True)
        