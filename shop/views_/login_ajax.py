from django.contrib.auth import authenticate, login
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from shop.form.login_form import LoginForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Category
from shop.models import Client, Product, Category, Cart, CartElement, Order
import datetime
from shop.views import summ_in_cart, add_to_cart
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.utils.encoding import force_text
import json


def my_login(request, next_='/'):
    form_ = LoginForm
    for_cat_menu = Category.objects.all()

    if ('next' in request.GET) and request.GET['next'].strip():
        next_ = request.GET['next']

    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        # session = request.session['key']
        # print(request.session['last_date'], session)
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)

    else:
        return HttpResponseRedirect(reverse_lazy('index'))
    l = len(for_cart)
    if request.method == 'POST':
        if request.is_ajax():
            # print('In ajax ', json.loads(request.body.decode('utf-8')))
            in_data = json.loads(request.body.decode('utf-8'))
            # print(in_data)
            form_ = LoginForm(data=in_data)
            # print('form - ', form_)
            user_ = in_data['login']
            password_ = in_data['password']
            # print(user_, password_)
            user = authenticate(username=user_, password=password_)
            if user is not None:
                add_to_cart(for_cart, user)
                login(request, user)
                response_data = {'errors': form_.errors, 'success_url': force_text(next_)}
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                # print('form is invalid', form_)
                response_data = {'errors': form_.errors, 'success_url': force_text(next_)}
                return HttpResponse(json.dumps(response_data), content_type="application/json")

    template = loader.get_template('bshop/login_ajax.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart), 'next': next_, 'form': form_}
    return HttpResponse(template.render(context, request))

