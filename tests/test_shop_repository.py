from numpy import median
from geopy.distance import distance as geo_dist
from server.app import Shop, ShopRepository, Location

# Distance in kilometers
max_distance = 100
shop_count = 200

def test_can_find_shops_within_distance():
    center_loc = Location(0, 20)
    locations = [center_loc.nearby(max_distance) for x in range(shop_count)]
    shops = [new_shop(loc) for loc in locations]
    sut = ShopRepository(shops)
    
    medianDistance = median([geo_dist(loc.data(), center_loc.data()) for loc in locations])
    
    expected = [shop for shop in shops if geo_dist(center_loc.data(), shop.location()) <= medianDistance]
    actual = sut.find_shops(center_loc.data(), medianDistance.kilometers)
   
    assert set(expected) == set(actual)


def test_can_filter_shops_by_tag():
    tag = 'outwear'
    center_loc = Location(0,0)
    locations = [center_loc.nearby(max_distance) for x in range(shop_count)]
    shops = [new_shop(loc) for loc in locations]
    taggings = [(tag, get_id(locations[i])) for i in range(shop_count/2)]
    
    sut = ShopRepository(shops, taggings)
    
    expected = shops[0:shop_count/2]
    actual = sut.find_shops(center_loc.data(), max_distance, [tag])
    
    assert set(expected) == set(actual)

def new_shop(loc):
    return Shop(get_id(loc), loc.lat, loc.lon)

def get_id(loc):
    return "{0}{1}".format(loc.lat, loc.lon)
