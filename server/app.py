# -*- coding: utf-8 -*-

import os
from flask import Flask
from server.api import api
from scipy.spatial import KDTree

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
    
    def __init__(self, shops, taggings):
        
        self._loc_data = [shop.location() for shop in shops]
        self._loc_index = KDTree(self._loc_data)
        self._loc_to_shop = {shop.location() : shop for shop in shops}
        self._tag_to_shops = {}
        
        for tag, shop_id in taggings:
            self._tag_shop(tag, shop_id)
                
    
    def _tag_shop(self, tag, shop_id):
        self._get_shops_by_tag(tag).add(shop_id)
        
    
    def _get_shops_by_tag(self, tag):
        if tag not in self._tag_to_shops:
            self._tag_to_shops[tag] = set()
        return self._tag_to_shops[tag]
    
    def find_shops(self, location, distance, tags = None):
        locations = self._find_shop_locations(location, distance)
        shops = [self._get_shop_by_location(loc) for loc in locations]
        
        if(tags is None):
            return shops
        
        tags_to_shops = [self._get_shops_by_tag(tag) for tag in tags]
        
        return filter(lambda shop: self._has_shop_any_tag(shop, tags_to_shops), shops) 
    
    def _find_shop_locations(self, location, distance):
        loc_idx = self._loc_index.query_ball_point(location, distance)
        return [self._loc_data[i] for i in loc_idx]
    
    def _get_shop_by_location(self, loc):
        return self._loc_to_shop[loc[0], loc[1]]
        
    def _has_shop_any_tag(self, shop, tags_to_shops):
        for tag_to_shops in tags_to_shops:
            if shop.id in tag_to_shops:
                return True
        return False


class Shop(object):
    
    def __init__(self, id, lat, lon, name=''):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.name = name
        
    def location(self):
        return (self.lat, self.lon)
      
