from server.app import Shop, ShopRepository
from numpy import mgrid, ravel

def test_can_find_shops_within_distance():
    repo = new_repo()
    shops = repo.find_shops((5,5), 1.01)
    assert len(shops) is 5
    assert set([x.location() for x in shops]) == set([(4,5), (5,4), (5,5), (5,6), (6,5)])


def test_can_find_shops_by_tag():
    tag = 'outwear'
    locations = [(4,5), (5,5), (5,4)]
    taggings = [(tag, get_id(loc)) for loc in locations]
    
    repo = new_repo(taggings = taggings)
    
    shops = repo.find_shops((5,5), 1.01, [tag])
    actualLocations = [s.location() for s in shops]
    
    assert set(locations) == set(actualLocations)


def new_repo(width = 10, height = 10, taggings = None):
    grid = make_grid(width, height)
    shops = [Shop(get_id(loc), loc[0], loc[1]) for loc in grid]
    return ShopRepository(shops, taggings or [])


def get_id(p):
    return '{0}{1}'.format(p[0],p[1])
    
def make_grid(width, height):
    x, y = mgrid[0:width, 0:height]
    return zip(x.ravel(), y.ravel())

    
    