from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django import forms
from djng.forms import NgModelFormMixin
from djng.forms import fields

class LoginForm_(Bootstrap3Form):

    login = fields.CharField(label='Логин', min_length=2, max_length=20, required=True,
                           error_messages={'invalid': 'Поле должно быть заполнено. Минимум 2 символа, максимум 20'})
    password = fields.CharField(label='Пароль', widget=forms.PasswordInput, required=True)


class LoginForm(NgModelFormMixin, LoginForm_):

    scope_prefix = 'subscribe_data'
    form_name = 'login_form'

    def clean(self):
        if not ('login' in self.cleaned_data and 'password' in self.cleaned_data):
            raise ValidationError('Необходимо указать имя пользователя и пароль', code='invalid')
        user_ = self.cleaned_data['login']
        password_ = self.cleaned_data['password']
        if authenticate(username=user_, password=password_) is None:
            raise ValidationError('Введен неверный логин или пароль пользователя', code='invalid')
        return super(LoginForm, self).clean()



