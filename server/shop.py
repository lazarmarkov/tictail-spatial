from scipy.spatial import KDTree
from geopy.distance import distance as geo_dist
from math import cos, radians


class ShopRepository(object):
        
    def __init__(self, shops, taggings = None):
        """ Allows range searching for shops within a certain distance.
        Also, tags can be specified to narrow the result.
        
        Parameters
        ----------
        shops : list of Shops
            The list of shops to be indexed.
        taggings : list of tuples of len 2
            Mappings from tag to shop_id.
        
        """

        # A list of all shop locations.
        self._loc_data = [shop.location for shop in shops]

        # A k-d tree based index of shop locations.
        # Storing the locations in a k-d tree 
        # makes it possible to perform range searching
        self._loc_index = KDTree(self._loc_data)
        
        # mappings from a location to a shop
        self._loc_to_shop = {s.location: s for s in shops}
        
        # mappings from a tag to shops that are tagged
        self._tag_to_shops = {}
        
        if taggings is None:
            return
        
        for tag, shop_id in taggings:
            self._tag_shop(tag, shop_id)

    def _tag_shop(self, tag, shop_id):
        """ Tags a shop with a tag.
        
        """
        self._get_shops_by_tag(tag).add(shop_id)
        
    def _get_shops_by_tag(self, tag):
        """ Return all shops, tagged with the specified `tag`.
        
        """
        if tag not in self._tag_to_shops:
            self._tag_to_shops[tag] = set()
        return self._tag_to_shops[tag]
    
    def find_shops(self, location, distance, tags=None):
        """ Finds all shops within `distance` of the specified `location`.
        
        Parameters
        ----------
        location : tuple of floats of len 2
            The GPS location acting as a center in the range search.
        distance : float
            The limiting distance (in kilometers) acting as a radius in the range search.
        tags : list of strings
            An list of tags that is used to filter the shops result.
            If a shop has none of the tags, it is filtered.
        
        Returns
        -------
        shops : list of Shops
            The list of Shops within range [ and filtered by tags].
        
        """
        # Finds the locations of the shops.
        locations = self._find_shop_locations(location, distance)
        
        # Get the shops by location.
        shops = [self._loc_to_shop[loc] for loc in locations]
        
        # If no tags specified, return the result.
        if tags is None:
            return shops
        
        # Get the mappings from a tag to shops, for each tag specified.
        tags_to_shops = [self._get_shops_by_tag(tag) for tag in tags]
        
        # Filter the shops.
        # If a shop has none of the specified tags - filter it.
        return filter(lambda shop: self._has_shop_any_tag(shop.id, tags_to_shops), shops)
    
    def _find_shop_locations(self, location, distance):
        """ Perform the actual range search.            
            
        Parameters
        ----------
        location : tuple of len 2
            The center GPS location used for the search.
        distance : float
            Limiting distance in km.

        """
        # Convert distance to longitude degrees at `location` latitude.
        # Motivation:
        # In GPS, as latitude increases,
        # the distance per degree of longitude decreases.
        # Hence, near the poles `distance`
        # equals more degrees than on the equator.
        # This must be taken into account since KDTree
        # computes Euclidean distance on the GPS locations.
        degrees = distance / (111.111 * cos(radians(location[0])))
        
        # Account for calculated distance deviation,
        # between geopy.distance.distance and
        # equating a flat 111.111 km per degree ratio.
        degrees *= 1.01

        # Perform the actual range search
        loc_idx = self._loc_index.query_ball_point(location, degrees)
        locations = [self._loc_data[i] for i in loc_idx]
        
        # Filter the result set, because of the enlarged distance,
        # accounting for the distance deviation.
        return filter(lambda l: geo_dist(location, l) <= distance, locations)

    @staticmethod
    def _has_shop_any_tag(shop_id, tags_to_shops):
        """ Checks if a shop has at least one of the specified tags.

        Parameters
        ----------
        shop_id : string
            The id of the shop to check.
        tags_to_shops : list of dict
            A list of dictionaries that map a tag to tagged shops.

        """
        return any(shop_id in d for d in tags_to_shops)


class Shop(object):
    
    def __init__(self, id, location, name=''):
                
        # Id of the shop.
        self.id = id
        
        # Location of the shop.
        self.location = location
        
        # Name of the shop.
        self.name = name

