from django.contrib.auth import authenticate, login
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from shop.form.login_form import LoginForm
from shop.form.restore_form import RestoreForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Client, Product, Category, Cart, CartElement, Order, Key, User
import datetime
from shop.views import summ_in_cart, add_to_cart, send_email
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.exceptions import ValidationError
# from django.shortcuts import render, get_list_or_404, get_object_or_404

def my_login(request, next_='/'):

    form_ = LoginForm()
    restore_form_ = RestoreForm()
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
    isError = False
    if request.method == 'POST':
        if 'Login' in request.POST:
             form_ = LoginForm(request.POST)
             if form_.is_valid():
                user_ = form_.cleaned_data['login']
                password_ = form_.cleaned_data['password']
                user = authenticate(username=user_, password=password_)
                if user is not None:
                    add_to_cart(for_cart, user)
                    login(request, user)
                    # print(next_)
                    return HttpResponseRedirect(next_)
                else:
                    pass
                    # raise Http404()
        elif 'Restore' in request.POST:
            restore_form_ = RestoreForm(request.POST)
            if restore_form_.is_valid():
                username_ = restore_form_.cleaned_data['login']
                user = User.objects.filter(username=username_)
                # print(user)
                if user:
                    user = user[0]
                    email_ = user.email
                    new_key_ = Key.objects.create(login=user.username)
                    new_key_.save()
                    # print(new_key_)
                    to = [email_]
                    from_email = settings.DEFAULT_FROM_EMAIL
                    subject_ = 'Восстановление пароля'
                    text_content = render_to_string('bshop/email/restore.txt',
                                                    {'email': email_,
                                                     'username': username_,
                                                     'key': new_key_.key})
                    html_content = render_to_string('bshop/email/restore.html',
                                                    {'email': email_,
                                                     'username': username_,
                                                     'key': new_key_.key})
                    send_email(to, from_email, subject_, text_content, html_content)
                else:
                    isError = True
            else:
                isError = True
                # raise ValidationError('Пользователь с таким логином не зарегистрирован в системе', code='invalid')
                # print('Form is invalid or user not exist')

    template = loader.get_template('bshop/login.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart), 'next': next_, 'form': form_, 'email_form': restore_form_, 'error': isError}
    return HttpResponse(template.render(context, request))

