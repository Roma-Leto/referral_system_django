import random
import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

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
                    # Если коды совпадают, генерируем инвайт-код и активируем пользователя
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
    """
    Эндпоинт для получения или обновления профиля пользователя.
    Пользователь может просматривать свой профиль и активировать инвайт-код.
    """
    serializer_class = UserProfileSerializer  # Сериализатор для работы с профилем пользователя.

    @swagger_auto_schema(operation_summary="Возврат данных текущего пользователя")
    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращает данные профиля текущего пользователя.
        """
        user = request.user  # Получаем текущего авторизованного пользователя.
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Проверка и активация invite-кода")
    def put(self, request, *args, **kwargs):
        """
        Обрабатывает PUT-запрос, обновляет профиль пользователя, активирует инвайт-код.
        """
        serializer = self.get_serializer(
            data=request.data)  # Создаем сериализатор с данными из запроса.

        if serializer.is_valid():  # Проверяем валидность данных.
            invite_code = serializer.validated_data[
                'invite_code']  # Извлекаем инвайт-код.
            user = request.user  # Получаем текущего пользователя.

            try:
                inviter = User.objects.get(
                    invite_code=invite_code)  # Ищем пользователя по инвайт-коду.
            except User.DoesNotExist:
                return Response({"error": "Неверный инвайт-код."},
                                status=status.HTTP_400_BAD_REQUEST)

            if inviter == user:
                return Response(
                    {"error": "Вы не можете активировать свой собственный инвайт-код."},
                    status=status.HTTP_400_BAD_REQUEST)

            if user.activated_invite_code:
                return Response({"error": "Вы уже активировали инвайт-код."},
                                status=status.HTTP_400_BAD_REQUEST)

            user.activated_invite_code = invite_code  # Активируем инвайт-код для пользователя.
            user.save()
            return Response({"message": "Инвайт-код активирован!"},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateInviteCodeView(GenericAPIView):
    """
    Эндпоинт для активации инвайт-кода другим пользователем.
    Пользователь может активировать инвайт-код, предоставленный другим пользователем.
    """
    serializer_class = InviteCodeSerializer  # Сериализатор для работы с инвайт-кодами.

    @swagger_auto_schema(operation_summary="Активация invite-кода")
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, проверяет и активирует инвайт-код для текущего пользователя.
        """
        serializer = self.get_serializer(
            data=request.data)  # Создаем сериализатор с данными из запроса.

        if serializer.is_valid():  # Проверяем валидность данных.
            invite_code = serializer.validated_data[
                'invite_code']  # Извлекаем инвайт-код.
            user = request.user  # Получаем текущего пользователя.

            try:
                inviter = User.objects.get(
                    invite_code=invite_code)  # Ищем пользователя по инвайт-коду.
            except User.DoesNotExist:
                return Response({"error": "Неверный инвайт-код."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Если инвайт-код уже активирован, возвращаем ошибку.
            if inviter.activated_invite_code:
                return Response({"error": "Вы уже активировали инвайт-код."},
                                status=status.HTTP_400_BAD_REQUEST)

            inviter.activated_invite_code = invite_code  # Активируем инвайт-код для пользователя.
            inviter.save()

            return Response({"message": "Инвайт-код активирован!"},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
