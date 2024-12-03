import random
import string

from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6,
                                   null=True,
                                   blank=True,
                                   verbose_name="Инвайт-код")
    activated_invite_code = models.CharField(max_length=6,
                                             null=True,
                                             blank=True,
                                             verbose_name="Активированный инвайт-код")
    verification_code = models.CharField(max_length=4,
                                         null=True,
                                         blank=True,
                                         verbose_name="Код верификации")
    verification_code_created_at = (
        models.DateTimeField(null=True,
                             blank=True,
                             verbose_name="Время создания кода верификации"))

    def __str__(self):
        return self.username

    def generate_invite_code(self):
        """Генерация случайного 6-значного инвайт-кода (смешанные цифры и буквы)"""
        self.invite_code = ''.join(
            random.choices(string.ascii_letters + string.digits, k=6))
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
        if code != self.invite_code:
            self.activated_invite_code = code
            self.save()
            return True
        return False

    # region Дополнительный функционал
    def reset_verification_code(self):
        """Сбросить код верификации"""
        self.verification_code = None
        self.verification_code_created_at = None
        self.save()

    def is_verification_code_expired(self):
        """Проверка истечения времени для кода верификации"""
        if self.verification_code_created_at:
            expiration_time = (self.verification_code_created_at +
                               datetime.timedelta(
                                   minutes=10))  # Код истекает через 10 минут
            return datetime.datetime.now() > expiration_time
        return False

    # endregion

    @classmethod
    def get_or_create_code(cls):
        """Возвращает существующий или новый инвайт-код."""
        invite_code, created = cls.objects.get_or_create(code=''.join
        (random.choices(string.ascii_letters + string.digits, k=6)))
        return invite_code
