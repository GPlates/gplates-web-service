import requests
import json

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

def gws_plot_polygons(polygon_feature,m,ax_map,**kwargs):
    for feature in polygon_feature['features']:
        coords = feature['geometry']['coordinates']
        xy = zip(*coords[0])
        x,y = m(xy[0],xy[1])
        patch = []
        patch.append( Polygon(zip(x,y), True) )
        ax_map.add_collection(PatchCollection(patch, **kwargs))


def gws_plot_vectors(velocity_feature,m,ax_map,**kwargs):
    
    data = np.asarray(velocity_feature['coordinates'])

    Xnodes = np.arange(-180,180.1,1.)
    Ynodes = np.arange(-90,90.1,1.)
    u = data[:,2].reshape((Ynodes.shape[0],Xnodes.shape[0]))
    v = data[:,3].reshape((Ynodes.shape[0],Xnodes.shape[0]))

    uproj,vproj,xx,yy = \
    m.transform_vector(u,v,Xnodes,Ynodes,60,30,returnxy=True,masked=True)
    # now plot.
    Q = m.quiver(xx,yy,uproj,vproj,**kwargs)

