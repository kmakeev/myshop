from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.styling.bootstrap3.forms import Bootstrap3Form
from django import forms
from djng.forms import fields


class EditCartForm(Bootstrap3Form):
    status = fields.BooleanField(label='Корзина/Заказ',
        widget=forms.CheckboxInput, required=True)