from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.styling.bootstrap3.forms import Bootstrap3Form
from shop.models import Order
from django import forms
from djng.forms import fields

class EditOrderForm(Bootstrap3Form):

    status = fields.ChoiceField(choices=Order.status_in_choices, label='Статус',
                                widget=forms.RadioSelect, required=True)
    prepay = fields.FloatField(label='Сумма предоплаты', required=True)
    relay_free = fields.FloatField(label='Сумма оплаты за пересылку')
    total = fields.FloatField(label='Итоговая сумма', required=True)
    type_of_dispatch = fields.ChoiceField(choices=Order.dispatch, label='Тип отправления', widget=forms.Select, required=True)
    track_number = fields.CharField(label='Номер для отслеживания',  min_length=0, max_length=20, required=False)
    linked_orders = fields.CharField(label='Связанные заказы', min_length=0, max_length=100, required=False)

