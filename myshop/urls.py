"""myshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import views as views_
from shop.views_ import cart, product, orders, order, login, logout, index, menu, my_register, not_login, about, \
	account, admin_orders, gallery
from shop import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	# url(r'^adm_in/', admin.site.urls),
	url(r'^adm_/admin/', admin.site.urls),
	url(r'^adm_/$', admin_orders.admin_, name='adm_'),
	url(r'^adm_/order/(?P<order>[0-9]+)/$', admin_orders.admin_order, name='adm_order'),
	url(r'^adm_/client/(?P<client>[0-9]+)/$', admin_orders.admin_client, name='adm_client'),
	url(r'^adm_/cart/(?P<cart>[0-9]+)/$', admin_orders.admin_cart, name='adm_cart'),
	url(r'^adm_/menu/(?P<cat>[0-9]+)/$', admin_orders.admin_catalog, name='adm_catalog'),
	url(r'^adm_/element/(?P<element>[0-9]+)/$', admin_orders.admin_element, name='adm_element'),
	url(r'^account/$', account.account, name='account'),
	url(r'^accounts/login/$', login.my_login, name='login'),
	url(r'^accounts/logout/$',logout.my_logout, name='logout'),
	url(r'^accounts/restorePwd/$', account.restorePwd, name='restorePwd'),
	url(r'^accounts/register/$', my_register.my_register, name='register'),
#	url(r'^gallery/$', views.gallery),
#	url(r'^on_registry', OnRegistry.as_view(), name='on_registry'),
	url(r'^$', index.index, name='index'),
	url(r'^gallery/$', gallery.gallery, name='gallery'),
	url(r'^gallery/(?P<amp>[0-9]+)/$', gallery.amplifier, name='amplifer'),
	url(r'^menu/(?P<cat>[0-9]+)/$', menu.menu, name='menu'),
	url(r'^menu/(?P<cat>[0-9]+)/(?P<prod>[0-9]+)$', product.product, name='product'),
#	url(r'^menu/(?P<cat>[0-9]+)/(?P<prod>[0-9]+)/$', product.product, name='product'),
	url(r'^cart/$', cart.cart, name='cart'),
	url(r'^cart/notlogin/$', not_login.not_login, name='notloginform'),
	url(r'^orders/$', orders.orders, name='orders'),
	url(r'^orders/(?P<order>[0-9]+)/$', order.order, name='order'),
	url(r'^about/$',about.about, name='about'),
	# url(r'^static/(?P<path>.*)$', views_.serve),
	#url(r'^photologue/', include('photologue.urls', namespace='photologue'))
	#url(r'^api/', include('rest_framework.urls'), name='rest_framework'),
	#url(r'^accounts/login/$', auth_views.login, {'temlate_name': 'myshop/confirm.html'}),
	# url(r'^accounts/logout/$', logout),
	]
