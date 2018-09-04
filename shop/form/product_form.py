from djng.styling.bootstrap3.forms import Bootstrap3Form
from django import forms
from djng.forms import fields


class ProductForm(Bootstrap3Form):
    quantity = fields.DecimalField(min_value=1, max_digits=3, initial=1, widget=forms.NumberInput(), decimal_places=0)
