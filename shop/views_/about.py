from django.contrib.auth import authenticate, login
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from shop.form.login_form import LoginForm
from django.core.urlresolvers import reverse_lazy
from shop.models import Category, CartElement
import datetime
from shop.views import summ_in_cart, add_to_cart


def about(request):

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
    l = len(for_cart)
    template = loader.get_template('bshop/about.html')
    context = {'menu': for_cat_menu, 'path': request.path, 'user': request.user, 'session': request.session,
               'cart_length':l, 'summ_in_cart': summ_in_cart(for_cart)}
    return HttpResponse(template.render(context, request))