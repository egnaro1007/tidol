from django.contrib import admin

from .models import Author, Book, Chapter, Genre, Comment, Bookmark

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Chapter)
admin.site.register(Genre)
admin.site.register(Comment)
admin.site.register(Bookmark)
