
from django import forms
from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.core.exceptions import ValidationError
from djng.forms import NgForm, NgModelFormMixin, NgFormValidationMixin
from django.contrib.auth.models import User
from shop.models import Client
from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.forms import fields


class RegisterForm_(Bootstrap3Form):
    login = fields.CharField(label='Логин', min_length=2, max_length=20, required=True,
                            error_messages={'invalid': 'Поле должно быть заполнено'})
    firstname = fields.CharField(label='Имя', min_length=2, max_length=100, required=True)
    lastname = fields.CharField(label='Фамилия', min_length=2, max_length=100, required=True)
    middlename = fields.CharField(label='Отчество', min_length=2, max_length=100, required=True)
    email = fields.EmailField(label='E-Mail', required=True, error_messages={'invalid': 'e-mail@domain.com'},
                             help_text='После регистации на указанный e-mail будет направлено письмо с Вашими учетными данными.'
                                       ' Если Вы не получили данное письмо, сообщите об этом нам по электронной почте.')
    address = fields.CharField(label='Адрес', required=True,
                              widget=forms.Textarea(attrs={'cols': '80', 'rows': '3'}))
    tel = fields.RegexField(r'^\+?[0-9 .-]{4,14}$', label='Телефон',
                           error_messages={'invalid': '4-14 цифр, начинается с \'+\''})
    password = fields.CharField(label='Введите пароль', widget=forms.PasswordInput, required=True,
                               min_length=5, error_messages={'invalid': 'Не менее 5 символов'})
    password_re = fields.CharField(label='Ведите пароль еще раз', widget=forms.PasswordInput, required=True,
                                  min_length=5, error_messages={'invalid': 'Не менее 5 символов'})


class RegisterForm(NgFormValidationMixin, RegisterForm_):
    def save_user(self):
        # print('Adding', self.cleaned_data.get('login'))
        u = User.objects.create_user(self.cleaned_data.get('login'), self.cleaned_data.get('email'),
                                    self.cleaned_data.get('password'))
        u.first_name = self.cleaned_data.get('firstname')
        u.last_name = self.cleaned_data.get('lastname')
        u.save()
        c = Client(user=u)
        c.address = self.cleaned_data.get('address')
        c.middle_name = self.cleaned_data.get('middlename')
        c.tel = self.cleaned_data.get('tel')
        c.save()

    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_re'):

            # msg = 'Введенные пароли не совпадают'
            # self.add_error('password', msg)
            # self.add_error('password_re', msg)
            raise ValidationError('Введенные пароли не совпадают', code='invalid')

        if User.objects.filter(username=self.cleaned_data.get('login')):
            # msg = 'Пользователь с таким логином уже есть в системе'
            raise ValidationError('Пользователь с таким логином уже есть в системе', code='invalid')

        return super(RegisterForm, self).clean()