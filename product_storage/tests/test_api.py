from copy import copy
from http import HTTPStatus
import pytest
from products.models import Product, ProductType


PRODUCT_DATA = {'name': 'Nokia Phone',
                'amount': 100,
                'barcode': '12345678',
                'type': None,
                'price': {'price': '100.00', 'currency': 'rub'}}
PRODUCT_TYPE_DATA = {'name': 'Овощи',
                     'description': 'Хранится в отделе с высокой влажностью'}


def test_create_product(api_client_with_jwt, product_type, product_list_url):
    Product.objects.all().delete()
    data = copy(PRODUCT_DATA)
    data['type'] = product_type.id

    response = api_client_with_jwt.post(product_list_url, data, format='json')
    assert response.status_code == HTTPStatus.CREATED
    assert Product.objects.count() == 1

    product = Product.objects.get()
    assert product.name == data.get('name')
    assert product.amount == data.get('amount')
    assert product.barcode == data.get('barcode')
    assert product.type.id == data.get('type')


def test_patch_product(api_client_with_jwt, product, product_type_2,
                       product_detail_url):
    new_data = {'name': 'Шкаф',
                'barcode': '1234567890123',
                'type': product_type_2.id,
                'price': {'price': '200.00', 'currency': 'dollar'},
                'is_active': False}

    response = api_client_with_jwt.patch(product_detail_url,
                                         new_data, format='json')
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('name') == new_data.get('name')
    assert response.data.get('barcode') == new_data.get('barcode')
    assert response.data.get('type') == new_data.get('type')
    assert response.data.get('price').get('price') == new_data.get('price').get('price')
    assert response.data.get('price').get('currency') == new_data.get('price').get('currency')
    assert response.data.get('is_active') == new_data.get('is_active')


def test_create_product_incorrect_barcode(api_client_with_jwt, product_type,
                                          product_list_url):
    Product.objects.all().delete()
    data = copy(PRODUCT_DATA)
    data['type'] = product_type.id
    data['barcode'] = '123456789'

    response = api_client_with_jwt.post(product_list_url, data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert Product.objects.count() == 0


def test_update_product_amount(api_client_with_jwt, product,
                               product_detail_url):
    start_amount = product.amount
    product_detail_url += 'update_amount/'

    response = api_client_with_jwt.patch(product_detail_url,
                                         {'amount_delta': 50},
                                         format='json')
    assert response.status_code == HTTPStatus.OK
    product.refresh_from_db()
    assert product.amount == start_amount + 50


def test_update_product_amount_incorrect_value(api_client_with_jwt, product,
                                               product_detail_url):
    start_amount = product.amount
    product_detail_url += 'update_amount/'

    response = api_client_with_jwt.patch(product_detail_url,
                                         {'amount_delta': -100},
                                         format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    product.refresh_from_db()
    assert product.amount == start_amount


def test_create_product_type(api_client_with_jwt, product_type_list_url):
    ProductType.objects.all().delete()

    response = api_client_with_jwt.post(product_type_list_url,
                                        PRODUCT_TYPE_DATA, format='json')
    assert response.status_code == HTTPStatus.CREATED
    assert ProductType.objects.count() == 1

    product_type = ProductType.objects.get()
    assert product_type.name == PRODUCT_TYPE_DATA.get('name')
    assert product_type.description == PRODUCT_TYPE_DATA.get('description')


def test_product_filters(api_client_with_jwt, product_list, product_list_url):
    response = api_client_with_jwt.get(product_list_url,
                                       {'is_active': True}, format='json')
    assert response.status_code == HTTPStatus.OK
    assert {el.get('id') for el in response.data.get('results')} == set(
        Product.objects.values_list('id', flat=True).filter(is_active=True))

    response = api_client_with_jwt.get(product_list_url,
                                       {'name': 'Top'}, format='json')
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == Product.objects.get(
        name='laptop').id

    response = api_client_with_jwt.get(product_list_url,
                                       {'min_price': 85, 'max_price': 95},
                                       format='json')
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == Product.objects.filter(
        price__price__gte=85, price__price__lte=95)[0].id


@pytest.mark.parametrize('ordering_field', ('name', '-name',
                                            'price', '-price',
                                            'date_updated', '-date_updated'))
def test_product_ordering(api_client_with_jwt, product_list, ordering_field,
                          product_list_url):
    response = api_client_with_jwt.get(product_list_url,
                                       {'ordering': ordering_field})
    assert response.status_code == HTTPStatus.OK
    assert [el.get('id') for el in response.data.get('results')] == list(
        Product.objects.order_by(ordering_field).values_list('id', flat=True))
