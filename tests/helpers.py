from random import random, randint
from heapq import nlargest
from server.product import Product

# Kilometers in one degree of latitude,
# or in one degree ot longitude at equator.
km_in_a_degree = 111.111

def most_popular(products, n):
    """
    Returns the `n` most popular products from `products`
    
    """
    return nlargest(n, products, lambda p: p.popularity)

def gen_products(shop_id, count = 10):
    return sorted([ gen_product(shop_id) for i in range(count)], key = lambda p: p.popularity * -1)

def gen_product(shop_id):
    return Product(0, shop_id, 'title', random(), randint(1,100))


def flatten(l):
    """
    Flattens a list of lists.
        
    """
    return  [val for subl in l for val in subl]
