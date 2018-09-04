from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order, Photo, Drawing
from shop.form.product_form import ProductForm
import datetime
from shop.views import summ_in_cart, get_jointly
from django.contrib.auth.decorators import login_required


# @login_required(login_url='/accounts/login/')
def product(request, cat="0", prod="0"):
    template = loader.get_template('bshop/product.html')
    for_cat_menu = Category.objects.all()
    name_ = ''
    for i in for_cat_menu:
        if int(cat) == int(i.id):
            name_ = i.name
    if not name_:
        return HttpResponseRedirect(reverse_lazy('index'))
    product_ = get_object_or_404(Product, id=prod)
    photos_ = Photo.objects.filter(product_in_time=product_.product).order_by('-is_alpha')
    jointly_ = get_jointly(prod)
    drawings_ = Drawing.objects.filter(product_in_time=product_.product)
    # print(drawings_)
    if not request.user.is_authenticated():
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
    l = len(for_cart)
    # обновляем сумму заказа
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                owner_ = get_object_or_404(Client, user__username=request.user.username)
                quantity_ = int(form.cleaned_data['quantity'])
                product_ = get_object_or_404(Product, id=prod, is_not_arhive=True)
                # cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_, is_preorder=False)
                cart_ = Cart.objects.filter(owner__user__username=request.user.username, status=True)
                if not cart_:
                    cart_ = Cart(owner=owner_, datetime=datetime.datetime.now())
                    cart_.save()
                else:
                    for item in cart_:
                        if item.status:
                            cart_ = item
                            break                   # Пока берем первую запись не являющуюся заказом
                # Провярzем на наличие позиции в корзине у этого пользователя
                cartElement_= CartElement.objects.filter(product=product_, cart__id=cart_.id)
                # print('found', cartElement_)
                if not cartElement_:
                    if product_.is_preorder:
                        cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_,
                                                                  is_preorder=True)
                        cart_.cartElement.add(cartElement_)
                        cart_.save()
                    elif product_.is_in_stock and (product_.quantity - product_.quantity_in_reserv) >= quantity_:
                        cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_,
                                                                  is_preorder=False)
                        # product_.quantity -= quantity_
                        product_.quantity_in_reserv += quantity_
                        product_.save()
                        cart_.cartElement.add(cartElement_)
                        cart_.save()
                    else:
                        # print('Not Adding in stok < reserv', product_.quantity, product_.quantity_in_reserv)
                        pass


                else:
                    # Ориентируемся что пока у пользователя только одна текущая корзина
                    if product_.is_preorder:
                        if cartElement_[0].is_preorder:
                            cartElement_[0].quantity = cartElement_[0].quantity + quantity_
                            cartElement_[0].save()
                    elif not cartElement_[0].is_preorder and (product_.quantity - product_.quantity_in_reserv) >= quantity_:
                        if not cartElement_[0].is_preorder:
                            # product_.quantity -= quantity_
                            product_.quantity_in_reserv += quantity_
                            product_.save()
                            cartElement_[0].quantity = cartElement_[0].quantity + quantity_
                            cartElement_[0].save()
                    else:
                        # print('Not Adding 2 in stok < reserv', product_.quantity, product_.quantity_in_reserv)
                        pass


            else:
                owner_ = get_object_or_404(Client, user__username='None')
                quantity_ = int(form.cleaned_data['quantity'])
                product_ = get_object_or_404(Product, id=prod, is_not_arhive=True)
                # cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_, is_preorder=False)
                cart_ = Cart.objects.filter(owner__user__username='None', key=request.session['key'], status=True)
                if not cart_:
                    cart_ = Cart(owner=owner_, datetime=datetime.datetime.now(), key=request.session['key'])
                    cart_.save()
                else:
                    for item in cart_:
                        if item.status:
                            cart_ = item
                            break                   # Пока берем первую запись не являющуюся заказом
                # Провярzем на наличие позиции в корзине у этого пользователя
                cartElement_ = CartElement.objects.filter(product=product_,
                                                          cart__id=cart_.id)
                # print('found', cartElement_)
                if not cartElement_:
                    if product_.is_preorder:
                        cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_, is_preorder=True)
                        cart_.cartElement.add(cartElement_)
                        cart_.save()
                    elif product_.is_in_stock and (product_.quantity - product_.quantity_in_reserv) >= quantity_:
                        cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_,
                                                                  is_preorder=False)
                        # product_.quantity -= quantity_
                        product_.quantity_in_reserv += quantity_
                        product_.save()
                        cart_.cartElement.add(cartElement_)
                        cart_.save()
                    else:
                        # print('Not Adding in stok < reserv', product_.quantity, product_.quantity_in_reserv)
                        pass
                else:
                    # Ориентируемся что пока у пользователя только одна текущая корзина
                    if product_.is_preorder:
                        if cartElement_[0].is_preorder:
                            cartElement_[0].quantity = cartElement_[0].quantity + quantity_
                            cartElement_[0].quantity = cartElement_[0].quantity + quantity_
                            cartElement_[0].save()
                    elif not cartElement_[0].is_preorder and (product_.quantity - product_.quantity_in_reserv) >= quantity_:
                        if not cartElement_[0].is_preorder:
                            # product_.quantity -= quantity_
                            product_.quantity_in_reserv += quantity_
                            product_.save()
                            cartElement_[0].quantity = cartElement_[0].quantity + quantity_
                            cartElement_[0].save()
                    else:
                        # print('Not Adding 2 in stok < reserv', product_.quantity, product_.quantity_in_reserv)
                        pass
        return HttpResponseRedirect(request.path)
    else:
        form = ProductForm()
        if product_.is_in_stock and (product_.quantity_in_reserv >= product_.quantity):
            is_missing_quantity = True
        else:
            is_missing_quantity = False

    context = {'menu': for_cat_menu, 'path': request.path, 'prod': product_, 'name': name_, 'catalog_id': cat,
             'form': form, 'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
             'photos': photos_, 'is_missing': is_missing_quantity, 'jointly': jointly_, 'drawings': drawings_}
    return HttpResponse(template.render(context, request))

