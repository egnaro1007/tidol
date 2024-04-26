import os
from django.db import models
from authentication.models import CustomUser


class Author(models.Model):
    name = models.CharField(max_length=128)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)

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


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
