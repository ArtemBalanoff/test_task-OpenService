from django.db import models
from product_storage.constants import (PRODUCT_NAME_MAX_LENGTH,
                                       PRODUCT_TYPE_NAME_MAX_LENGTH,
                                       BARCODE_LENGTH_1,
                                       BARCODE_LENGTH_2,
                                       PRICE_DECIMAL_PLACES,
                                       PRICE_MAX_DIGITS,
                                       LONG_NAME_LENGTH_LIMIT as LEN_LIM)
from product_storage.products.validators import barcode_regex_validator


class Product(models.Model):
    name = models.CharField('Название',
                            max_length=PRODUCT_NAME_MAX_LENGTH)
    amount = models.PositiveSmallIntegerField('Количество')
    barcode = models.CharField('Штрихкод', max_length=max(BARCODE_LENGTH_1,
                                                          BARCODE_LENGTH_2),
                               validators=(barcode_regex_validator,),
                               db_index=True)
    date_updated = models.DateTimeField('Дата обновления', auto_now=True)
    type = models.ForeignKey('ProductType', on_delete=models.PROTECT,
                             verbose_name='Тип товара')

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'
        ordering = ('-date_updated',)

    def __str__(self):
        name = self.name
        return name[:LEN_LIM] + '...' if len(name) > LEN_LIM else name


class ProductType(models.Model):
    name = models.CharField('Название',
                            max_length=PRODUCT_TYPE_NAME_MAX_LENGTH)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'тип товара'
        verbose_name_plural = 'Типы товаров'
        ordering = ('name',)

    def __str__(self):
        name = self.name
        return name[:LEN_LIM] + '...' if len(name) > LEN_LIM else name


class ProductPrice(models.Model):
    class Currencies(models.TextChoices):
        RUB = 'rub', 'Рубль'
        DOLLAR = 'dollar', 'Доллар'
        EURO = 'euro', 'Евро'
        YUAN = 'yuan', 'Юань'

    currency = models.CharField(
        'Валюта',
        max_length=max(map(len, Currencies.values)),
        choices=Currencies.choices,
        default=Currencies.RUB)
    price = models.DecimalField('Цена',
                                max_digits=PRICE_MAX_DIGITS,
                                decimal_places=PRICE_DECIMAL_PLACES)
    product = models.OneToOneField(Product, on_delete=models.CASCADE,
                                   related_name='price', verbose_name='Товар')

    class Meta:
        verbose_name = 'стоимость'
        verbose_name_plural = 'Стоимости'
        ordering = ('price',)

    def __str__(self):
        return f'{self.price} {self.get_currency_display()}'
