from djng.forms.fields import FloatField
from django import forms
from djng.styling.bootstrap3.forms import Bootstrap3Form
from django.core.exceptions import ValidationError
from djng.forms import NgForm, NgModelFormMixin, NgFormValidationMixin
from django.contrib.auth.models import User
from shop.models import Client, Person
from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.forms import fields


class NotLoginForm_(Bootstrap3Form):

    firstname = fields.CharField(label='Имя', min_length=2, max_length=100, required=True,
                                error_messages={'invalid': 'Минимум 2 символа'})
    lastname = fields.CharField(label='Фамилия', min_length=2, max_length=100, required=True,
                               error_messages={'invalid': 'Минимум 2 символа'})
    middlename = fields.CharField(label='Отчество', min_length=2, max_length=100, required=True,
                                 error_messages={'invalid': 'Минимум 2 символа'})
    email = fields.EmailField(label='E-Mail', required=True, error_messages={'invalid': 'e-mail@domain.com'},
                             help_text='Информация о  заказе будет выслана на указанный Вами e-mail')
    address = fields.CharField(label='Адрес', required=True,
                                widget=forms.Textarea(attrs={'cols': '80', 'rows': '3'}))
    tel = fields.RegexField(r'^\+?[0-9 .-]{4,25}$', label='Телефон',
                             error_messages={'invalid': '4-25 цифр, начинается с \'+\''})

    comment = fields.CharField(label='Комментарий к заказу', required=False,
                              widget=forms.Textarea(attrs={'cols': '80', 'rows': '5'}))


class NotLoginForm(NgFormValidationMixin, NotLoginForm_):

    def save_person(self):
        # print('Adding', self.cleaned_data.get('firstname'), self.cleaned_data.get('tel'))


        p = Person(first_name=self.cleaned_data.get('firstname'),last_name=self.cleaned_data.get('lastname'),
                    middle_name=self.cleaned_data.get('middlename'), email=self.cleaned_data.get('email'),
                   address=self.cleaned_data.get('address'), tel=self.cleaned_data.get('tel'))
        p.save()
        return p

