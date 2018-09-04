from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.template import loader
from shop.models import Client, Product, Category, Cart, CartElement, Order
from shop.views import summ_in_cart
from shop.form.product_form import ProductForm
from shop.form.edit_orders_form import EditOrderForm
from shop.form.edit_carts_form import EditCartForm
from shop.form.datetime_form import DateTimeForm
from django.forms import formset_factory
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from shop.views import summ_in_cart, send_email, get_query
from django.http import QueryDict
from django.db.models import Avg, Sum
import pytz
from datetime import datetime, time
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.dateformat import DateFormat
from  django.core.exceptions import *
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


#@permission_required('shop.can_admin')
def admin_(request):
    permission_req_ = 'shop.change_order'
    # print(request.user.has_perm(permission_req_))

    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        if request.method == 'GET':
            params_ = request.GET
            if not params_:
                p = QueryDict('order=True')
            elif 'order' not in params_:
                p = params_.copy()
                p['order'] = 'True'
            else:
                p = params_.copy()
            #print(p)
            f_order_ = p.get('order')
            f_status_ = p.get('status')
            f_ispreorder = p.get('ispreorder')
            page = p.get('page')
            start_date_ = p.get('start_date')
            end_date_ = p.get('end_date')
            # print(start_date_, end_date_)
            query_string = ''
            init_ = {}
            if start_date_:
                init_['start_date'] = parse_date(start_date_)
            if end_date_:
                init_['end_date'] = parse_date(end_date_)
            form_ = DateTimeForm(initial=init_)
            # print(form_)
            for_cat_menu = Category.objects.all()
            for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
            l = len(for_cart)
            if f_order_ == 'True':
                if f_ispreorder:
                    if f_status_:
                        orders_ = Order.objects.filter(list__cartElement__is_preorder=f_ispreorder, list__status=False,
                                                       status=f_status_).distinct().order_by('-datetime')
                    else:
                        orders_ = Order.objects.filter(list__cartElement__is_preorder=f_ispreorder,
                                                      list__status=False).distinct().order_by('-datetime')
                elif f_ispreorder == 'False':
                    if f_status_:
                        orders_ = Order.objects.filter(list__cartElement__is_preorder=f_ispreorder, list__status=False,
                                                       status=f_status_).distinct().order_by('-datetime')
                    else:
                        orders_ = Order.objects.filter(list__cartElement__is_preorder=f_ispreorder,
                                                       list__status=False).distinct().order_by('-datetime')
                else:
                    if f_status_:
                        orders_ = Order.objects.filter(list__status=False,
                                                       status=f_status_).distinct().order_by('-datetime')
                    else:
                        orders_ = Order.objects.filter(list__status=False).distinct().order_by('-datetime')

                        # start_date_aware = datetime.combine(parse_date(start_date_), time())
                        # end_date_aware = datetime.combine(parse_date(end_date_), time())
                        # tz = pytz.timezone('Europe/Moscow')
                        # print(start_date_aware, end_date_aware)
                        # print(timezone.make_aware(start_date_aware, tz, is_dst=True))
                        # print(timezone.make_aware(end_date_aware, tz, is_dst=True))
                        # print(timezone.is_naive(parse_date(start_date_)))
                        # print(parse_date(start_date_), timezone.make_naive(parse_date(start_date_), timezone='Europe/Moscow'))
                if start_date_:
                    try:
                        start = parse_date(start_date_)
                        orders_ = orders_.filter(datetime__date__gte=start)
                    except:
                        pass
                if end_date_:
                    try:
                        end = parse_date(end_date_)
                        orders_ = orders_.filter(datetime__date__lte=end)
                    except:
                        pass
                if 'q' in p:
                    # print("Search", p.get('q'))
                    query_string = p.get('q')
                    entry_query = get_query(query_string, ['linked_orders', 'track_number', 'comment', 'list__summ',
                                                           'list__owner__tel', 'list__owner__address', 'list__owner__middle_name',
                                                           'list__owner__user__username', 'list__owner__user__first_name',
                                                           'list__owner__user__last_name', 'list__owner__user__email',
                                                           'list__cartElement__product__product__name',
                                                           'list__cartElement__product__product__description',
                                                           'person__first_name', 'person__last_name', 'person__middle_name',
                                                           'person__address', 'person__tel', 'person__email'])
                    orders_ = orders_.filter(entry_query)
                paginator = Paginator(orders_, 20)               # Количество отображаемых записей на странице
                try:
                    orders_on_page = paginator.page(page)
                except PageNotAnInteger:
                    orders_on_page = paginator.page(1)
                except EmptyPage:
                    orders_on_page = paginator.page(paginator.num_pages)
                summ_ = 0
                for i in orders_:
                    summ_ += i.list.summ
                template = loader.get_template('bshop/admin_orders.html')
                context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                           'session': request.session, 'orders': orders_,
                           'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart), 'orders': orders_on_page, 'p': p,
                           'status': Order.status_in_choices, 'summ': summ_, 'form' : form_, 'count': paginator.count,
                           'query_string': query_string,}
            else:
                if f_ispreorder =='True' or f_ispreorder =='False':
                    carts_ = Cart.objects.filter(cartElement__is_preorder=f_ispreorder, status=True).distinct().order_by('-datetime')
                else:
                    carts_ = Cart.objects.filter(status=True).order_by('-datetime')
                if start_date_:
                    try:
                        start = parse_date(start_date_)
                        carts_ = carts_.filter(datetime__date__gte=start)
                    except:
                        pass
                if end_date_:
                    try:
                        end = parse_date(end_date_)
                        carts_ = carts_.filter(datetime__date__lte=end)
                    except:
                        pass
                if 'q' in p:
                    # print("Search", p.get('q'))
                    query_string = p.get('q')
                    entry_query = get_query(query_string, ['summ', 'owner__tel', 'owner__address', 'owner__middle_name',
                                                           'owner__user__username', 'owner__user__first_name',
                                                           'owner__user__last_name', 'owner__user__email',
                                                           'cartElement__product__product__name',
                                                           'cartElement__product__product__description',])
                    carts_ = carts_.filter(entry_query)

                paginator = Paginator(carts_, 20)  # Количество отображаемых записей на странице

                try:
                    carts_on_page = paginator.page(page)
                except PageNotAnInteger:
                    carts_on_page = paginator.page(1)
                except EmptyPage:
                    carts_on_page = paginator.page(paginator.num_pages)
                template = loader.get_template('bshop/admin_carts.html')
                context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                           'session': request.session, 'carts': carts_on_page, 'p': p,
                           'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                           'status': Order.status_in_choices, 'form': form_, 'count': paginator.count,
                           'query_string': query_string, }
            return HttpResponse(template.render(context, request))
        #elif request.method == 'POST':
        #    form_ = DateTimeForm(request.POST)
        #    print(form_)
        #    if form_.is_valid():
        #        start_date = form_.cleaned_data['start_date']
        #        end_date = form_.cleaned_data['end_date']
        #        print(request.path + '?start_date=' + DateFormat(start_date).format('d/m/Y'))
        #        HttpResponseRedirect(reverse('adm_', kwargs={'startdate': DateFormat(start_date).format('d/m/Y')}))
        #    return HttpResponseRedirect(request.path)
        else:
            return HttpResponseRedirect(reverse_lazy('adm_'))

def admin_order(request, order="0"):
    permission_req_ = 'shop.change_order'
    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        for_cat_menu = Category.objects.all()
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        l = len(for_cart)
        order_ = get_object_or_404(Order, id=order)
        for_order = CartElement.objects.filter(cart__id=order_.list.id)
        client_ = order_.list.owner
        pre_quantity_list = []
        for item in for_order:
            if item.is_preorder:
                sum_ = CartElement.objects.filter(product__id=item.product.id, is_preorder=True, is_calculate=False,
                                                  cart__status='False').exclude(cart__order__status='CLOSE').aggregate(Sum('quantity'))
                pre_quantity_list.append((item, sum_['quantity__sum']))
            else:
                pre_quantity_list.append((item, 0))
        if request.method == 'GET':
            data = {'status': order_.status, 'prepay': order_.prepay, 'relay_free': order_.relay_free,
                    'total': order_.total, 'type_of_dispatch': order_.type_of_dispatch, 'track_number': order_.track_number, 'linked_orders': order_.linked_orders}
            form_ = EditOrderForm(data)
            template = loader.get_template('bshop/admin_order.html')
            context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                       'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                       'order': order_, 'positions': for_order, 'client': client_, 'form': form_, 'pre_quantity': pre_quantity_list}

            return HttpResponse(template.render(context, request))
        elif request.method == 'POST':
            form_ = EditOrderForm(request.POST)
            if form_.is_valid():
                change_status = 'False'
                if order_.status != form_.cleaned_data['status']:
                    change_status = True
                order_.status = form_.cleaned_data['status']
                order_.prepay = form_.cleaned_data['prepay']
                order_.relay_free = form_.cleaned_data['relay_free']
                order_.total = form_.cleaned_data['total']
                order_.type_of_dispatch = form_.cleaned_data['type_of_dispatch']
                order_.track_number = form_.cleaned_data['track_number']
                order_.linked_orders = form_.cleaned_data['linked_orders']
                order_.save()
                if order_.status in ('PRE', 'INJOB', 'PAY', 'CLOSE'):
                    for i in for_order:
                        if i.is_preorder == False and i.is_calculate == False:
                            if i.product.quantity > i.quantity:
                                i.product.quantity = int(i.product.quantity) - int(i.quantity)
                                i.product.quantity_in_reserv = int(i.product.quantity_in_reserv) - int(i.quantity)
                                # print('calculate to ', i.product.quantity, i.product.quantity_in_reserv)
                                i.is_calculate = True
                                i.product.save()
                                i.save()
                if order_.status in ('CLOSE',):
                    for i in for_order:
                        if i.is_preorder == True and i.is_calculate == False:
                            i.is_calculate = True
                            i.save()
                if change_status == True:
                    if client_.user.username != 'None':
                        to = [client_.user.email]
                        first_name_ = client_.user.first_name
                    else:
                        to = [order_.person.email]
                        first_name_ = order_.person.first_name
                    from_email = settings.DEFAULT_FROM_EMAIL
                    subject_ = 'Изменение статуса заказа ' + str(order_.id)
                    text_content = render_to_string('bshop/email/changeorder.txt',
                                                        {'first_name': first_name_,
                                                         'summ_in_cart': order_.list.summ,
                                                         'order': order_,
                                                         'positions': for_order})
                    html_content = render_to_string('bshop/email/changeorder.html',
                                                   {'first_name': first_name_,
                                                    'summ_in_cart': order_.list.summ,
                                                    'order': order_,
                                                    'positions': for_order})
                    send_email(to, from_email, subject_, text_content, html_content)

                return HttpResponseRedirect(reverse_lazy('adm_'))

            return HttpResponseRedirect(reverse_lazy('adm_order', args=[order_.id]))
        else:
            return HttpResponseRedirect(reverse_lazy('adm_order', args=[order_.id]))

def admin_cart(request, cart="0"):
    permission_req_ = 'shop.change_order'
    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        for_cat_menu = Category.objects.all()
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        l = len(for_cart)
        cart_ = get_object_or_404(Cart, id=cart)
        carts_ = CartElement.objects.filter(cart__id=cart_.id)
        client_ = cart_.owner
        pre_quantity_list = []

        for item in carts_:
            if item.is_preorder:
                sum_ = CartElement.objects.filter(product__id=item.product.id, is_preorder=True,
                                                  cart__status='False').exclude(cart__order__status='CLOSE').aggregate(Sum('quantity'))
                # print(sum_)
                pre_quantity_list.append((item, sum_['quantity__sum']))
            else:
                pre_quantity_list.append((item, 0))
        if request.method == 'GET':
            data = {'status': cart_.status}
            form_ = EditCartForm(data)
            template = loader.get_template('bshop/admin_cart.html')
            context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                       'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                       'cart': cart_, 'positions': carts_, 'client': client_, 'form': form_, 'pre_quantity': pre_quantity_list}

            return HttpResponse(template.render(context, request))

        elif request.method == 'POST':
            for i in carts_:
                if i.is_preorder == False:
                    if (int(i.product.quantity_in_reserv) - int(i.quantity)) >= 0:
                        i.product.quantity_in_reserv = int(i.product.quantity_in_reserv) - int(i.quantity)
                        i.product.save()
                # try:
                #     i.delete()          #Удаление элемента корзины
                # except:
                #    pass
            try:
                cart_.delete()          #Удаление самой корзины пользователя
            except:
                pass
            return HttpResponseRedirect('/adm_/?order=False')
        else:
            return HttpResponseRedirect(reverse_lazy('adm_cart', args=[cart_.id]))


def admin_catalog(request, cat="0"):
    permission_req_ = 'shop.change_order'
    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        for_cat_menu = Category.objects.all()
        name_ = ''
        for i in for_cat_menu:
            # str = i.get_absolute_url()
            if int(cat) == int(i.id):
                name_ = i.name
                product_ = Product.objects.filter(product__category=i.id)
        if not name_:
            return HttpResponseRedirect(reverse_lazy('adm_'))

        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        l = len(for_cart)
        params_ = request.GET
        if not params_:
            p = QueryDict()
        else:
            p = params_.copy()
        start_date_ = p.get('start_date')
        end_date_ = p.get('end_date')
        # print(start_date_, end_date_)
        init_ = {}
        if start_date_:
            init_['start_date'] = parse_date(start_date_)
        if end_date_:
            init_['end_date'] = parse_date(end_date_)
        form_ = DateTimeForm(initial=init_)

        orders_products_ = []
        amount = 0
        for item in product_:
            orders_ = []
            cartElements_ = CartElement.objects.filter(product__id=item.id)
            if start_date_:
                try:
                    start = parse_date(start_date_)
                    cartElements_ = cartElements_.filter(cart__datetime__date__gte=start)
                except:
                    pass
            if end_date_:
                try:
                    end = parse_date(end_date_)
                    cartElements_ = cartElements_.filter(datetime__date__lte=end)
                except:
                    pass
            if cartElements_:
                for el in cartElements_:
                    # Получить список корзин с данным товаром
                    cart_ = Cart.objects.filter(cartElement=el.id).distinct().order_by('-datetime')
                    if cart_:
                        # print(cart_[0], cart_[0].status)
                        if cart_[0].status:                 # Если корзина
                            # print ('is cart')
                            orders_.append((cart_[0], el))
                        else:                               # Если заказ
                            # print('is order')
                            order_ = Order.objects.filter(list__cartElement=el.id).distinct().order_by('-datetime')
                            if order_:                      # Если заказ не потерт
                                orders_.append((order_[0], el))
                            else:                           # Если заказ стерт потерта
                                orders_.append((order_, el))
                    else:                                   # Если корзина потерта
                        orders_.append((cart_, el))
                total_quantity = cartElements_.aggregate(Sum('quantity'))['quantity__sum']
                total_sum = total_quantity * item.cost
                amount += total_sum
                total_proceeds = total_quantity * (item.cost - item.outlay)
                # print('Add - ', item, orders_, cartElements_.aggregate(Sum('quantity'))['quantity__sum'])
                orders_products_.append((item, orders_, total_quantity, total_sum, total_proceeds))

        template = loader.get_template('bshop/admin_catalog_list.html')
        context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                    'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                   'catalog_name': name_, 'orders_products': orders_products_, 'form': form_, 'amount': amount}

        return HttpResponse(template.render(context, request))


def admin_element(request, element="0"):
    permission_req_ = 'shop.change_order'
    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        for_cat_menu = Category.objects.all()
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        l = len(for_cart)

        element_ = get_object_or_404(CartElement, id=element)
        if request.method == 'GET':
            template = loader.get_template('bshop/admin_element.html')
            context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                       'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                        'element': element_}

            return HttpResponse(template.render(context, request))

        elif request.method == 'POST':
            # print('in POST', element_, element_.id)
            element_.delete()          #Удаление элемента корзины
            return HttpResponseRedirect('/adm_/?order=False')
        else:
            return HttpResponseRedirect(reverse_lazy('adm_element', args=[element_.id]))


def admin_client(request, client="0"):
    permission_req_ = 'shop.change_order'
    if not request.user.has_perm(permission_req_):
        raise Http404()
    else:
        for_cat_menu = Category.objects.all()
        for_cart = CartElement.objects.filter(cart__owner__user__username=request.user.username, cart__status=True)
        l = len(for_cart)
        clients_ = Client.objects.all()
        client_ = get_object_or_404(Client, id=client)
        orders_client = Order.objects.filter(list__owner__id=client_.id)
        if request.method == 'GET':
            p = request.GET
            page = p.get('page')
            paginator = Paginator(clients_, 20)
            try:
                clients_on_page = paginator.page(page)
            except PageNotAnInteger:
                clients_on_page = paginator.page(1)
            except EmptyPage:
                clients_on_page = paginator.page(paginator.num_pages)
            summ_ = 0
            for i in orders_client:
                summ_ += i.list.summ
            template = loader.get_template('bshop/admin_client.html')
            context = {'menu': for_cat_menu, 'request': request, 'path': request.path, 'user': request.user,
                       'session': request.session, 'cart_length': l, 'summ_in_cart': summ_in_cart(for_cart),
                       'orders': orders_client, 'client': client_, 'summ': summ_, 'clients': clients_on_page}

            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect(reverse_lazy('adm_client', args=[client_.id]))

