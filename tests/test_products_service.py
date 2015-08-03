from helpers import *
from server.app import Product, PopularProductsService

def test_can_find_most_popular_products():
    products = [gen_products(shop_id, 10) for shop_id in range(10)]
    sut = PopularProductsService(flatten(products))
    
    expected = most_popular(products[2] + products[3] + products[5], 10)
    actual = sut.find_popular_products([2,3,5], 10)
    
    assert expected == actual


def test_products_are_bound_by_count():
    products = [gen_products(shop_id, 10) for shop_id in range(10)]
    sut = PopularProductsService(flatten(products))
    result = sut.find_popular_products(range(10), 7)
    assert 7 == len(result)


def test_can_handle_products_with_equal_popularity():
    products = gen_products(0, 2)
    products[0].popularity = products[1].popularity
    sut = PopularProductsService(products)
    result = sut.find_popular_products([0], 2)
    assert set(products) == set(result)


def test_will_ignore_out_of_stock_products():
    products = flatten([gen_products(shop_id, 10) for shop_id in range(10)])
    for i in range(0, 100, 3):
        products[i].quantity = 0
    sut = PopularProductsService(products)
    
    expected = filter(lambda p: p.quantity > 0, products)
    actual = sut.find_popular_products(range(10), 100)
    
    assert set(expected) == set(actual)


def test_can_handle_no_data():
    sut = PopularProductsService([])
    assert [] == sut.find_popular_products(range(10), 100)

