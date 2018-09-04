from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order
from shop.form.product_form import ProductForm
from shop.form.cart_element_form import CartForm
from django.forms import formset_factory
# from django.contrib.sessions.backends.db import SessionStore
# from django.contrib.sessions.models import Session
import datetime
from  django.core.exceptions import *
from django.contrib.auth.decorators import login_required
from shop.views import summ_in_cart

@login_required(login_url='/accounts/login/')
def order(request, order = '0'):
    template = loader.get_template('bshop/order.html')
    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        order_ = get_object_or_404(Order, list__key=request.session['key'], id=order)
        for_order = CartElement.objects.filter(cart__id=order_.list.id)
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)

    else:
        order_ = get_object_or_404(Order,list__owner__user__username=request.user.username, id=order)
        for_order = CartElement.objects.filter(cart__id=order_.list.id)
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
    l = len(for_cart)
    for_cat_menu = Category.objects.all()
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session, 'order': order_, 'positions': for_order,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart)}

    return HttpResponse(template.render(context, request))