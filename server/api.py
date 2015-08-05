# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, jsonify, request

api = Blueprint('api', __name__)


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


@api.route('/search', methods=['GET'])
def search():
    lat = request.args.get('lat', 0, float)
    lon = request.args.get('lon', 0, float)
    distance = request.args.get('d', 10, float)
    tags = request.args.get('tags', None, str)
    count = request.args.get('n', 100, int)

    if bool(tags):
        tags = tags.split(',')

    shops = current_app.shop_repo.find_shops((lat, lon), distance, tags)
    products = current_app.prod_service.find_popular_products([s.id for s in shops], count)

    d = current_app.shops_by_id
    resp = jsonify({
        'products': [serialize(p, d) for p in products]
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def serialize(p, shops):
    s = shops[p.shop_id]
    return {
        'id': p.id,
        'shop_id': p.shop_id,
        'title': p.title,
        'popularity': p.popularity,
        'quantity': p.quantity,
        'shop': {
            'id': s.id,
            'lat': s.location[0],
            'lng': s.location[1],
            'name': s.name
        }
    }

