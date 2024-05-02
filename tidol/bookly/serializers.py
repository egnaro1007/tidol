from rest_framework import serializers

from .models import Author, Book, Chapter, Comment, Review, Bookmark, Follow, History


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
        viewcount = serializers.SerializerMethodField()
        is_read = serializers.SerializerMethodField()
        
        class Meta:
            model = Chapter
            fields = ['id', 'title', 'chapter_number', 'lastupdated', 'is_read', 'viewcount']
        
        def get_is_read(self, obj):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                return History.objects.filter(user=request.user, chapter=obj).exists()
            return False
        
        def get_viewcount(self, obj):
            return obj.count_views()

    chapters = ChapterSerializer(many=True, read_only=True)


class ChapterSerializer(serializers.ModelSerializer):
    viewcount = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'chapter_number', 'book', 'content', 'created', 'lastupdated', 'viewcount']
        read_only_fields = ['created', 'lastupdated']
        
    def get_viewcount(self, obj):
        return obj.count_views()

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
        
class HistorySerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(source='chapter.book.id', read_only=True)
    book_title = serializers.CharField(source='chapter.book.title', read_only=True)
    chapter_id = serializers.IntegerField(source='chapter.id', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    
    class Meta:
        model = History
        fields = ['id', 'user', 'book_id', 'book_title', 'chapter_id', 'chapter_title', 'timestamp']
        read_only_fields = ['timestamp']
    
    