from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import OtpCode, User
from .constants import JAMLYF_INCORRECT_CREDENTIALS_MESSAGE


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def validate_password(self, plain_password):
        validate_password(plain_password)
        return make_password(plain_password)


class ReadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, plain_password):
        if not self.context['request'].user.check_password(plain_password):
            raise serializers.ValidationError(JAMLYF_INCORRECT_CREDENTIALS_MESSAGE)
        return plain_password

    def validate_new_password(self, plain_password):
        validate_password(plain_password)
        return plain_password


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpCode
        fields = "__all__"
