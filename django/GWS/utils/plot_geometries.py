import io

import matplotlib

matplotlib.use("Agg")
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from PIL import Image


def plot_polygons(
    polygons,
    edgecolor="black",
    facecolor="lime",
    alpha=0.7,
    extent=None,
    central_meridian=0,
):
    """plot polygons with cartopy and return the map PNG image

    :params polygons: shapely polygons
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

        ax.add_geometries(
            polygons,
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
