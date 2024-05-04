from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import CustomUser
from .serializers import RegisterUserSerializer
from .serializers import CustomTokenObtainPairSerializer
from bookly.models import Author
from bookly.serializers import AuthorSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        access_expiration = datetime.now() + refresh.access_token.lifetime
        refresh_expiration = datetime.now() + refresh.lifetime

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'access_expires_at': access_expiration.isoformat(),
            'refresh_expires_at': refresh_expiration.isoformat(),
        })
        
        
class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User register successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        author_name = request.data.get('author_name')
        if author_name is None:
            return Response({"message": "Author name is required"}, status=status.HTTP_400_BAD_REQUEST)

        if Author.objects.filter(user=request.user).exists():
            return Response({"message": "Author profile already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        author = Author(name=author_name, user=request.user)
        author.save()

        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        new_author_name = request.data.get('author_name')
        if new_author_name is None:
            return Response({"message": "New author name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist:
            return Response({"message": "Author profile does not exist for this user"},
                            status=status.HTTP_404_NOT_FOUND)

        author.name = new_author_name
        author.save()

        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        author.delete()
        return Response({"message": "Author profile deleted successfully"}, status=status.HTTP_200_OK)


class CheckUsernameAPIView(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        if username is None:
            return Response({"message": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not username.isalnum():
            return Response({"message": "Username can only contain letters and numbers"},
                            status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).exists():
            return Response({"message": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Username is available"}, status=status.HTTP_200_OK)
