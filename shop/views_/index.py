from shop.views import summ_in_cart, get_query
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order, Photo
import datetime
from django.http import QueryDict
from django.contrib.auth.decorators import login_required
from shop.form.login_form import LoginForm
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login

# @login_required(login_url='/accounts/login/')
def index(request):
    template = loader.get_template('bshop/content.html')

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
    photos_ = Photo.objects.filter(is_alpha=True)[0:5]
    # print(photos_)

    if request.method == 'GET':
        params_ = request.GET
        p = QueryDict('')
        if params_:
            p = params_.copy()
        if 'q' in p:
            # print("Search", request.GET['q'])
            query_string = p.get('q')
            entry_query = get_query(query_string, ['product__name', 'product__description', ])
            found_entries = Product.objects.filter(entry_query)
            query_string = 'Результат поиска - ' + str(p.get('q'))
        else:
            query_string = 'Последнее добавленное '
            found_entries = Product.objects.filter()
        f_ispreorder = p.get('ispreorder')
        if f_ispreorder == 'True' or f_ispreorder == 'False':
            found_entries = found_entries.filter(is_preorder=f_ispreorder)
        if 'sort' in p:
            sort_ = p.get('sort')
            if sort_ == 'PRICEUP':
                found_entries = found_entries.order_by('cost')
            if sort_ == 'PRICEDOWN':
                found_entries = found_entries.order_by('-cost')
            if sort_ == 'AVIALABLE':
                found_entries = found_entries.order_by('is_preorder')

    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart), 'query_string': query_string,
               'found_entries': found_entries, 'photos': photos_, 'p': p, 'sort': Product.by_sort}
    return HttpResponse(template.render(context, request))