from numpy import median
from geopy.distance import distance as geo_dist
from server.shop import Shop, ShopRepository
from server.location import loc_in_range

# Distance in kilometers
max_distance = 100
shop_count = 200

def test_can_find_shops_within_distance():
    center_loc = (0, 20)
    locations = [loc_in_range(center_loc, max_distance) for x in range(shop_count)]
    shops = [new_shop(loc) for loc in locations]
    sut = ShopRepository(shops)
    
    medianDistance = median([geo_dist(loc, center_loc) for loc in locations])
    
    expected = [shop for shop in shops if geo_dist(center_loc, shop.location) <= medianDistance]
    actual = sut.find_shops(center_loc, medianDistance.kilometers)
   
    assert set(expected) == set(actual)


def test_can_filter_shops_by_tag():
    tag = 'outwear'
    center_loc = (0,0)
    locations = [loc_in_range(center_loc, max_distance) for x in range(shop_count)]
    shops = [new_shop(loc) for loc in locations]
    taggings = [(tag, get_id(locations[i])) for i in range(shop_count/2)]
    
    sut = ShopRepository(shops, taggings)
    
    expected = shops[0:shop_count/2]
    actual = sut.find_shops(center_loc, max_distance, [tag])
    
    assert set(expected) == set(actual)

def new_shop(loc):
    return Shop(get_id(loc), loc)

def get_id(loc):
    return "{0}{1}".format(loc[0], loc[1])
