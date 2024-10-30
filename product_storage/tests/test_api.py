from copy import copy
from http import HTTPStatus
from django.urls import reverse
import pytest
from products.models import Product, ProductType


PRODUCT_DATA = {'name': 'Nokia Phone',
                'amount': 100,
                'barcode': '12345678',
                'type': None,
                'price': {'price': 100, 'currency': 'rub'}}


def test_create_product(api_client_with_jwt, product_type):
    Product.objects.all().delete()
    url = reverse('product-list')
    data = copy(PRODUCT_DATA)
    data['type'] = product_type.id
    response = api_client_with_jwt.post(url, data, format='json')
    assert response.status_code == HTTPStatus.CREATED
    assert Product.objects.count() == 1
    product = Product.objects.get()
    assert product.name == data.get('name')
    assert product.amount == data.get('amount')
    assert product.barcode == data.get('barcode')
    assert product.type.id == data.get('type')


def test_create_product_incorrect_barcode(api_client_with_jwt, product_type):
    Product.objects.all().delete()
    data = copy(PRODUCT_DATA)
    data['type'] = product_type.id
    data['barcode'] = '123456789'
    url = reverse('product-list')
    response = api_client_with_jwt.post(url, data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert Product.objects.count() == 0


def test_update_product_amount(api_client_with_jwt, product):
    start_amount = product.amount
    url = reverse('product-detail', args=(product.id,)) + 'update_amount/'
    response = api_client_with_jwt.patch(url, {'amount_delta': 50},
                                         format='json')
    assert response.status_code == HTTPStatus.OK
    product.refresh_from_db()
    assert product.amount == start_amount + 50


def test_update_product_amount_incorrect_value(api_client_with_jwt, product):
    start_amount = product.amount
    url = reverse('product-detail', args=(product.id,)) + 'update_amount/'
    response = api_client_with_jwt.patch(url, {'amount_delta': -100},
                                         format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    product.refresh_from_db()
    assert product.amount == start_amount


def test_create_product_type(api_client_with_jwt):
    ProductType.objects.all().delete()
    data = {'name': 'Овощи',
            'description': 'Хранится в отделе с высокой влажностью'}
    url = reverse('product_type-list')
    response = api_client_with_jwt.post(url, data, format='json')
    assert response.status_code == HTTPStatus.CREATED
    assert ProductType.objects.count() == 1
    product_type = ProductType.objects.get()
    assert product_type.name == data.get('name')
    assert product_type.description == data.get('description')


def test_product_filters(api_client_with_jwt, product_list):
    url = reverse('product-list')
    response = api_client_with_jwt.get(url, {'is_active': True}, format='json')
    assert response.status_code == HTTPStatus.OK
    assert {el.get('id') for el in response.data.get('results')} == set(
        Product.objects.values_list('id', flat=True).filter(is_active=True))
    response = api_client_with_jwt.get(url, {'name': 'Top'}, format='json')
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == Product.objects.get(
        name='laptop').id
    response = api_client_with_jwt.get(url, {'min_price': 85,
                                             'max_price': 95}, format='json')
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('count') == 1
    assert response.data.get('results')[0].get('id') == Product.objects.filter(
        price__price__gte=85, price__price__lte=95)[0].id


@pytest.mark.parametrize('ordering_field', ('name', '-name',
                                            'price', '-price',
                                            'date_updated', '-date_updated'))
def test_product_ordering(api_client_with_jwt, product_list, ordering_field):
    url = reverse('product-list')
    response = api_client_with_jwt.get(url, {'ordering': ordering_field})
    assert response.status_code == HTTPStatus.OK
    assert [el.get('id') for el in response.data.get('results')] == list(
        Product.objects.order_by(ordering_field).values_list('id', flat=True))
