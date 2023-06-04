import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import cartopy.crs as ccrs
from shapely.geometry.polygon import Polygon

import pygplates


def plot_polygons(
    polygons,
    edgecolor="black",
    facecolor="lime",
    alpha=0.7,
    extent=None,
    central_meridian=0,
):
    """plot polygons with cartopy and return the map PNG image

    :params polygons: polygons
    :params edgecolor: edge color
    :params facecolor: face color
    :params alpha: alpha channel value
    :params extent: the extent of map, such as [-180, 180, -90, 90]
    :params central_meridian: central meridian

    :returns: binary data for the map image
    :rtype: bytes

    """
    try:
        crs = ccrs.PlateCarree(central_longitude=central_meridian)

        fig = plt.figure(figsize=(12, 8), dpi=300)
        ax = plt.axes(
            projection=crs,
            frameon=False,
        )
        # ax.gridlines()
        if extent:
            ax.set_extent(extent, crs=crs)
        else:
            ax.set_global()
        # ax.background_patch.set_visible(False)  # Background
        # ax.outline_patch.set_visible(False)  # Borders
        imgdata = io.BytesIO()

        # alway wrap when plotting map
        date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        # date_line_wrapper = pygplates.DateLineWrapper(0)
        # wrap the polygons at date iine
        shapely_polygons = []

        for polygon in polygons:
            ps = date_line_wrapper.wrap(polygon.get_reconstructed_geometry(), 2.0)
            for p in ps:
                points = []
                for point in p.get_exterior_points():
                    lon = point.to_lat_lon()[1]
                    lat = point.to_lat_lon()[0]

                    # LOOK HERE!!!!!!
                    # https://www.gplates.org/docs/pygplates/generated/pygplates.datelinewrapper
                    # If central_meridian is non-zero then the dateline is essentially shifted
                    # such that the longitudes of the wrapped points lie in the range
                    # [central_meridian - 180, central_meridian + 180]. If central_meridian
                    # is zero then the output range becomes [-180, 180].
                    lon = lon - central_meridian
                    points.append([lon, lat])
                shapely_polygons.append(Polygon(points))

        ax.add_geometries(
            shapely_polygons,
            crs,
            edgecolor=edgecolor,
            facecolor=facecolor,
            alpha=float(alpha),
        )
        fig.savefig(
            imgdata,
            format="png",
            bbox_inches="tight",
            dpi=96,
            transparent=True,
            pad_inches=0,
        )

        imgdata.seek(0)  # rewind the data
        plt.clf()

        return imgdata.getvalue()

    except Exception as e:
        # raise e
        print(str(e))
        tmp = Image.new("RGBA", (512, 512), (255, 100, 100, 100))
        b = io.BytesIO()
        tmp.save(b, "png")
        return b.getvalue()
