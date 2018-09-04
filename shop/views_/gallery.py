from django.shortcuts import render, get_list_or_404, get_object_or_404
from shop.views import summ_in_cart, get_query
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order, Photo, Amplifier
import datetime
from django.http import QueryDict

def gallery(request):
    template = loader.get_template('bshop/gallery.html')

    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)

    # query_string = ''
    # found_entries = None
    l = len(for_cart)
    for_cat_menu = Category.objects.all()
    # photos_ = Photo.objects.filter(is_alpha=True)[0:5]
    photos_ = Photo.objects.filter(amplifier__name__isnull=False, is_alpha=True)[0:5]


    if request.method == 'GET':
        params_ = request.GET
        p = QueryDict('')
        if params_:
            p = params_.copy()
        if 'q' in p:
            # print("Search", request.GET['q'])
            query_string = p.get('q')
            entry_query = get_query(query_string, ['name', 'description', ])
            found_entries = Amplifier.objects.filter(entry_query)
            query_string = 'Результат поиска - ' + str(p.get('q'))
        else:
            query_string = 'Галерея усилителей '
            found_entries = Amplifier.objects.filter()
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart), 'query_string': query_string,
               'found_entries': found_entries, 'photos': photos_, 'p': p}
    return HttpResponse(template.render(context, request))


def amplifier(request, amp="0"):
    template = loader.get_template('bshop/gallery_amp.html')

    if not request.user.is_authenticated():
        request.session.set_expiry(None)
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)

    # query_string = ''
    # found_entries = None
    l = len(for_cart)
    for_cat_menu = Category.objects.all()
    # photos_ = Photo.objects.filter(is_alpha=True)[0:5]
    amp_ = get_object_or_404(Amplifier, id=amp)
    photos_ = Photo.objects.filter(amplifier=amp_).order_by('-is_alpha')
    print(photos_)
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
               'photos': photos_, 'amp': amp_}
    return HttpResponse(template.render(context, request))