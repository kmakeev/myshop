from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import  User
from  shop.models import Category, Photo, Product_in_time, Product, Client, CartElement, Cart, Order, Person, Drawing,\
    Key, Amplifier
from imagekit.admin import AdminThumbnail


# Register your models here.

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'is_alpha', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')


class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Пользователь'

class UserAdmin(BaseUserAdmin):
    inlines = (ClientInline, )

class DrawingAdmin(admin.ModelAdmin):
    list_display = ('name', 'file')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('middle_name', 'address',  'tel')
    search_fields = ('middle_name', 'address', 'tel')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'num',)
    list_filter = ('name', 'num')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'datetime')
    ordering = ('-datetime', )
    # fields = ('owner', 'cartElement', )
    filter_horizontal = ('cartElement',)


class CartElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'is_preorder', 'is_calculate')
    list_filter = ('is_preorder', 'is_calculate',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'cost', 'quantity', 'quantity_in_reserv', 'is_preorder', 'is_in_stock', 'is_not_arhive',
                    'date_of_delivery',)
    list_filter = ('is_in_stock', 'is_preorder', 'is_not_arhive')
    # filter_horizontal = ('product',)
    date_hierarchy = 'date_of_delivery'
    ordering = ('-date_actions',)

    # search_fields = ('cost', )

class Product_in_timeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', )
    filter_horizontal = ('photos',)
    search_fields = ('name', 'description')
    list_filter = ('category',)
    ordering = ('name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'list', 'datetime', 'status', 'prepay', 'relay_free', 'total', 'type_of_dispatch', 'track_number',)

class PersonAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'address', 'tel', 'email')

class KeyAdmin(admin.ModelAdmin):
    list_display = ('login', 'key', 'datetime', 'isUsed')

class AmplifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', )
    filter_horizontal = ('photos',)
    search_fields = ('name', 'description')
    ordering = ('name',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Drawing, DrawingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Product_in_time, Product_in_timeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(CartElement, CartElementAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Amplifier, AmplifierAdmin)