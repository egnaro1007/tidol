from rest_framework import serializers

from .models import Author, Book, Chapter, Comment, Review, Bookmark, Follow


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


class CommentSerializer(serializers.ModelSerializer):
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    book_title = serializers.CharField(source='chapter.book.title', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'chapter', 'chapter_title', 'book_title', 'user', 'content', 'timestamp']
        read_only_fields = ['timestamp']
        
class ReviewSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'book', 'book_title', 'user', 'score', 'comment', 'timestamp']
        read_only_fields = ['timestamp']

class FollowSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = Follow
        fields = ['id', 'user', 'book', 'book_title', 'timestamp']
        read_only_fields = ['timestamp']
    