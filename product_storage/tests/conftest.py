from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Product, ProductPrice, ProductType

User = get_user_model()


# ---------- INSTANCES ----------


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_type():
    return ProductType.objects.create(
        name='Электроника', description='Телефоны, планшеты')


@pytest.fixture
def product_type_2():
    return ProductType.objects.create(
        name='Мебель', description='Изысканная мебель на любой вкус')


@pytest.fixture
def product(product_type):
    product = Product.objects.create(name='NokiaPhone',
                                     amount=50,
                                     barcode='12345678',
                                     type=product_type)
    ProductPrice.objects.create(price=500, currency='rub', product=product)
    return product


@pytest.fixture()
def test_user_data():
    return {'username': 'test_user', 'password': 'test_pass'}


@pytest.fixture()
def user(test_user_data):
    return User.objects.create_user(**test_user_data)


@pytest.fixture()
def api_client_with_jwt(user, test_user_data):
    client = APIClient()
    url = reverse('jwt-create')
    response = client.post(url, test_user_data, format='json')
    if response.status_code != HTTPStatus.OK:
        pytest.fail('Не удалось получить JWT токен. Статус-код: '
                    + str(response.status_code))
    token = response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def product_list(product_type):
    product_list = [Product(
        name=['car', 'laptop', 'banana'][idx],
        type=product_type,
        amount=100 - idx,
        barcode=f'1234567{idx}',
        is_active=bool(idx)
    ) for idx in range(3)]
    Product.objects.bulk_create(product_list)
    products = Product.objects.all()
    ProductPrice.objects.bulk_create(ProductPrice(
        price=100 - idx * 10,
        currency=['rub', 'dollar', 'euro'][idx],
        product=product) for idx, product in enumerate(products))
    return products


# ---------- DATA ----------


@pytest.fixture
def product_create_data(product_type):
    return {'name': 'Nokia Phone',
            'amount': 100,
            'barcode': '12345678',
            'type': product_type.id,
            'price': {'price': 100.00, 'currency': 'rub'}}


@pytest.fixture
def product_patch_data(product_type_2):
    return {'name': 'Шкаф',
            'is_active': False,
            'barcode': '1234567890123',
            'type': product_type_2.id,
            'price': {'price': 200.00, 'currency': 'dollar'}}


@pytest.fixture
def product_bulk_create_data(product_type):
    return {'products': [{'name': str(idx), 'amount': idx,
                          'barcode': str(12345678 + idx),
                          'price': {'price': 100, 'currency': 'rub'},
                          'type': product_type.id
                          }for idx in range(3)]}


@pytest.fixture
def product_type_data():
    return {'name': 'Овощи',
            'description': 'Хранится в отделе с высокой влажностью'}


@pytest.fixture
def product_type_patch_data():
    return {'name': 'Запчасти', 'description': 'Очень ценный груз'}


# ---------- URLS ----------


@pytest.fixture
def product_list_url():
    return reverse('product-list')


@pytest.fixture
def product_detail_url(product):
    return reverse('product-detail', args=(product.id,))


@pytest.fixture
def product_bulk_create():
    return reverse('product-bulk-create')


@pytest.fixture
def update_amount_url(product):
    return reverse('product-update-amount', args=(product.id,))


@pytest.fixture
def product_type_list_url():
    return reverse('product_type-list')


@pytest.fixture
def product_type_detail_url(product_type):
    return reverse('product_type-detail', args=(product_type.id,))
