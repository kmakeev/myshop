from django.contrib.auth import authenticate, login
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponse
from shop.form.login_form import LoginForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Client, Category
from shop.form.register_form import RegisterForm
from shop.models import Client, Product, Category, Cart, CartElement, Order
import datetime
from shop.views import summ_in_cart, add_to_cart, send_email
from django.conf import settings
from django.shortcuts import render,get_list_or_404, get_object_or_404
from django.template.loader import render_to_string


def my_register(request, next_='/'):

    form_ = RegisterForm()
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
        form_ = RegisterForm(request.POST)
        if form_.is_valid():
            form_.save_user()
            user_ = form_.cleaned_data['login']
            password_ = form_.cleaned_data['password']
            user = authenticate(username=user_, password=password_)
            if user is not None:
                add_to_cart(for_cart, user)
                login(request, user)
                to = [form_.cleaned_data['email']]
                from_email = settings.DEFAULT_FROM_EMAIL
                subject_ = 'Регистрация на сайте'
                text_content = render_to_string('bshop/email/register.txt', {'first_name': form_.cleaned_data['firstname'],
                                                                              'username': form_.cleaned_data['login'],
                                                                              'password': form_.cleaned_data['password']})
                html_content = render_to_string('bshop/email/register.html', {'first_name': form_.cleaned_data['firstname'],
                                                                              'username': form_.cleaned_data['login'],
                                                                               'password': form_.cleaned_data['password']})
                # print(to, from_email, subject_, text_content, html_content)

                send_email(to, from_email, subject_, text_content, html_content)
                return HttpResponseRedirect(next_)
            else:
                pass
    template = loader.get_template('bshop/register.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session, 'form':form_, 'next': next_,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart), 'next': next_, 'form': form_}
    return HttpResponse(template.render(context, request))