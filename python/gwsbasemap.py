import requests
import json

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

def gws_plot_polygons(polygon_feature,m,ax_map):
    for feature in polygon_feature['features']:
        coords = feature['geometry']['coordinates']
        xy = zip(*coords[0])
        x,y = m(xy[0],xy[1])
        patch = []
        patch.append( Polygon(zip(x,y), True) )
        ax_map.add_collection(PatchCollection(patch, facecolor='darkkhaki', edgecolor='k', linewidths=1., zorder=3))

