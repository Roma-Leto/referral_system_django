import random
import time

from django.contrib import messages
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView, DetailView

from users.forms import PhoneNumberForm, VerificationCodeForm, ActiveInviteCodeView
from .models import User
from .serializers import PhoneNumberVerificationSerializer, VerificationCodeSerializer, \
    UserProfileSerializer, InviteCodeSerializer


# region API
class PhoneNumberView(GenericAPIView):
    """
    Эндпоинт для ввода номера телефона.
    После успешной валидации номера телефона генерируется 4-значный код для верификации.
    """
    serializer_class = PhoneNumberVerificationSerializer

    @swagger_auto_schema(operation_summary="Авторизация по номеру телефона")
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, проверяет номер телефона на дублирование в базе данных,
        а так же активацию через код ранее, отправляет 4-значный код верификации.

        Параметры:

          "phone_number" числовое поле json: "номер телефона, 11-15 цифр",

        Возвращает сообщение о результате операции и отправляет код верификации с
        имитацией задержки в 1-2 секунды на введённый номер.
        """
        serializer = PhoneNumberVerificationSerializer(data=request.data)

        if serializer.is_valid():  # Проверяем, что данные валидны.
            phone_number = serializer.validated_data[
                'phone_number']  # Извлекаем номер телефона из данных.

            # Проверка на существование пользователя с данным номером телефона.
            user = User.objects.filter(
                phone_number=phone_number).first()  # Используем номер телефона как username
            if user:
                if user.is_active:
                    # Если пользователь уже верифицирован (is_active=1),
                    # возвращаем сообщение и перенаправляем на профиль.
                    return Response({
                        "message": "Пользователь верифицирован",
                        "profile_url": f"/profile/{user.id}/"
                    }, status=status.HTTP_200_OK)
                else:
                    # Если пользователь существует, но не активирован (is_active=0),
                    # отправляем новый код верификации.
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
    serializer_class = VerificationCodeSerializer

    @swagger_auto_schema(operation_summary="Верификация номера телефона")
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, проверяет номер телефона на дублирование в базе данных
        и отправляет код верификации в случае когда информация о пользователе
        в базе данных отсутствует.

        Параметры:

          "phone_number" числовое поле json: "номер телефона, 11-15 цифр",
          "verification_code" числовое поле json: "4 цифры"

        Возвращает сообщение о результате операции.
        """
        # Создаем экземпляр сериализатора с данными из запроса.
        serializer = VerificationCodeSerializer(data=request.data)
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

    @swagger_auto_schema(operation_summary="Просмотр профиля пользователя.")
    def get(self, request, *args, **kwargs):
        """
        Получить информацию о профиле пользователя по номеру телефона.

        Параметры:
          Поле "username" строковое: 11-15 цифр

        Возвращает данные пользователя: номер телефона (он же имя пользователя),
        инвайт-код профиля, инвайт-код реферала (null если такого кода нет),
        номера телефонов пользователей которые воспользовались инвайт-кодом профиля.

        Пример ответа на запрос:

        {
          "phone_number": "00009996633",
          "invite_code": "0aVNRO",
          "activated_invite_code": null,
          "invited_users": ["8989989989"]
        }
        """
        username = kwargs.get('username')  # Извлекаем username из URL-параметра

        try:
            user = User.objects.get(
                username=username)  # Находим пользователя по username
        except User.DoesNotExist:
            return Response({"message": "Пользователь не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Сериализуем данные пользователя
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivateInviteCodeView(GenericAPIView):
    serializer_class = InviteCodeSerializer

    @swagger_auto_schema(operation_summary="Активация инвайт-кода.",
                         request_body=InviteCodeSerializer)
    def post(self, request, *args, **kwargs):
        """
        Активация инвайт-кода.
        Предусмотренны случаи ранее активированного инвайт-кода, несуществующего кода,
        успешной активации. Реализовано ьез необходимости предварительной авторизации.

        Параметры:

          "phone_number" числовое поле json: "номер телефона, 11-15 цифр",
          "activated_invite_code" строка json: "любые шесть символов"

          Поле "username" и поле "phone_number" должны содержать один номер телефона.

        Возвращает сообщение о результате операции.
        """
        # Проверка на существование инвайт-кода
        if request.data.get('activated_invite_code'):
            # Получаем инвайт-код из запроса
            activated_invite_code = request.data.get('activated_invite_code')
            # Получаем пользователя (не авторизированного) добавляющего инвайт
            user = User.objects.get(phone_number=request.data.get('phone_number'))

            try:
                # Проверяем, существует ли пользователь с этим инвайт-кодом
                inviter = User.objects.get(invite_code=activated_invite_code)
            except User.DoesNotExist:
                return Response({"message": "Нет пользователя "
                                            "с таким инвайт-кодом."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Если инвайн не активировался ранее
            if user.activated_invite_code is None:
                # Проверка на добавление своего же инвайт-кода
                user.activate_invite_code(request.data.get('activated_invite_code'))
                return Response(
                    {
                        "message": f"Инвайт-код {request.data.get('activated_invite_code')} "
                                   f"успешно активирован!"},
                    status=status.HTTP_200_OK)
            else:
                return Response({"message": f"Инвайт-код ранее активирован"},
                                status=status.HTTP_400_BAD_REQUEST)


# endregion API

# region Templates


class HomePageView(FormView):
    template_name = 'users/index.html'
    form_class = PhoneNumberForm

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number)
            # Проверка верификации
            if user.is_active:
                # Перенаправляем на профиль пользователя
                return redirect('profile', username=user.username)
            else:
                return redirect('verify', phone_number=phone_number)
        except User.DoesNotExist:
            # Если пользователя с таким номером нет, перенаправляем на страницу ввода кода
            return redirect('verify', phone_number=phone_number)


class VerifyPhoneNumberView(FormView):
    template_name = 'users/verify.html'
    form_class = VerificationCodeForm

    def form_valid(self, form):
        verification_code = form.cleaned_data['verification_code']
        try:
            user = User.objects.get(verification_code=verification_code)
            if user.verification_code == verification_code:
                # Код верен, генерируем инвайт-код, меняем статус активации пользователя.
                user.generate_invite_code()
                user.is_active = True
                user.save()
                return redirect('profile', username=user.username)
            else:
                return HttpResponse("Неверный код верификации", status=400)
        except User.DoesNotExist:
            return HttpResponse("Пользователь не найден", status=404)


class UserProfileView(DetailView, FormView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'
    form_class = ActiveInviteCodeView

    def form_valid(self, form):
        activated_invite_code = form.cleaned_data['activated_invite_code']
        is_exists = User.objects.filter(invite_code=activated_invite_code).exists()

        if is_exists:
            user = User.objects.get(username=self.kwargs['username'])
            user.activate_invite_code(activated_invite_code)
            return redirect('profile', username=self.kwargs['username'])
        else:
            return redirect('profile', username=self.kwargs['username'])

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs['username'])

# endregion Templates
