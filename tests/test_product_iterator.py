from server.product import PopularProductsIterator
from tests.helpers import most_popular, flatten, gen_products


def test_iterator_orders_products_by_popularity():
    shop_ids = range(10)
    products = [gen_products(id) for id in shop_ids]
    shops = zip(shop_ids, [iter(p) for p in products])
    sut = PopularProductsIterator(shops, 10)
    
    assert most_popular(flatten(products), 10) == list(sut)


def test_iterator_bounded_by_count():
    shop_ids = range(10)
    products = [gen_products(id) for id in shop_ids]
    
    shops = zip(shop_ids, [iter(p) for p in products])
    
    sut = PopularProductsIterator(shops, 7)
    assert len(list(sut)) is 7


def test_iterator_can_handle_empty_shops():
    products = gen_products(1, 5)
    empty = iter([])
    shops = zip([1, 2, 3], [iter(products), empty, empty])
    sut = PopularProductsIterator(shops, 5)
    assert list(sut) == products


def test_iterator_can_handle_insufficient_products():
    products = gen_products(1, 5)
    sut = PopularProductsIterator([(1, iter(products))], 10)
    assert products == list(sut)


def test_iterator_can_handle_no_data():
    sut = PopularProductsIterator([], 10)
    assert len(list(sut)) == 0

