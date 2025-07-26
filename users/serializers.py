from rest_framework import serializers
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['student_id', 'full_name', 'entry_year', 'major']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['student_id', 'full_name', 'entry_year', 'major']
        read_only_fields = ['student_id']
