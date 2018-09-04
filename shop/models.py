from django.db import models
from django.contrib.auth.models import User
from imagekit.processors import ResizeToFill
from imagekit.models import ImageSpecField
from imagekit.processors.watermark import TextWatermark
import uuid
from sortedm2m.fields import SortedManyToManyField
# from photologue.models import Gallery

import datetime
from django.utils import timezone

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование категории')
    num = models.IntegerField(default=0, verbose_name='Номер п/п')

    class Meta:
        ordering = ['num']

    def __str__(self):
        return '%s, id - %s' % (self.name, self.id)

    def get_absolute_url(self):
        return '/menu/%i/' % self.id


class Watermark(object):

    def __init__(self, font_size=16):
        self.font_size = font_size

    def process(self, image):
        title_mark = TextWatermark("http://myamp.online",
                                   font=("/font/Tahoma Bold.ttf", self.font_size),
                                   text_color='gray',
                                   position=(-20, -20),
                                   opacity=0.7)
        img = title_mark.process(image)
        return img



class Photo(models.Model):
    file = models.ImageField(upload_to='img')
    name = models.CharField(max_length=30)
    is_alpha = models.BooleanField(default=False, verbose_name='Основное')

    thumbnail = ImageSpecField(source='file',
                                    processors=[ResizeToFill(320, 170), Watermark()],
                                    format='JPEG',
                                    options={'quality': 80})

    foto_800x400 = ImageSpecField(source='file',
                               processors=[ResizeToFill(800, 400), Watermark(font_size=300)],
                               format='JPEG',
                               options={'quality': 80})

    foto_original = ImageSpecField([Watermark(font_size=110)],
                                          source='file',
                                          format='JPEG',
                                          options={'quality': 100})

    def __str__(self):
        return '%s, id - %s' % (self.name, self.id)

class Drawing(models.Model):
    file = models.FileField(upload_to='img')
    name = models.CharField(max_length=30)

    def __str__(self):
        return '%s, id - %s' % (self.name, self.id)


class Product_in_time(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    photos = models.ManyToManyField(Photo, verbose_name='Фото')
    description = models.CharField(max_length=400, blank=True, verbose_name='Описание')
    drawings = models.ManyToManyField(Drawing, blank=True, verbose_name='Чертежи')

    def get_image(self):
        img = "img/320x170.png"
        i = self.photos.all()
        for a in i:
            if a.is_alpha:
                img = a.thumbnail
                break
        return img

    def __str__(self):
        return '%s in %s, id - %s' % (self.name, self.category.__str__(), self.id)

class Product(models.Model):
    date_actions = models.DateField(verbose_name='Дата ввода в действие')
    product = models.ForeignKey(Product_in_time, verbose_name='Наименование')
    cost = models.FloatField(default=1.0, verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    quantity_in_reserv = models.IntegerField(default=0, verbose_name='Количество зарезервированных')
    is_preorder = models.BooleanField(default=False, verbose_name='Доступно к заказу')
    is_in_stock = models.BooleanField(default=True, verbose_name='Есть в наличии')
    date_of_delivery = models.DateField(verbose_name='Планируемая дата поставки')
    is_not_arhive = models.BooleanField(default=True, verbose_name='Признак не архивного')
    outlay = models.FloatField(default=1.0, verbose_name='Закупка')

    def get_absolute_url(self):
        return '/menu/%i/%a' % (self.product.category.id, self.id)

    def __str__(self):
        return '%s, id - %i' % (self.product.__str__(), self.id)

    by_sort = (
        ('PRICEUP', 'Дешевле'),
        ('PRICEDOWN', 'Дороже'),
        ('AVIALABLE', 'Наличие'),
    )

    class Meta:
        ordering = ['is_preorder']


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    # lastname = models.CharField(max_length=20, verbose_name='Имя')
    # firstname = models.CharField(max_length=100, verbose_name='Фамилия', null=True)
    middle_name = models.CharField(max_length=100, default='', verbose_name='Отчество', null=True)
    address = models.CharField(max_length=300, verbose_name='Адрес', null=True)
    tel = models.CharField(max_length=15, verbose_name='Контактный телефон', null=True)

    def __str__(self):
        return '%s, id - %i' % (self.user, self.id)

    def full_info(self):
        return '%s %s %s, Адрес: %s, Телефон: %s' % (self.user.last_name, self.user.first_name, self.middle_name,
                                                       self.address, self.tel)


class CartElement(models.Model):
    # owner = models.ForeignKey(Client)
    product = models.ForeignKey(Product, verbose_name='Наименование')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    is_preorder = models.BooleanField(default=False, verbose_name='Предзаказ')
    is_calculate = models.BooleanField(default=False, verbose_name='Был вычет при обработке заказа')

    def __str__(self):
        return '%s from %s, %s, id - %i' % (self.product, self.product.date_actions, self.quantity, self.id)

    def amount(self):
        return round(int(self.quantity)*float(self.product.cost), 2)



class Cart(models.Model):
    owner = models.ForeignKey(Client)
    datetime = models.DateTimeField(auto_now_add=True)
    cartElement = models.ManyToManyField(CartElement)
    key = models.CharField(verbose_name='Ключ сессии', max_length=100, default='', null=True)
    status = models.BooleanField(verbose_name='Корзина/Заказ', default=True)
    summ = models.FloatField(default=0, verbose_name='Сумма')

    def __str__(self):
        return '%s, id - %i' % (self.owner.__str__(), self.id)


class Person(models.Model):
    first_name = models.CharField(max_length=100, default='', verbose_name='Имя')
    last_name = models.CharField(max_length=100, default='', verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, default='', verbose_name='Отчество', null=True)
    address = models.CharField(max_length=300, verbose_name='Адрес', null=True)
    tel = models.CharField(max_length=15, verbose_name='Контактный телефон', null=True)
    email = models.EmailField(max_length=100, verbose_name='E-MAIL')

    def __str__(self):
        return '%s, %s, id - %i' % (self.last_name, self.first_name, self.id)


class Order(models.Model):

    status_in_choices = (
        ('NEW', 'Новый'),
        ('ACC', 'Принят'),
        ('PRE', 'Предоплачен'),
        ('INJOB', 'В работе'),
        ('PAY', 'Оплачен'),
        ('CLOSE', 'Закрыт'),
    )

    dispatch = (
        ('POST', 'Почта'),
        ('TK', 'ТК'),
        ('PER', 'Лично'),

    )

    list = models.ForeignKey(Cart, verbose_name='Корзина для заказа')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    status = models.CharField(max_length=15, choices=status_in_choices, default='NEW', verbose_name='Статус')
    comment = models.CharField(max_length=400, blank=True, verbose_name='Комментарий')
    person = models.ForeignKey(Person, verbose_name='Информация о заказчике', default=1)
    prepay = models.FloatField(default=0, verbose_name='Сумма предоплаты')
    relay_free = models.FloatField(default=0, verbose_name='Сумма оплаты за пересылку')
    total = models.FloatField(default=0, verbose_name='Итоговая сумма')
    type_of_dispatch = models.CharField(max_length=15, choices=dispatch, default='POST', verbose_name='Тип отправления')
    track_number = models.CharField(max_length=20, blank=True, verbose_name='Номер для отслеживания')
    linked_orders = models.CharField(max_length=100, blank=True, verbose_name='Связанные заказы')

    class Meta:
        ordering = ['-datetime']

    def get_absolute_url(self):
        return '/orders/%i/' % self.id

    def __str__(self):
        return '%s, id - %i' % (self.list.__str__(), self.id)


class Key(models.Model):
    login = models.CharField(max_length=150, verbose_name='Логин')
    # email = models.EmailField(max_length=100, verbose_name='E-MAIL')
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isUsed = models.BooleanField(default=False, verbose_name='Ключ использован')
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s, %s, id - %i' % (self.login, self.key, self.id)


class Amplifier(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование')
    photos = models.ManyToManyField(Photo, verbose_name='Фото')
    description = models.CharField(max_length=400, blank=True, verbose_name='Описание')


    def get_image(self):
        img = "img/320x170.png"
        i = self.photos.all()
        for a in i:
            if a.is_alpha:
                img = a.thumbnail
                break
        return img

    def __str__(self):
        return '%s, id - %s' % (self.name, self.id)