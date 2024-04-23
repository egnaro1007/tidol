from rest_framework import permissions

from .models import Author, Book, Chapter

class IsAuthor(permissions.BasePermission):
    """
    Permission to only allow users have an author profile.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist:
            return False
        
        return True

class IsAuthorOf(permissions.BasePermission):
    """
    Permission to only allow authors of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Book):
            return obj.author.user == request.user
        elif isinstance(obj, Chapter):
            return obj.book.author.user == request.user
        return False
    