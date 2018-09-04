from djng.styling.bootstrap3.forms import Bootstrap3Form
from django import forms
from djng.forms import fields


class CommentForm(Bootstrap3Form):
    comment = fields.CharField(label='Комментарий к заказу', required=False,
                                widget=forms.Textarea(attrs={'cols': '80', 'rows': '5'}))