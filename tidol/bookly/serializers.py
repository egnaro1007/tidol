from rest_framework import serializers

from .models import Author, Book, Chapter, Comment


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'description', 'cover']


class BookDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'description', 'chapters']

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
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'chapter', 'user', 'content', 'timestamp']
        read_only_fields = ['timestamp']
