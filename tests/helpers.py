from math import sqrt, pi, cos, sin, radians
from random import random, randint
from heapq import nlargest
from server.product import Product


def most_popular(products, n):
    """
    Returns the `n` most popular products from `products`
    
    """
    return nlargest(n, products, lambda p: p.popularity)


def gen_products(shop_id, count=10):
    return sorted([gen_product(shop_id) for i in range(count)], key=lambda p: p.popularity * -1)


def gen_product(shop_id):
    return Product(0, shop_id, 'title', random(), randint(1,100))


def flatten(list_of_lists):
    """
    Flattens a list of lists.

    """
    return [item for l in list_of_lists for item in l]


# A degree length at the equator equals ~ 111.111 km
km_per_degree = 111.111


def loc_in_range(location, r):
    """ Computes a random GPS location within radius.

        Due to west-east shrinking, a point can break the radius at high latitude.
        For correct results, use within degrees: -75 < latitude < 75.
        [more info](http://gis.stackexchange.com/questions/25877/how-to-generate-random-locations-nearby-my-location)

        Parameters
        ----------
        location : tuple of floats
            The base location. Format: (latitude, longitude).
        r : float
            The limiting radius in km.

    """
    r /= km_per_degree
    u = random()
    v = random()
    w = r*sqrt(u)
    t = 2*pi*v
    x = w*cos(t)
    y = w*sin(t)
    x /= cos(radians(location[0]))
    return location[0] + y, location[1] + x


def rand_loc():
    """ Generates a random GPS location.

    """
    lat = random() * 90 * 1 if randint(0, 1) % 2 == 0 else -1
    lon = random() * 180 * 1 if randint(0, 1) % 2 == 0 else -1
    return lat, lon

