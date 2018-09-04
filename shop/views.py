from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order, Photo
import re
from django.db.models import Q
from django.shortcuts import render, get_list_or_404, get_object_or_404
import datetime
from django.core.mail import EmailMultiAlternatives

def summ_in_cart(cart):
    summ = 0
    for i in cart:
        summ += int(i.quantity) * float(i.product.cost)
    return round(float(summ), 2)


def send_email(to, from_email, subject_,  text_content, html_content):
    msg = EmailMultiAlternatives(subject_, text_content, from_email, to)
    msg.attach_alternative(html_content, 'text/html')
    try:
        msg.send()
    except:
        pass
        # print('Send registration email error')


def add_to_cart(for_cart, user):
    ''' Добавляет позиции корзины неавторизованного пользователя к корзине авторизованного.
    Вызывается при входе пользователя, либо его регистрации

    '''
    for position in for_cart:
        owner_ = get_object_or_404(Client, user__username=user.username)
        # quantity_ = int(form.cleaned_data['quantity'])
        product_ = get_object_or_404(Product, id=position.product.id)
        # cartElement_ = CartElement.objects.create(product=product_, quantity=quantity_, is_preorder=False)
        cart_ = Cart.objects.filter(owner__user__username=user.username, status=True)
        if not cart_:
            cart_ = Cart(owner=owner_, datetime=datetime.datetime.now())
            cart_.save()
        else:
            for item in cart_:
                if item.status:
                    cart_ = item
                    break  # Пока берем первую запись не являющуюся заказом
        # Провярzем на наличие позиции в корзине у этого пользователя
        cartElement_ = CartElement.objects.filter(product=product_, cart__id=cart_.id)
        # print('found', cartElement_)
        if not cartElement_:
            cartElement_ = position
            cart_.cartElement.add(cartElement_)
            cart_.save()
        else:
            # Ориентируемся что пока у пользователя только одна текущая корзина
            cartElement_[0].quantity = cartElement_[0].quantity + position.quantity
            cartElement_[0].save()


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


# @login_required(login_url='/accounts/login/')
def gallery(request):
    photos = Photo.objects.all()
    template = loader.get_template('gallery/index.html')
    context = {'path': request.path, 'user': request.user, 'session': request.session, 'photos': photos}
    return HttpResponse(template.render(context, request))


def get_jointly(prod):
    product_ = get_object_or_404(Product, id=prod)
    carts = Cart.objects.filter(cartElement__product=product_).order_by('-datetime')[0:10]
    jointly_ = []
    if carts:
        for item in carts:
            all_product_in_cart = Product.objects.filter(cartelement__cart__id=item.id)
            for product in all_product_in_cart:
                # print(product, product_)
                if product != product_:
                    jointly_.append(product)
    return list(set(jointly_))