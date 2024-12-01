from rest_framework.test import APITestCase
from rest_framework import status

class PhoneAuthTestCase(APITestCase):

    def test_send_verification_code(self):
        """Проверяем, что система отправляет код на номер телефона"""
        response = self.client.post('/auth/phone/', {'phone_number': '1234567890'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['message'], "Verification code sent")

    def test_verify_code_success(self):
        """Проверяем успешную верификацию кода"""
        phone_number = '1234567890'
        code = '1234'  # Предположим, что мы уже знаем код, который был отправлен
        self.client.post('/auth/phone/', {'phone_number': phone_number})  # Отправляем код

        response = self.client.post('/auth/verify/', {'phone_number': phone_number, 'code': code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Phone number verified successfully")

    def test_verify_code_failure(self):
        """Проверяем неверный код"""
        phone_number = '1234567890'
        wrong_code = '9999'

        self.client.post('/auth/phone/', {'phone_number': phone_number})  # Отправляем код

        response = self.client.post('/auth/verify/', {'phone_number': phone_number, 'code': wrong_code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid code or phone number")
