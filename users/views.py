import random
import time

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import PhoneNumberVerificationSerializer, VerificationCodeSerializer, \
    UserProfileSerializer, InviteCodeSerializer


class PhoneNumberView(GenericAPIView):
    """
    Эндпоинт для ввода номера телефона.
    После успешной валидации номера телефона генерируется 4-значный код для верификации.
    """
    serializer_class = PhoneNumberVerificationSerializer  # Используется сериализатор для проверки номера телефона.

    @swagger_auto_schema(operation_summary="Авторизация по номеру телефона")
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, проверяет номер телефона и отправляет код верификации.
        """
        serializer = PhoneNumberVerificationSerializer(data=request.data)

        if serializer.is_valid():  # Проверяем, что данные валидны.
            phone_number = serializer.validated_data[
                'phone_number']  # Извлекаем номер телефона из данных.

            # Проверка на существование пользователя с данным номером телефона.
            user = User.objects.filter(
                phone_number=phone_number).first()  # Используем номер телефона как username
            print("XXXXXXXXXXXXX", user)
            if user:
                if user.is_active:
                    # Если пользователь уже верифицирован (is_active=1), возвращаем сообщение и перенаправляем на профиль.
                    return Response({
                        "message": "Пользователь верифицирован",
                        "profile_url": f"/profile/{user.id}/"  # Пример ссылки на профиль
                    }, status=status.HTTP_200_OK)
                else:
                    # Если пользователь существует, но не активирован (is_active=0), отправляем новый код верификации.
                    verification_code = user.generate_and_send_verification_code()

                    # Имитируем задержку на сервере для отправки кода верификации.
                    time.sleep(random.randint(1, 2))  # Задержка от 1 до 2 секунд.

                    return Response({
                        "message": "Новый код верификации отправлен на номер телефона",
                        "verification_code": verification_code
                    }, status=status.HTTP_200_OK)

            else:
                # Если пользователь не найден, создаём нового пользователя с is_active=0 и генерируем код верификации.
                user = User.objects.create(username=phone_number,
                                           phone_number=phone_number, is_active=False)
                verification_code = user.generate_and_send_verification_code()

                # Имитируем задержку на сервере для отправки кода верификации.
                time.sleep(random.randint(1, 2))  # Задержка от 1 до 2 секунд.

                return Response({
                    "message": "Пользователь создан, код верификации отправлен на номер телефона",
                    "verification_code": verification_code
                }, status=status.HTTP_201_CREATED)

        # Если данные некорректны, возвращаем ошибки.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationCodeView(GenericAPIView):
    """
    Эндпоинт для ввода кода верификации, который был отправлен на номер телефона.
    Если код правильный, то создается или обновляется пользователь.
    """
    serializer_class = VerificationCodeSerializer  # Сериализатор для проверки кода верификации.

    @swagger_auto_schema(operation_summary="Верификация номера телефона")
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, проверяет номер телефона и отправляет код верификации.
        """
        # Создаем экземпляр сериализатора с данными из запроса.
        serializer = PhoneNumberVerificationSerializer(data=request.data)
        if serializer.is_valid():  # Проверяем, что данные валидны.
            phone_number = serializer.validated_data[
                'phone_number']  # Извлекаем номер телефона из данных.
            verification_code = serializer.validated_data[
                'verification_code']  # Извлекаем верификационный код

            # Проверка на существование пользователя с данным номером телефона.
            user = User.objects.filter(phone_number=phone_number).first()

            if user:
                # Проверяем, совпадает ли введённый верификационный код с сохранённым у пользователя
                if user.verification_code == verification_code:
                    if not user.invite_code:
                        user.generate_invite_code()
                    user.is_active = True
                    user.save()

                    # Имитируем задержку на сервере для отправки кода верификации.
                    time.sleep(random.randint(1, 2))  # Задержка от 1 до 2 секунд.

                    return Response({
                        "message": f"Верификация прошла успешно! Ваш invite-код: {user.invite_code}"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": "Неверный код верификации"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "message": "Пользователь с таким номером телефона не найден"
                }, status=status.HTTP_404_NOT_FOUND)

        # Если сериализатор не прошёл валидацию, возвращаем ошибки.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(GenericAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        """
        Получить профиль пользователя по имени пользователя (username).
        """
        username = kwargs.get('username')  # Извлекаем username из URL-параметра

        try:
            user = User.objects.get(username=username)  # Находим пользователя по username
        except User.DoesNotExist:
            return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем данные пользователя
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivateInviteCodeView(GenericAPIView):
    # Убираем или не указываем permission_classes
    serializer_class = InviteCodeSerializer

    @swagger_auto_schema(operation_summary="Активация инвайт-кода для пользователя.",
                         request_body=InviteCodeSerializer)
    def post(self, request, *args, **kwargs):
        """Активация инвайт-кода для пользователя."""

        # Получаем инвайт-код из запроса
        invite_code = request.data.get('invite_code')

        # Проверка на существование инвайт-кода
        if not invite_code:
            return Response({"message": "Инвайт-код не может быть пустым."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Проверяем, существует ли пользователь с этим инвайт-кодом
            inviter = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response({"message": "Неверный инвайт-код."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Если пользователь найден, но не авторизован, то создаем нового пользователя
        user = request.user if request.user.is_authenticated else None

        if user:
            # Если пользователь авторизован, активируем инвайт-код для него
            if user.activated_invite_code:
                return Response({"message": "Вы уже активировали инвайт-код."},
                                status=status.HTTP_400_BAD_REQUEST)

            user.activate_invite_code(invite_code)
            return Response(
                {"message": f"Инвайт-код {invite_code} успешно активирован!"},
                status=status.HTTP_200_OK)

        return Response({
                            "message": "Пользователь не авторизован. Но вы можете создать нового пользователя."},
                        status=status.HTTP_200_OK)
