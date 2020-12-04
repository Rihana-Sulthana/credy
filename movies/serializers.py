from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserRegistrationSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ('user_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token = self.get_jwt_token(validated_data)
        return token

    def get_jwt_token(self, validated_data):
        auth_user = authenticate(user_name=validated_data['user_name'], password=validated_data['password'])
        if auth_user is None:
            raise serializers.ValidationError(
                'A user with this name and password is not found.'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(auth_user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, auth_user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'access_token': jwt_token
        }