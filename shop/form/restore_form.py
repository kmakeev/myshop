from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django import forms
from djng.forms import NgModelFormMixin
from django.contrib.auth.models import User
from djng.forms import fields


class RestoreForm_(Bootstrap3Form):

    login = fields.CharField(label='Логин', min_length=2, max_length=20, required=True,
                            help_text='Введите ваш логин. '
                                      'На адрес электронной почты, указанной в параметрах вашей учетной записи, будет отправлено письмо с инструкция по восстановлению пароля. '
                                      'Если вы не получите отправленное письмо или забыли свой логин, пожалуйста, свяжитесь с администрацией сайта.')


class RestoreForm(NgModelFormMixin, RestoreForm_):

    form_name = 'email_form'


