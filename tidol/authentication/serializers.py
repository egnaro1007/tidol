from rest_framework import serializers

from .models import CustomUser
from datetime import date

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'hobby', 'date_of_birth']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    def validate_date_of_birth(self, value):
        if value >= date.today():
            raise serializers.ValidationError("Invalid date")
        return value
