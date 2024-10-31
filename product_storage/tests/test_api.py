from decimal import Decimal
from http import HTTPStatus
import pytest
from products.models import Product, ProductType


def test_create_product(api_client_with_jwt, product_create_data,
                        product_list_url):
    '''Тест проверяет возможность создания товара'''

    Product.objects.all().delete()
    data = product_create_data

    # Проверяем, создается ли продукт
    response = api_client_with_jwt.post(product_list_url, data, format='json')
    assert response.status_code == HTTPStatus.CREATED, (
        f'Response: {response.data}')
    assert Product.objects.count() == 1

    # Проверяем соответствие полей
    product = Product.objects.get()
    assert product.name == data.get('name')
    assert product.amount == data.get('amount')
    assert product.barcode == data.get('barcode')
    assert product.type.id == data.get('type')


def test_bulk_create_product(api_client_with_jwt, product_bulk_create_data,
                             product_bulk_create):
    '''Тест проверяет множественное добавление товаров'''

    Product.objects.all().delete()
    data = product_bulk_create_data
    response = api_client_with_jwt.post(product_bulk_create,
                                        data, format='json')
    assert response.status_code == HTTPStatus.CREATED, (
        f'Response: {response.data}')
    assert Product.objects.count() == len(data.get('products'))
    products_from_db = Product.objects.order_by('name')
    for product_from_db, given_value in zip(products_from_db,
                                            data.get('products')):
        assert product_from_db.name == given_value.get('name')
        assert product_from_db.amount == given_value.get('amount')
        assert product_from_db.price.price == Decimal(
            given_value.get('price').get('price'))
        assert product_from_db.price.currency == (
            given_value.get('price').get('currency'))


def test_patch_product(api_client_with_jwt, product_patch_data,
                       product_detail_url, product):
    '''Тест проверяет возможность изменения товара'''

    data = product_patch_data

    # Проверяем соответствие полей
    response = api_client_with_jwt.patch(product_detail_url, data,
                                         format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    product.refresh_from_db()
    assert product.name == data.get('name')
    assert product.barcode == data.get('barcode')
    assert product.type.id == data.get('type')
    assert product.price.price == Decimal(data.get('price').get('price'))
    assert product.price.currency == data.get('price').get('currency')
    assert product.is_active is data.get('is_active')


def test_create_product_incorrect_barcode(api_client_with_jwt,
                                          product_create_data,
                                          product_list_url):
    '''Тест ожидает ошибку при вводе некорректного штрихкода'''

    Product.objects.all().delete()
    data = product_create_data
    data['barcode'] = '123456789'  # invalid barcode

    # Проверяем, что товар не был создан
    response = api_client_with_jwt.post(product_list_url, data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Response: {response.data}')
    assert Product.objects.count() == 0


def test_update_product_amount(api_client_with_jwt, product,
                               update_amount_url):
    '''Тест проверяет возможность относительного изменения кол-ва товара'''

    start_amount = product.amount

    # Проверяем, что кол-во изменилось
    response = api_client_with_jwt.patch(update_amount_url,
                                         {'amount_delta': 50}, format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    product.refresh_from_db()
    assert product.amount == start_amount + 50


def test_update_product_amount_incorrect_value(api_client_with_jwt, product,
                                               update_amount_url):
    '''Тест ожидает ошибку при попытке вычесть
    большее кол-во, чем есть у товара'''

    start_amount = product.amount

    # Проверяем, что кол-во не изменилось
    response = api_client_with_jwt.patch(update_amount_url,
                                         {'amount_delta': -100}, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Response: {response.data}')
    product.refresh_from_db()
    assert product.amount == start_amount


def test_create_product_type(api_client_with_jwt, product_type_list_url,
                             product_type_data):
    '''Тест проверяет возможность создания типа товара'''

    ProductType.objects.all().delete()
    data = product_type_data

    # Проверяем, что тип создался
    response = api_client_with_jwt.post(product_type_list_url, data,
                                        format='json')
    assert response.status_code == HTTPStatus.CREATED, (
        f'Response: {response.data}')
    assert ProductType.objects.count() == 1

    # Проверяем соответствие полей
    product_type = ProductType.objects.get()
    assert product_type.name == data.get('name')
    assert product_type.description == data.get('description')


def test_update_product_type(api_client_with_jwt, product_type_detail_url,
                             product_type, product_type_patch_data):
    '''Тест проверяет возможность изменения типа товара'''

    data = product_type_patch_data
    response = api_client_with_jwt.patch(product_type_detail_url,
                                         data)
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    product_type.refresh_from_db()
    assert product_type.name == data.get('name')
    assert product_type.description == (
        data.get('description'))


def test_product_filters(api_client_with_jwt, product_list, product_list_url):
    '''Тест проверяет опциональную фильтрацию товаров'''

    # Проверяем поиск по статусу
    response = api_client_with_jwt.get(product_list_url,
                                       {'is_active': True}, format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    assert {el.get('id') for el in response.data.get('results')} == set(
        Product.objects.values_list('id', flat=True).filter(is_active=True))

    # Проверяем поиск по названию
    response = api_client_with_jwt.get(product_list_url,
                                       {'name': 'Top'}, format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == Product.objects.get(
        name='laptop').id

    # Проверяем поиск по границам цены
    response = api_client_with_jwt.get(product_list_url,
                                       {'min_price': 85, 'max_price': 95},
                                       format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == (
        Product.objects.filter(price__price__gte=85,
                               price__price__lte=95)[0].id)

    # Проверяем поиск по валюте цены
    response = api_client_with_jwt.get(product_list_url,
                                       {'currency': 'rub'}, format='json')
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    assert all(el.get('price').get('currency') == 'rub'
               for el in response.data.get('results'))


@pytest.mark.parametrize('ordering_field', ('name', '-name',
                                            'price', '-price',
                                            'date_updated', '-date_updated'))
def test_product_ordering(api_client_with_jwt, product_list,
                          ordering_field, product_list_url):
    '''Тест проверяет опциональную сортировку товаров'''

    response = api_client_with_jwt.get(product_list_url,
                                       {'ordering': ordering_field})
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    assert [el.get('id') for el in response.data.get('results')] == list(
        Product.objects.order_by(ordering_field).values_list('id', flat=True))
