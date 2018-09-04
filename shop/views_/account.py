from django.contrib.auth.hashers import make_password, check_password
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from shop.form.update_form import UpdateForm
from shop.form.change_password_form import ChangePasswordForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Category
from shop.models import Client, Product, Category, Cart, CartElement, Order, User, Key
import datetime
from django.utils import timezone
from shop.views import summ_in_cart, add_to_cart
from django.shortcuts import render, get_list_or_404, get_object_or_404
import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string


def account(request):

    for_cat_menu = Category.objects.all()
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('index'))
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        client_ = get_object_or_404(Client, user__username=request.user.username)
        data = {'firstname': client_.user.first_name, 'lastname': client_.user.last_name,
                'middlename': client_.middle_name,
                'tel': client_.tel, 'address': client_.address}
        form_ = UpdateForm(data)
    l = len(for_cart)
    if request.method == 'POST':
         form_ = UpdateForm(request.POST)
         if form_.is_valid():
            c = get_object_or_404(Client, user__username=request.user.username)
            u = request.user
            u.first_name = form_.cleaned_data.get('firstname')
            u.last_name = form_.cleaned_data.get('lastname')
            u.save()
            c.address = form_.cleaned_data.get('address')
            c.middle_name = form_.cleaned_data.get('middlename')
            c.tel = form_.cleaned_data.get('tel')
            c.save()
            if form_.cleaned_data.get('password_re') or form_.cleaned_data.get('password_re'):
                # print('password user', form_.cleaned_data.get('old_password'), u.password)
                if check_password(form_.cleaned_data.get('old_password'), u.password):
                    if form_.cleaned_data.get('password_re') == form_.cleaned_data.get('password_re2'):
                        try:
                            u.password = make_password(form_.cleaned_data.get('password_re'))
                            u.save()
                        except:
                            form_.add_error(field=None,
                                            error=ValidationError(
                                                'Возникла ошибка при сохранении нового пароля, обратитесь к администратору',
                                                code='invalid'))
                    else:
                        form_.add_error(field=None,
                                        error=ValidationError(
                                            'Введенные новые пароли пользователя не совпадают', code='invalid'))
                else:
                    form_.add_error(field=None,
                                    error=ValidationError(
                                        'Неверно указан текущий пароль пользователя',
                                        code='invalid'))


    template = loader.get_template('bshop/account.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart),'form': form_}
    return HttpResponse(template.render(context, request))


def restorePwd(request):

    for_cat_menu = Category.objects.all()
    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
    if ('key' in request.GET) and request.GET['key'].strip():
        key_ = request.GET['key']
        # print("Get Change Password for key", key_)
    else:
        return HttpResponseRedirect(reverse_lazy('login'))

    l = len(for_cart)
    form_ = ChangePasswordForm()
    isChangeOk = False
    if request.method == 'POST':
        if key_:
            # print("POST Change Password for key", key_)
            form_ = ChangePasswordForm(request.POST)
            if form_.is_valid():
                # print('Edit ')
                try:
                    a = uuid.UUID(key_)
                    # print('Is valid uuid', a)
                    k = Key.objects.filter(key=key_)[0]
                    # print(k)
                    # k = get_object_or_404(Key, )
                    if k and not k.isUsed:
                        if timezone.now() < k.datetime + datetime.timedelta(hours=24):
                            u = get_object_or_404(User, username=k.login)
                            # print(u, k)
                            try:
                                u.password = make_password(form_.cleaned_data.get('password'))
                                u.save()
                                k.isUsed = True
                                k.save()
                                isChangeOk = True
                                # return HttpResponseRedirect(reverse_lazy('login'))
                            except:
                                # print("Passsword change error")
                                form_.add_error(field=None,
                                                error=ValidationError(
                                                    'Возникла ошибка при сохранении нового пароля, обратитесь к администратору',
                                                    code='invalid'))
                        else:
                            # print("Key key is expired")
                            form_.add_error(field=None,
                                            error=ValidationError('Срок действия ключа для восстановления пароля истек',
                                                                  code='invalid'))
                    else:
                        # print('key is used')
                        form_.add_error(field=None,
                                        error=ValidationError('Ключ для восстановления пароля уже использован',
                                                              code='invalid'))
                except:
                    # print('Is not valid uuid')
                    form_.add_error(field=None, error=ValidationError('Неверный формат ключа для восстановления пароля',
                                                                      code='invalid'))

    template = loader.get_template('bshop/restore_password.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart), 'form': form_, 'key': key_, 'isChangeOk': isChangeOk}
    return HttpResponse(template.render(context, request))