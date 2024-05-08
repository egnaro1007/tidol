from rest_framework import serializers

from .models import Author, Book, Chapter, Comment, Review, Bookmark, Follow, History


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    viewcount = serializers.SerializerMethodField()
    number_of_chapters = serializers.SerializerMethodField()
    lastupdated = serializers.SerializerMethodField()
    
    def get_viewcount(self, obj):
        return obj.count_views()
    
    def get_number_of_chapters(self, obj):
        return obj.chapters.count()
    
    def get_lastupdated(self, obj):
        lastupdated = obj.lastupdated
        chapters = obj.chapters.all()
        if chapters:
            lastupdated = max([lastupdated] + [chapter.lastupdated for chapter in chapters])
        return lastupdated
    

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'description', 'cover', 'viewcount', 'number_of_chapters', 'lastupdated']


class BookDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    is_followed = serializers.SerializerMethodField()
    
    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(user=request.user, book=obj).exists()
        return False

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'description', 'cover', 'is_followed', 'chapters']

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
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'book', 'book_title', 'user', 'user_name', 'score', 'comment', 'timestamp']
        read_only_fields = ['timestamp']

class FollowSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source='book.author.id', read_only=True)
    author_name = serializers.CharField(source='book.author.name', read_only=True)
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_description = serializers.CharField(source='book.description', read_only=True)
    book_cover = serializers.ImageField(source='book.cover', read_only=True)
    latest_chapter = serializers.SerializerMethodField()
    
    def get_latest_chapter(self, obj):
        latest_chapter = obj.book.chapters.order_by('-lastupdated').first()
        if latest_chapter:
            return {
                'chapter_id': latest_chapter.id,
                'chapter_number': latest_chapter.chapter_number,
                'chapter_title': latest_chapter.title,
                'lastupdated': latest_chapter.lastupdated
            }
        return None
    
    
    class Meta:
        model = Follow
        fields = ['id', 'user', 'author_id', 'author_name', 'book_id', 'book_title', 'book_description', 'book_cover', 'latest_chapter', 'timestamp']
        read_only_fields = ['timestamp']
        
class HistorySerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source='chapter.book.author.id', read_only=True)
    author_name = serializers.CharField(source='chapter.book.author.name', read_only=True)
    book_id = serializers.IntegerField(source='chapter.book.id', read_only=True)
    book_title = serializers.CharField(source='chapter.book.title', read_only=True)
    book_description = serializers.CharField(source='chapter.book.description', read_only=True)
    book_cover = serializers.ImageField(source='chapter.book.cover', read_only=True)
    chapter_id = serializers.IntegerField(source='chapter.id', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    chapter_number = serializers.IntegerField(source='chapter.chapter_number', read_only=True)
    
    class Meta:
        model = History
        fields = ['id', 'author_id', 'author_name', 'book_id', 'book_title', 'book_description', 'book_cover', 'chapter_id', 'chapter_title', 'chapter_number', 'timestamp']
        read_only_fields = ['timestamp']
    
    