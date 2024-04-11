from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import CustomUser
from .serializers import RegisterUserSerializer

class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckUsernameAPIView(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        if username is None:
            return Response({"message": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not username.isalnum():
            return Response({"message": "Username can only contain letters and numbers"}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).exists():
            return Response({"message": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Username is available"}, status=status.HTTP_200_OK)
    