from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from shop.views import summ_in_cart, get_query
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order, Photo
import datetime
from django.http import QueryDict
from django.contrib.auth.decorators import login_required


# @login_required(login_url='/accounts/login/')
def menu(request, cat="0"):
    template = loader.get_template('bshop/in_catalog.html')
    for_cat_menu = Category.objects.all()
    name_ = ''
    for_content = {}

    for i in for_cat_menu:
        # str = i.get_absolute_url()
        if int(cat) == int(i.id):
            name_ = i.name
            for_content = Product.objects.filter(product__category=i.id)
    if not name_:
        return HttpResponseRedirect(reverse_lazy('index'))

    if request.method == 'GET':
        params_ = request.GET
        p = QueryDict('')
        if params_:
            p = params_.copy()
        if 'q' in p:
            # print("Search", request.GET['q'])
            query_string = p.get('q')
            entry_query = get_query(query_string, ['product__name', 'product__description', ])
            for_content = for_content.filter(entry_query)
            query_string = 'Результат поиска - ' + str(p.get('q'))
        else:
            query_string = name_

        f_ispreorder = p.get('ispreorder')
        if f_ispreorder == 'True' or f_ispreorder == 'False':
            for_content = for_content.filter(is_preorder=f_ispreorder)

        if 'sort' in p:
            sort_ = p.get('sort')
            if sort_ == 'PRICEUP':
                for_content = for_content.order_by('cost')
            if sort_ == 'PRICEDOWN':
                for_content = for_content.order_by('-cost')
            if sort_ == 'AVIALABLE':
                for_content = for_content.order_by('is_preorder')

    if not request.user.is_authenticated():
        if 'key' not in request.session:
            request.session['last_date'] = str(datetime.datetime.now())
            request.session.save()
            request.session['key'] = request.session.session_key
        for_cart = CartElement.objects.filter(cart__key=request.session['key'], cart__status=True)
    else:
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
    l = len(for_cart)
    category_ = get_object_or_404(Category, id=cat)
    photos_ = get_list_or_404(Photo, product_in_time__category=category_.id, is_alpha=True)[0:4]

    # photos_ = Photo.objects.all()[0:4]
    context = {'menu': for_cat_menu, 'path': request.path, 'content': for_content, 'name': name_, 'catalog_id': cat,
               'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
               'query_string': query_string,'photos': photos_, 'p': p, 'sort': Product.by_sort}
    return HttpResponse(template.render(context, request))