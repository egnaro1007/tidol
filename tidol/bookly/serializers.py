from rest_framework import serializers

from .models import Author, Book, Chapter, Bookmark


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

class BookmarkSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='chapter.book.title', read_only=True)
    class Meta:
        model = Bookmark
        fields = ['id', 'book_title', 'chapter_id', 'user_id',  'page']
        read_only_field = ['user_id']
