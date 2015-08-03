from server.app import Shop, ShopRepository
from numpy import mgrid, ravel
from helpers import *


def test_can_find_shops_within_distance():
    distance = 1000
    center_loc = Location.rand()
    far_away_loc = center_loc.add(distance*2+1, 0)
    
    nearby_shops = [new_shop(center_loc.new(distance)) for x in range(5)]
    far_away_shops = [new_shop(far_away_loc.new(distance)) for x in range(100)]
    
    sut = ShopRepository(nearby_shops + far_away_shops)
    result = sut.find_shops(center_loc.data(), distance)
    
    assert set(nearby_shops) == set(result)


def test_can_filter_shops_by_tag():
    distance = 1000
    tag = 'outwear'
    center_loc = Location.rand()
    locations = [center_loc.new(distance) for x in range(10)]
    shops = [new_shop(loc) for loc in locations]
    taggings = [(tag, get_id(locations[i])) for i in range(5)]
    
    sut = ShopRepository(shops, taggings)
    result = sut.find_shops(center_loc.data(), distance, [tag])
    
    assert set(shops[0:5]) == set(result)

def new_shop(loc):
    return Shop(get_id(loc), loc.lat, loc.lon)

def get_id(loc):
    return "{0}{1}".format(loc.lat, loc.lon)
