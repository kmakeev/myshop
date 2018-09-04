from django import forms
from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.core.exceptions import ValidationError
from djng.forms import NgForm, NgModelFormMixin, NgFormValidationMixin
from django.contrib.auth.models import User
from shop.models import Client
from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.forms import fields

class UpdateForm_(Bootstrap3Form):

    # login = forms.CharField(label='Логин', min_length=2, max_length=20, required=True,
    #                       error_messages={'invalid': 'Поле должно быть заполнено'})
    firstname = fields.CharField(label='Имя', min_length=2, max_length=100, required=True)
    lastname = fields.CharField(label='Фамилия', min_length=2, max_length=100, required=True)
    middlename = fields.CharField(label='Отчество', min_length=2, max_length=100, required=True)
    address = fields.CharField(label='Адрес', required=True,
                                widget=forms.Textarea(attrs={'cols': '80', 'rows': '3'}))
    tel = fields.RegexField(r'^\+?[0-9 .-]{4,14}$', label='Телефон', max_length=15,
                             error_messages={'invalid': '4-14 цифр, начинается с \'+\''})
    old_password = fields.CharField(label='Текущий пароль', widget=forms.PasswordInput, required=False,
                               min_length=5, error_messages={'invalid': 'Не менее 5 символов'})
    password_re = fields.CharField(label='Новый пароль', widget=forms.PasswordInput, required=False,
                                  min_length=5, error_messages={'invalid': 'Не менее 5 символов'})
    password_re2 = fields.CharField(label='Новый пароль еще раз', widget=forms.PasswordInput, required=False,
                                  min_length=5, error_messages={'invalid': 'Не менее 5 символов'})

class UpdateForm(NgFormValidationMixin, UpdateForm_):

    form_name = 'update_form'
