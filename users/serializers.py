from rest_framework import serializers

from .models import User


class PhoneNumberVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

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
    # Список пользователей, активировавших инвайт-код этого пользователя
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'activated_invite_code',
                  'invited_users']

    def get_invited_users(self, obj):
        # Возвращает список пользователей, которые активировали инвайт-код этого пользователя
        invited_users = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone_number for user in invited_users]


class InviteCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    activated_invite_code = serializers.CharField(max_length=6)

