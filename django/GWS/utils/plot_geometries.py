import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import cartopy.crs as ccrs
from shapely.geometry.polygon import Polygon

#
#
#
def plot_polygons(polygons, edgecolor, facecolor, alpha, date_line_wrapper, extent):
    try:
        fig = plt.figure(figsize=(12, 8), dpi=300)
        ax = plt.axes(projection=ccrs.PlateCarree(),frameon=False)
        # ax.gridlines()
        if extent:
            ax.set_extent(extent)
        else:
            ax.set_global()
        #ax.background_patch.set_visible(False)  # Background
        #ax.outline_patch.set_visible(False)  # Borders
        imgdata = io.BytesIO()

        # wrap the polygons at date iine
        wrapped_polygons = []
        for polygon in polygons:
            if date_line_wrapper:
                wrapped_polygons.extend(
                    date_line_wrapper.wrap(polygon.get_reconstructed_geometry(), 2.0)
                )
            else:
                wrapped_polygons.append(polygon.get_reconstructed_geometry())

        polygons = []
        for p in wrapped_polygons:
            if date_line_wrapper:
                points = [
                    [point.to_lat_lon()[1], point.to_lat_lon()[0]]
                    for point in p.get_exterior_points()
                ]
            else:
                points = [
                    [point.to_lat_lon()[1], point.to_lat_lon()[0]]
                    for point in p.get_exterior_ring_points()
                ]
            polygons.append(Polygon(points))

        ax.add_geometries(
            polygons,
            ccrs.PlateCarree(),
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
