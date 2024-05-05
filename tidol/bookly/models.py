import os
from django.db import models
from django.utils import timezone
from authentication.models import CustomUser


class Author(models.Model):
    name = models.CharField(max_length=128)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    bio = models.TextField(null=True)
    
    def __str__(self):
        return self.name


def get_cover_upload_to(instance, filename):
    base_filename, extension = os.path.splitext(filename)
    new_filename = f"cover_{instance.id}{extension}"
    return os.path.join('covers/', new_filename)


class Book(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    description = models.TextField(null=True)
    cover = models.ImageField(upload_to=get_cover_upload_to, null=True)
    lastupdated = models.DateTimeField(auto_now=True)

    # Chapters
    # Many to many with Genres
    
    def count_views(self):
        return sum([chapter.count_views() for chapter in Chapter.objects.filter(book=self)])

    def __str__(self):
        return self.title + " by " + str(self.author.name)


class Chapter(models.Model):
    title = models.CharField(max_length=128)
    chapter_number = models.DecimalField(max_digits=16, decimal_places=2, null=False, blank=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'chapter_number'], name='unique_chapter_number')
        ]  
            
    def count_views(self):
        return History.objects.filter(chapter=self).count()

    def save(self, *args, **kwargs):
        if self.pk is not None:
            origin = Chapter.objects.get(pk=self.pk)
            if origin.book != self.book:
                raise ValueError("Cannot change the book of a chapter.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title + " - " + str(self.book.title)


class Genre(models.Model):
    name = models.CharField(max_length=128)
    books = models.ManyToManyField(Book, related_name='genres')

    def __str__(self):
        return self.name

class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'chapter'], name='unique_history')
        ]
        
    def save(self, *args, **kwargs):
        if self.user is None:
            super().save(*args, **kwargs)
            return
        if not self.pk:
            try:
                existing = History.objects.get(user=self.user, chapter=self.chapter)
                self.pk = existing.pk
            except History.DoesNotExist:
                pass
        self.timestamp = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} - {self.chapter.title} - {timezone.localtime(self.timestamp)}"


class Comment(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', null=False, blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False)
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=False, null=False)
    comment = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'user'], name='unique_review')
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.score}"
    
class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookmarks", null=False, 
                                blank=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="bookmarks", null=False,
                                   blank=False)
    page = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'chapter', 'page'], name="unique_bookmark")
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.chapter.book.title} - {self.chapter.chapter_number} - {self.page}"

class Follow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="users", null=False, blank=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="books", null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def get_follow_of_user(user):
        return Follow.objects.filter(user=user)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], name='unique_follow')
        ]
    def __str__(self) -> str:
        return f"{self.user.username} - {self.book.title} - {self.timestamp}"