from http import HTTPStatus

import pytest

from products.models import Product


@pytest.mark.parametrize('invalid_barcode', ('abc', '1' * 7, '1' * 12))
def test_create_product_incorrect_barcode(api_client_with_jwt,
                                          product_create_data,
                                          product_list_url,
                                          invalid_barcode):
    '''Тест ожидает ошибку при вводе некорректного штрихкода'''

    Product.objects.all().delete()
    data = product_create_data
    data['barcode'] = invalid_barcode

    # Проверяем, что товар не был создан
    response = api_client_with_jwt.post(product_list_url, data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        f'Response: {response.data}')
    assert Product.objects.count() == 0


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
