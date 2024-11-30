import random
import string
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy

#
# # Создадим кастомный менеджер для пользователя
# class CustomUserManager(BaseUserManager):
#     def create_user(self, phone_number, password=None, **extra_fields):
#         """Создание обычного пользователя с номером телефона и паролем"""
#         if not phone_number:
#             raise ValueError(gettext_lazy('Поле номера телефона не может быть пустым'))
#         phone_number = phone_number.strip()
#         user = self.model(phone_number=phone_number, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user
#
#     def create_superuser(self, phone_number, password=None, **extra_fields):
#         """Создание суперпользователя с номером телефона и паролем"""
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         return self.create_user(phone_number, password, **extra_fields)
#
#
# # Основная модель пользователя
# class User(AbstractBaseUser, PermissionsMixin):
#     phone_number = models.CharField(max_length=15, unique=True)  # Номер телефона
#     invite_code = models.CharField(max_length=6, unique=True, blank=True,
#                                    null=True)  # Инвайт-код
#     referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
#                                     blank=True, related_name='referrals')  # Реферал
#     # Код инвайта, который пользователь активировал
#     activated_invite_code = models.CharField(max_length=6, null=True,
#                                              blank=True)
#
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)  # Для админов
#     date_joined = models.DateTimeField(auto_now_add=True)
#
#     objects = CustomUserManager()  # Используем наш кастомный менеджер
#
#     USERNAME_FIELD = 'phone_number'  # Поле для аутентификации
#     REQUIRED_FIELDS = []  # Можно оставить пустым, так как используем только phone_number
#
#     def __str__(self):
#         return self.phone_number
#
#     def generate_invite_code(self):
#         """Генерация случайного инвайт-кода"""
#         return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#
#     def save(self, *args, **kwargs):
#         if not self.invite_code:
#             # Присваиваем инвайт-код только при первом сохранении
#             self.invite_code = self.generate_invite_code()
#         super().save(*args, **kwargs)
#
#     def get_full_name(self):
#         return self.phone_number
#
#     def get_short_name(self):
#         return self.phone_number


# import random
# import string
# from django.db import models
# from django.contrib.auth.models import AbstractUser
#
#
# # Кастомная модель пользователя
# class User(AbstractUser):
#     phone_number = models.CharField(max_length=15, unique=True)
#     invite_code = models.CharField(max_length=6, null=True, blank=True)
#     activated_invite_code = models.CharField(max_length=6, null=True, blank=True)
#
#     def __str__(self):
#         return self.username
#
#     def generate_invite_code(self):
#         """Генерация случайного 6-значного инвайт-кода (смешанные цифры и буквы)"""
#         self.invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#         self.save()
#
#     def get_invite_code(self):
#         """Получение invite-кода их базы"""
#         return self.invite_code
#
#
#     def get_invited_users(self):
#         """Возвращает список пользователей, которые использовали инвайт-код этого пользователя."""
#         return User.objects.filter(activated_invite_code=self.invite_code)
#
#
# class PhoneVerification(models.Model):
#     phone_number = models.CharField(max_length=15, unique=True)
#     verification_code = models.CharField(max_length=4)
#
#     def generate_verification_code(self):
#         """Генерация 4-значного кода авторизации"""
#         self.verification_code = str(random.randint(1000, 9999))
#         self.save()
#
#
# class InviteCode(models.Model):
#     code = models.CharField(max_length=6, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.code
#
#     def generate_code(self):
#         """Генерация случайного 6-значного инвайт-кода (смешанные цифры и буквы)"""
#         self.code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#         self.save()
#
#     @classmethod
#     def get_or_create_code(cls):
#         """Возвращает существующий или новый инвайт-код."""
#         invite_code, created = cls.objects.get_or_create(code=''.join(random.choices(string.ascii_letters + string.digits, k=6)))
#         return invite_code
#

import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, null=True, blank=True)  # Инвайт-код
    activated_invite_code = models.CharField(max_length=6, null=True, blank=True)  # Активированный инвайт-код
    verification_code = models.CharField(max_length=4, null=True, blank=True)  # Код верификации
    verification_code_created_at = models.DateTimeField(null=True, blank=True)  # Время создания кода верификации

    def __str__(self):
        return self.username

    def generate_invite_code(self):
        """Генерация случайного 6-значного инвайт-кода (смешанные цифры и буквы)"""
        self.invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        self.save()

    def generate_verification_code(self):
        """Генерация 4-значного кода авторизации"""
        self.verification_code = str(random.randint(1000, 9999))
        self.save()

    def get_invite_code(self):
        """Получение invite-кода"""
        return self.invite_code

    def get_verification_code(self):
        """Получение verification-кода"""
        return self.verification_code

    def generate_and_send_verification_code(self):
        """Генерация и отправка кода верификации"""
        self.generate_verification_code()
        # Здесь можно отправить код на телефон или email
        # Например, отправка через SMS или email
        # send_sms(self.phone_number, self.verification_code)
        return self.verification_code

    def activate_invite_code(self, code):
        """Активация инвайт-кода"""
        if code == self.invite_code:
            self.activated_invite_code = code
            self.save()
            return True
        return False

    def reset_verification_code(self):
        """Сбросить код верификации"""
        self.verification_code = None
        self.verification_code_created_at = None
        self.save()

    def is_verification_code_expired(self):
        """Проверка истечения времени для кода верификации"""
        if self.verification_code_created_at:
            expiration_time = self.verification_code_created_at + datetime.timedelta(minutes=10)  # Код истекает через 10 минут
            return datetime.datetime.now() > expiration_time
        return False

    @classmethod
    def get_or_create_code(cls):
        """Возвращает существующий или новый инвайт-код."""
        invite_code, created = cls.objects.get_or_create(code=''.join(random.choices(string.ascii_letters + string.digits, k=6)))
        return invite_code