# -*- coding: utf-8 -*-

import os
from flask import Flask
from server.api import api
from scipy.spatial import KDTree
from rbtree import rbtree

def create_app(settings_overrides=None):
    app = Flask(__name__)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)
    return app


def configure_settings(app, settings_override):
    parent = os.path.dirname(__file__)
    data_path = os.path.join(parent, '..', 'data')
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'DATA_PATH': data_path
    })
    if settings_override:
        app.config.update(settings_override)


def configure_blueprints(app):
    app.register_blueprint(api)

class ShopRepository(object):
        
    def __init__(self, shops, taggings = None):
        """ Allows range searching for shops within a certain distance.
        Optionally, tags can be specified when searching for finer results.
        
        Parameters
        ----------
        shops : list of Shops
            A list of shops that will be indexed and queried.
        taggings : list of tuples of len 2
            Mappings from tag to shop_id.
        
        """
        # A collection of all shop locations.
        self._loc_data = [shop.location() for shop in shops]
        
        # An k-d tree based index of shop locations.
        # Storing the locations in a k-d tree 
        # makes it possible to perform range searching in logarithmic time
        self._loc_index = KDTree(self._loc_data)
        
        # mappings from a location to a shop
        self._loc_to_shop = {s.location() : s for s in shops}
        
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
    
    def find_shops(self, location, distance, tags = None):
        """ Finds all shops within `distance` of the specified `location`.
        
        Parameters
        ----------
        location : tuple of floats of len 2
            The GPS location(lat, lon) acting as a center in the range search.
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
        if(tags is None):
            return shops
        
        # Get the mappings from a tag to shops,
        # for each tag specified.
        tags_to_shops = [self._get_shops_by_tag(tag) for tag in tags]
        
        # Filter the shops.
        # If a shop has none of the specified tags - filter it.
        return filter(lambda shop: self._has_shop_any_tag(shop.id, tags_to_shops), shops)
    
    def _find_shop_locations(self, location, distance):
        """ Perform the actual range search.            
            
        """
        # Convert kilometers to degrees
        # since locations in index are in GPS format.
        distance = float(distance) / 111111
        
        # Find the indices of the shop locations within `distance` of `location`.
        loc_idx = self._loc_index.query_ball_point(location, distance)
        
        # Return the locations of the shops found.
        return [self._loc_data[i] for i in loc_idx]
    
    def _has_shop_any_tag(self, shop_id, tags_to_shops):
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
    
    def __init__(self, id, lat, lon, name=''):
                
        # Id of the shop.
        self.id = id
        
        # Latitude of the shop location.
        self.lat = lat
        
        # longitude of the shop location.
        self.lon = lon
        
        # Name of the shop.
        self.name = name
    
    def location(self):
        """ Return the GPS location of the shop.
            
        """
        return (self.lat, self.lon)
    
    
class PopularProductsService(object):
    
    def __init__(self, products):
        """ A service that finds the most popular products
        within a list of shops.
        
        Parameters
        ----------
        products : list of Products
        
        """
        # Mapping from shop id to list of products within the shop.
        # The products are sorted by popularity in descending order.
        self._products_by_shop = {}
        
        # Filter the out of stock products.
        products = filter(lambda p: p.quantity > 0, products)
        
        for p in products:
            products = self._get_products_by_shop(p.shop_id)
            products[p.popularity] = p
    
    def _get_products_by_shop(self, shop_id):
        """ Returns a list of products for the `shop id`, ordered by popularity.
        
            Parameters
            ----------
            shop_id : string
                The id of the shop for which to get the products.
            
            Returns
            -------
            products : bst of Products
                A red-black tree of Products, ordered by Product.popularity, in descending order.
        
        """
        
        # Check if a mapping for the shop is missing.
        if shop_id not in self._products_by_shop:
            # Map the shop to an empty rbtree.
            self._products_by_shop[shop_id] = rbtree(
                cmp = PopularProductsService._duplicate_reverse_order_comparer)
        
        # Return the products for the shop.
        return self._products_by_shop[shop_id]
    
    def find_popular_products(self, shop_ids, count):
        """ Finds the most popular products within the specified shops.
        
        Parameters
        ----------
        shop_ids : list of strings
            Ids of the shops included in the search.
        count : int
            The max number of products to return.
        
        Returns
        -------
        products : list of Products
            The list of most popular products.
        
        """
        # Get the list of sorted products by popularity for each shop specified.
        products_per_shop = [self._get_products_by_shop(id).values() for id in shop_ids]
        
        # Get an iterator for each list of products.
        iterators = [iter(products) for products in products_per_shop]
        
        # Create a ad-hoc iterator,
        # feeded with products iterators for the specified shops.
        it = PopularProductsIterator(zip(shop_ids, iterators), count)
        
        # List the result.
        return list(it)
    
    @staticmethod
    def _duplicate_reverse_order_comparer(x, y):
        """ A reverse order comparer that allows duplicate entries.
        If two items are equal it declares the first one larger.
        
        """
        x = cmp(x, y)
        if(x == 0):
            return 1
        return -x


class PopularProductsIterator(object):
    
    def __init__(self, shops, count):
        """ Iterates products by popularity from multiple shops.
        
            Parameters
            ----------
            shops : list of tuples
                First item is id of the shop,
                second item is an iterator to its products, ordered by Product.popularity.
            count : int
                The max number of products to return.
            
        """
        # Mappings from shop id to an iterator to its products.
        self._shops = dict(shops)
        
        # Mappings from shop id to its current most popular product.
        self._most_popular_in_shop = {}
        
        # The number of products left to return.
        self._count = count
        
        # Initialize the current most popular product per shop.
        for shop_id in self._shops.keys():
            self._next_most_popular_in_shop(shop_id)

    def _next_most_popular_in_shop(self, shop_id):
        """ Moves to the next most popular product for a shop.
        
        """
        try:
            # Gets next most popular product for the shop
            # and assigns it as its current most popular.
            self._most_popular_in_shop[shop_id] = self._shops[shop_id].next()
        # No more products in the shop.
        except StopIteration:
            
            # Remove the taken product.
            if shop_id in self._most_popular_in_shop:
                del self._most_popular_in_shop[shop_id]
            
            # Remove the empty shop.
            del self._shops[shop_id]
    
    def __iter__(self):
        return self
    
    def next(self):
        """ Return the next most popular product with the shops.
        
            Returns
            -------
            product : Product
                
        """
        # If max number of products are returned
        # OR
        # if there are no more products to return,
        # signal stop iteration.
        if self._count == 0 or not bool(self._most_popular_in_shop):
            raise StopIteration
        
        # Find the most popular product within the shops.
        p = max(self._most_popular_in_shop.values(), key = lambda p: p.popularity)
        
        # Mark the product as taken,
        # and move to the next one in the shop.
        self._next_most_popular_in_shop(p.shop_id)
        
        # Decrease the remaining products to return.
        self._count -= 1
        return p
    

class Product(object):
    
    def __init__(self, id, shop_id, title, popularity, quantity):
        
        # Id of the product.
        self.id = id
        
        # Id of the product's shop.
        self.shop_id = shop_id
        
        # Title of the product.
        self.title = title
        
        # Popularity rating of the product.
        self.popularity = popularity
        
        # Product quantity in stock.
        self.quantity = quantity
    
    def __str__(self):
        return "Product: id:{0}, shop_id:{1}, title:{2}, populariy:{3}, quantity:{4}".format(
            self.id, self.shop_id, self.title, self.popularity, self.quantity)

