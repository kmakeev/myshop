from djng.forms import NgForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from django.utils import six
from djng.styling.bootstrap3.forms import Bootstrap3Form
from djng.forms import fields
from django.forms import widgets


class CartForm(Bootstrap3Form):

    quantity = fields.DecimalField(min_value=1, max_digits=3, widget=widgets.NumberInput(), decimal_places=0)
