from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django import forms
from djng.forms import NgModelFormMixin
from djng.forms import fields


class ChangePasswordForm_(Bootstrap3Form):

    password = fields.CharField(label='Введите пароль', widget=forms.PasswordInput, required=True,
                               min_length=5, error_messages={'invalid': 'Не менее 5 символов'})
    password_re = fields.CharField(label='Ведите пароль еще раз', widget=forms.PasswordInput, required=True,
                                  min_length=5, error_messages={'invalid': 'Не менее 5 символов'})


class ChangePasswordForm(NgModelFormMixin, ChangePasswordForm_):

    form_name = 'changePwd_form'

    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_re'):

            # msg = 'Введенные пароли не совпадают'
            # self.add_error('password', msg)
            # self.add_error('password_re', msg)
            raise ValidationError('Введенные пароли не совпадают', code='invalid')

        return super(ChangePasswordForm, self).clean()