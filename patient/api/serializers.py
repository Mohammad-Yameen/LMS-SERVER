from django.contrib.auth.models import User
from rest_framework import serializers


class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}