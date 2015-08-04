# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from flask import Flask
from server.api import api, data_path
from server.product import Product, PopularProductsService
from server.shop import Shop, ShopRepository


def create_app(settings_overrides=None):
    app = Flask(__name__)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)
    initialize(app)
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


def initialize(app):
    get_data = lambda f: pd.read_csv(os.path.join(app.config['DATA_PATH'], f)).get_values()

    tags = {r[0]: r[1] for r in get_data('tags.csv')}
    shops = [Shop(r[0], (r[2], r[3]), r[1]) for r in get_data('shops.csv')]
    taggings = [(tags[r[2]], r[1]) for r in get_data('taggings.csv')]
    products = [Product(r[0], r[1], r[2], r[3], r[4]) for r in get_data('products.csv')]

    app.shop_repo = ShopRepository(shops, taggings)
    app.prod_service = PopularProductsService(products)
