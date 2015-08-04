from random import randint, random
from math import sin, cos, pi, radians, sqrt

km_per_degree = 111.111

def offset_loc(location, offset):
    """ Creates a new GPS location at offset of the original one.
        
        Parameters
        ----------
        location : tuple of floats
            Base location in degrees. Format: (latitude, longitude).
        offsetLat : tuple of floats
            The offset distance in kilometers. Format: (latitude, logitude).
            
        Returns
        -------
        location : tuple of floats
            The new location in degrees. Format: (latitude, longitude).
            
    """
    lat = location.lat + offset[0] / km_per_degree
    lon = location.lon + offset[1] / (km_per_degree / cos(radians(lat)))
    return lat, lon

def loc_in_range(location, r):
    """ Computes a random GPS location within radius.
    
        Due to west-east shrinking, it can break the radius at high latitude.
        For correct results, use within degrees: -75 < latitude < 75.
        [more info](http://gis.stackexchange.com/questions/25877/how-to-generate-random-locations-nearby-my-location)
        
        Parameters
        ----------
        location : tuple of floats
            The base location. Format: latitude, longitude.
        r : float
            The limiting radius in kilometers.
            
    """
    r /= km_per_degree
    u = random()
    v = random()
    w = r*sqrt(u)
    t = 2*pi*v
    x = w*cos(t)
    y = w*sin(t)
    x /= cos(radians(location[0]))
    return location[0] + y, location[1] + x

def rand_loc():
    """ Generates a random GPS location.
    
    """
    lat = random() * 90 * 1 if randint(0,1) % 2 == 0 else -1
    lon = random() * 180 * 1 if randint(0,1) % 2 == 0 else -1
    return lat, lon

