import random
import string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy


# Создадим кастомный менеджер для пользователя
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        """Создание обычного пользователя с номером телефона и паролем"""
        if not phone_number:
            raise ValueError(gettext_lazy('Поле номера телефона не может быть пустым'))
        phone_number = phone_number.strip()
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Создание суперпользователя с номером телефона и паролем"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)


# Основная модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)  # Номер телефона
    invite_code = models.CharField(max_length=6, unique=True, blank=True,
                                   null=True)  # Инвайт-код
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                                    blank=True, related_name='referrals')  # Реферал
    # Код инвайта, который пользователь активировал
    activated_invite_code = models.CharField(max_length=6, null=True,
                                             blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Для админов
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()  # Используем наш кастомный менеджер

    USERNAME_FIELD = 'phone_number'  # Поле для аутентификации
    REQUIRED_FIELDS = []  # Можно оставить пустым, так как используем только phone_number

    def __str__(self):
        return self.phone_number

    def generate_invite_code(self):
        """Генерация случайного инвайт-кода"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.invite_code:
            # Присваиваем инвайт-код только при первом сохранении
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.phone_number

    def get_short_name(self):
        return self.phone_number
