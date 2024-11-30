from rest_framework import serializers

from .models import User


class PhoneNumberVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    verification_code = serializers.CharField(max_length=4)

    def validate_phone_number(self, value):
        """Валидация номера телефона"""
        # Здесь можно добавить дополнительные проверки на формат телефона
        if len(value) < 10:
            raise serializers.ValidationError("Номер телефона слишком короткий.")
        return value


class VerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    verification_code = serializers.CharField(max_length=4)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'activated_invite_code']


class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)
