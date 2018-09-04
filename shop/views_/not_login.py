from django.contrib.auth import authenticate, login
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from shop.form.not_login_form import NotLoginForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Category
from shop.models import Client, Product, Category, Cart, CartElement, Order
import datetime
from shop.views import summ_in_cart, add_to_cart, send_email
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string

def not_login(request, next_='/'):

    form_ = NotLoginForm()
    for_cat_menu = Category.objects.all()

    if ('next' in request.GET) and request.GET['next'].strip():
        next_ = request.GET['next']

    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)

    else:
        return HttpResponseRedirect(reverse_lazy('cart'))
    l = len(for_cart)
    if request.method == 'POST':
         form_ = NotLoginForm(request.POST)
         if form_.is_valid():
            # print('Save order')
            p = form_.save_person()
            # print(p)
            owner_ = get_object_or_404(Client, user__username='None')
            cart_ = Cart.objects.filter(owner__user__username='None', key=request.session['key'], status=True)
            comment = form_.cleaned_data['comment']
            if not cart_:
                cart_ = Cart(owner=owner_, datetime=datetime.datetime.now(), key=request.session['key'])
                cart_.save()
            else:
                for item in cart_:
                    if item.status:
                        cart_ = item
                        break  # Пока берем первую запись не являющуюся заказом

            new_order = Order(list=cart_, datetime=datetime.datetime.now(), status='NEW', comment=comment, person=p)
            new_order.save()
            cart_.status = False
            cart_.summ = summ_in_cart(for_cart)
            cart_.save()
            # print(" Sending mail")
            for_order = CartElement.objects.filter(cart__id=new_order.list.id)
            # user = request.user
            to = [p.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            subject_ = 'Новый заказ - ' + str(new_order.id)
            text_content = render_to_string('bshop/email/neworder.txt',
                                            {'first_name': p.first_name,
                                             'summ_in_cart': summ_in_cart(for_cart),
                                             'order': new_order,
                                             'positions': for_order})
            html_content = render_to_string('bshop/email/neworder.html',
                                            {'first_name': p.first_name,
                                             'summ_in_cart': summ_in_cart(for_cart),
                                             'order': new_order,
                                             'positions': for_order})
            # print(to, from_email, subject_, html_content)

            send_email(to, from_email, subject_, text_content, html_content)
            to = [settings.ADMIN_EMAIL]
            send_email(to, from_email, subject_, text_content, html_content)

            return HttpResponseRedirect(reverse_lazy('orders'))

    template = loader.get_template('bshop/notlogin.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart), 'next': next_, 'form': form_}
    return HttpResponse(template.render(context, request))