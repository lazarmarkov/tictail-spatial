from random import random, randint
from math import pi, sin, cos
from heapq import nlargest
from server.app import Product



def most_popular(products, n):
    return nlargest(n, products, lambda p: p.popularity)

def gen_products(shop_id, count = 10):
    return sorted([ gen_product(shop_id) for i in range(count)], key = lambda p: p.popularity * -1)

def gen_product(shop_id):
    return Product(0, shop_id, 'title', random(), randint(1,100))

def flatten(l):
    return  [val for subl in l for val in subl]

def km_to_degree(km):
    return float(km) / 1111111

class Location(object):
    
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    
    def add(self, offsetLat, offsetLon):
        lat = self.lat + float(offsetLat) / 111111
        lon = self.lon + float(offsetLon) / (111111 * cos(lat))
        return Location(lat, lon)

    def new(self, radius):
        t = 2*pi*random()
        u = random()+random()
        r = 2 - u if u > 1 else u
        degrees = km_to_degree(radius)
        return Location(self.lat + r*cos(t) * degrees, self.lon + r*sin(t) * degrees)
    
    def data(self):
        return self.lat, self.lon
    
    @staticmethod
    def rand():
        lat = random() * 90 * 1 if randint(0,1) % 2 == 0 else -1
        lon = random() * 180 * 1 if randint(0,1) % 2 == 0 else -1
        return Location(lat, lon)