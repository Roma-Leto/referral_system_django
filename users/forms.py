from django import forms


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'placeholder': 'Введите номер телефона'}))


class VerificationCodeForm(forms.Form):
    verification_code = forms.CharField(max_length=4, widget=forms.TextInput(
        attrs={'placeholder': 'Введите код верификации'}))


class ActiveInviteCodeView(forms.Form):
    activated_invite_code = forms.CharField(max_length=6, min_length=6, label="Код...",
                                        widget=forms.TextInput(
                                            attrs={'placeholder': 'Введите инвайт-код'}
                                        ))
