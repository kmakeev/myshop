from djng.styling.bootstrap3.forms import Bootstrap3Form
from django import forms
from djng.forms import fields


class DateTimeForm(Bootstrap3Form):
    start_date = fields.DateField(label='С', required=False, input_formats=['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d'])
    end_date = fields.DateField(label='По', required=False, input_formats=['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d'])

