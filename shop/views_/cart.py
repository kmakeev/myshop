from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order
from shop.form.cart_element_form import CartForm
from django.forms import formset_factory
from shop.views import summ_in_cart, send_email
import datetime
from django.contrib.auth.decorators import login_required
from shop.form.comment_form import CommentForm
from django.conf import settings
from django.template.loader import render_to_string


# @login_required(login_url='/accounts/login/')
def cart(request):

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
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
    l = len(for_cart)
    all_product_not_archive = True
    data_ = dict()
    formset = []
    form = CommentForm()
    if l:
        """form_data = {
            'form-TOTAL_FORMS': str(l),
            'form-INITIAL_FORMS:': str(l),
            'form-MAX_NUM_FORMS': str(l),
        }"""
        CartFormSet = formset_factory(CartForm, max_num=l, can_delete=True)
        if request.method == 'POST':
            formset = CartFormSet(request.POST, request.FILES)
            if formset.is_valid():
                # print('Update cart')
                on_delete = False
                for i in range(len(for_cart)):
                    # print(for_cart[i].quantity, for_cart[i].id, formset[i].cleaned_data['quantity'])
                    if (for_cart[i].quantity != formset[i].cleaned_data['quantity']):
                        # print(for_cart[i].quantity, formset[i].cleaned_data['quantity'])
                        try:
                            cart_element = CartElement.objects.get(id=for_cart[i].id)
                            product = get_object_or_404(Product, id=cart_element.product.id)
                            if cart_element.is_preorder:
                                # print('preorder change')
                                cart_element.quantity = formset[i].cleaned_data['quantity']
                                cart_element.save()
                            elif not cart_element.is_preorder:
                                # print('Edit in stock')
                                if cart_element.quantity > formset[i].cleaned_data['quantity']:
                                    # print('Is in dec quantity', cart_element.quantity, formset[i].cleaned_data['quantity'])
                                    # print('Old - ', product.quantity_in_reserv)
                                    product.quantity_in_reserv -= int(cart_element.quantity) - int(formset[i].cleaned_data['quantity'])
                                    if product.quantity_in_reserv < 0:
                                        product.quantity_in_reserv = 0
                                    product.save()
                                    # print('New - ', product.quantity_in_reserv)
                                    cart_element.quantity = formset[i].cleaned_data['quantity']
                                else:
                                    # print('Is in add quantity')
                                    if (product.quantity - product.quantity_in_reserv) >= (formset[i].cleaned_data['quantity'] - cart_element.quantity):
                                        # print('Is Ok in rexize quantity')
                                        product.quantity_in_reserv += formset[i].cleaned_data['quantity'] - cart_element.quantity
                                        cart_element.quantity = formset[i].cleaned_data['quantity']
                                        product.save()

                                cart_element.save()
                        except:
                            pass
                    if formset[i].cleaned_data['DELETE']:
                        try:
                            cart_element = CartElement.objects.get(id=for_cart[i].id)
                            product = get_object_or_404(Product, id=cart_element.product.id)
                            # print(product)
                            if not product.is_preorder and (product.quantity_in_reserv - cart_element.quantity) >= 0:
                                product.quantity_in_reserv -= cart_element.quantity
                                product.save()
                            cart_element.delete()
                            on_delete = True
                        except:
                            pass

                if on_delete:
                    return HttpResponseRedirect(reverse_lazy('cart'))
            if 'Order' in request.POST:
                # print('Is Place order')
                # Переполучаем корзину, т.к. она могла обновиться на форме и обработана выше.
                if not request.user.is_authenticated():
                    for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
                else:
                    for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username,
                                                          cart__status=True)
                # Проверки на наличие в корзине товара со статусом не доступен к заказу (обход запреда нажатия html кнопок)
                for i in for_cart:
                    if not i.product.is_not_arhive:
                        return HttpResponseRedirect(reverse_lazy('cart'))  #Если есть, редиректим на страницу корзины

                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.cleaned_data['comment']
                if request.user.is_authenticated:
                    cart_ = Cart.objects.filter(owner__user__username=request.user.username, status=True)
                    if cart_:
                        for item in cart_:
                            if item.status:
                                cart_ = item
                                break  # Пока берем первую запись не являющуюся заказом

                        new_order = Order(list=cart_, datetime=datetime.datetime.now(), status='NEW', comment=comment)
                        new_order.save()
                        cart_.status = False
                        cart_.summ = summ_in_cart(for_cart)
                        cart_.save()
                        # print(" Sending mail")
                        for_order = CartElement.objects.filter(cart__id=new_order.list.id)
                        user = request.user
                        to = [user.email]
                        from_email = settings.DEFAULT_FROM_EMAIL
                        subject_ = 'Новый заказ - ' + str(new_order.id)
                        text_content = render_to_string('bshop/email/neworder.txt',
                                                        {'first_name': request.user.first_name,
                                                         'username': user.username,
                                                         'summ_in_cart': summ_in_cart(for_cart),
                                                         'order': new_order,
                                                         'positions': for_order})
                        html_content = render_to_string('bshop/email/neworder.html',
                                                        {'first_name': request.user.first_name,
                                                         'username': user.username,
                                                         'summ_in_cart': summ_in_cart(for_cart),
                                                         'order': new_order,
                                                         'positions': for_order})
                        # print(to, from_email, subject_, html_content)

                        send_email(to, from_email, subject_, text_content, html_content)

                        to = [settings.ADMIN_EMAIL]
                        send_email(to, from_email, subject_, text_content, html_content)

                        return HttpResponseRedirect(reverse_lazy('orders'))
                else:
                    # Нужно авторизовать или зарегистрировать пользователя, после чего добавить ему товар из сессии
                    # и отправить на страницу оформления заказа
                    # Скорее всего решается требованием работы со страницей потверждения заказа только автотизованного пользователя
                    return HttpResponseRedirect(reverse_lazy('login'))

            return HttpResponseRedirect(reverse_lazy('cart'))

        else:
            init_ = []
            for i in for_cart:
                if not i.product.is_not_arhive:
                    all_product_not_archive = False
                init_.append({'quantity': i.quantity})
            # formset = CartFormSet(form_data, initial=init_)
            formset = CartFormSet(initial=init_)
        data_ = dict(pairs=zip(for_cart, formset))


    template = loader.get_template('bshop/cart.html')
    for_cat_menu = Category.objects.all()
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart), 'formset': formset, 'data': data_, 'form': form,
               'alert_archive': all_product_not_archive}

    return HttpResponse(template.render(context, request))