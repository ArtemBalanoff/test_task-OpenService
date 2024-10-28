from django.db import models
from django.core.validators import RegexValidator
from product_storage.constants import (PRODUCT_NAME_MAX_LENGTH,
                                       PRODUCT_TYPE_NAME_MAX_LENGTH,
                                       BARCODE_MAX_LENGTH,
                                       PRICE_DECIMAL_PLACES,
                                       PRICE_MAX_DIGITS)


class Product(models.Model):
    name = models.CharField('Название',
                            max_length=PRODUCT_NAME_MAX_LENGTH)
    price = models.OneToOneField('Price', on_delete=models.CASCADE,
                                 verbose_name='Цена')
    amount = models.PositiveSmallIntegerField('Количество')
    barcode = models.CharField(
        'Штрихкод', max_length=BARCODE_MAX_LENGTH,
        validators=RegexValidator(
            regex=r'^\d{8}|\d{13}$', message='Штрихкод должен иметь длину'
            '8 или 13 символов и состоять из цифр'),
        db_index=True)
    date_updated = models.DateTimeField('Дата обновления', auto_now=True)
    type = models.ForeignKey('ProductType', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'
        ordering = ('date_updated',)

    def __str__(self):
        return self.name.split()[:5]


class ProductType(models.Model):
    name = models.CharField('Название',
                            max_length=PRODUCT_TYPE_NAME_MAX_LENGTH)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'тип товара'
        verbose_name_plural = 'Типы товаров'
        ordering = ('name',)

    def __str__(self):
        return self.name.split()[:5]


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

    class Meta:
        verbose_name = 'стоимость'
        verbose_name_plural = 'Стоимости'
        ordering = ('price',)

    def __str__(self):
        return f'{self.price} {self.get_currency_display()}'
