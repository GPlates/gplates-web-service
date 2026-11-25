"""Load the GSFML magnetic anomaly identification picks into the database.

Usage
-----

Download the data from gsfml.earthbyte.org and load it::

    python manage.py load_magnetic_picks

Reload from scratch (drops the existing table first)::

    python manage.py load_magnetic_picks --recreate

Load from shapefiles/zip files which have already been downloaded::

    python manage.py load_magnetic_picks --data-dir /path/to/gsfml-picks


About the data
--------------

The GSFML picks are published as five shapefiles -- one global file and four
regional files. The four regional files partition the global file exactly:
their record counts add up to the global count, no pick appears in two regions,
and concatenating them in the order

    AtlanticOcean, IndianOcean, Marginal_BackarcBasins, PacificOcean

reproduces the global file record for record (verified against the 2022-11-22
release: 41961 + 25388 + 3718 + 30624 = 101691 picks).

Because of that, only the four regional files are loaded here. Every pick gets
a "region" and the global data set is simply the whole table. Loading the
regional files in the order above makes the "pick_index" column line up with
the row order of the global shapefile, so an index into "magnetic.picks" means
the same thing as a row number in GSFML.global.picks.shp.

Note that the source data contains a small number of exact duplicate rows
(identical coordinates and attributes -- 1031 of them in the 2022-11-22
release). They are loaded as they are, rather than silently de-duplicated, so
that the table stays faithful to the published data set.
"""

import os
import shutil
import tempfile
import urllib.request
import zipfile

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

# Sent when downloading the data. gsfml.earthbyte.org answers 403 to the
# default urllib User-Agent.
USER_AGENT = "gplates-web-service/load_magnetic_picks"

# The regions, in the order which reproduces the row order of
# GSFML.global.picks.shp. The first element of each tuple is the canonical
# region name stored in the database and accepted by the web service.
REGIONS = [
    (
        "atlantic",
        "GSFML.AtlanticOcean.picks",
        "https://gsfml.earthbyte.org/ML/DATA/AtlanticOcean/GSFML.AtlanticOcean.picks.zip",
    ),
    (
        "indian",
        "GSFML.IndianOcean.picks",
        "https://gsfml.earthbyte.org/ML/DATA/IndianOcean/GSFML.IndianOcean.picks.zip",
    ),
    (
        "marginal_backarc_basins",
        "GSFML.Marginal_BackarcBasins.picks",
        "https://gsfml.earthbyte.org/ML/DATA/Marginal_BackarcBasins/GSFML.Marginal_BackarcBasins.picks.zip",
    ),
    (
        "pacific",
        "GSFML.PacificOcean.picks",
        "https://gsfml.earthbyte.org/ML/DATA/PacificOcean/GSFML.PacificOcean.picks.zip",
    ),
]

# The attribute columns of the GSFML pick shapefiles, mapped to our column
# names. The shapefile field names are given in the .dbf header.
#   Chron       C(80)  -- e.g. "C13n"
#   AnomalyEnd  C(80)  -- "y" (young), "o" (old) or "c" (centre)
#   AnomEndQua  N(9)   -- quality 1, 2 or 3
#   CruiseName  C(80)  -- "N/A" when unknown
#   Reference   C(80)  -- e.g. "Cande++_1988_JGR"
#   DOI         C(80)  -- "N/A" or empty when unknown
#   GeeK2007    N(24)  -- age in Ma, on the Gee & Kent (2007) timescale
#   IDMethod    C(80)  -- e.g. "Magnetic Anomaly"
FIELDS = [
    ("Chron", "chron"),
    ("AnomalyEnd", "anomaly_end"),
    ("AnomEndQua", "anom_end_quality"),
    ("CruiseName", "cruise_name"),
    ("Reference", "reference"),
    ("DOI", "doi"),
    ("GeeK2007", "geek2007"),
    ("IDMethod", "id_method"),
]

# Values which mean "no data" in the GSFML text columns.
NO_DATA = {"", "n/a", "na", "none", "unknown"}

SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS magnetic"

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS magnetic.picks (
    pick_index       integer PRIMARY KEY,
    region           text             NOT NULL,
    chron            text,
    anomaly_end      text,
    anom_end_quality smallint,
    cruise_name      text,
    reference        text,
    doi              text,
    geek2007         double precision,
    id_method        text,
    geom             geometry(Point, 4326) NOT NULL
)
"""

INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS picks_region_idx ON magnetic.picks (region)",
    "CREATE INDEX IF NOT EXISTS picks_geek2007_idx ON magnetic.picks (geek2007)",
    "CREATE INDEX IF NOT EXISTS picks_region_geek2007_idx ON magnetic.picks (region, geek2007)",
    "CREATE INDEX IF NOT EXISTS picks_region_pick_index_idx ON magnetic.picks (region, pick_index)",
    "CREATE INDEX IF NOT EXISTS picks_geom_idx ON magnetic.picks USING GIST (geom)",
]

COMMENT_SQL = [
    (
        "COMMENT ON TABLE magnetic.picks IS "
        "'GSFML magnetic anomaly identification picks, from https://gsfml.earthbyte.org/ML/DATA/ . "
        'Loaded by "manage.py load_magnetic_picks".\''
    ),
    (
        "COMMENT ON COLUMN magnetic.picks.pick_index IS "
        "'0-based stable index. Follows the row order of GSFML.global.picks.shp.'"
    ),
    (
        "COMMENT ON COLUMN magnetic.picks.geek2007 IS "
        "'Age in Ma on the Gee & Kent (2007) timescale.'"
    ),
]

INSERT_SQL = """
INSERT INTO magnetic.picks
    (pick_index, region, chron, anomaly_end, anom_end_quality, cruise_name,
     reference, doi, geek2007, id_method, geom)
VALUES %s
"""

# The %s placeholders of INSERT_SQL, per row. The last two are lon and lat.
INSERT_TEMPLATE = (
    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))"
)


def clean_text(value):
    """Return a stripped string, or None when the value means "no data"."""
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in NO_DATA:
        return None
    return text


def clean_number(value):
    """Return a float, or None when the value is missing or not a number."""
    text = clean_text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Load the GSFML magnetic anomaly identification picks into magnetic.picks."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            default=None,
            help=(
                "Directory holding the already-downloaded GSFML region zip files or "
                "the extracted shapefiles. The data is downloaded from "
                "gsfml.earthbyte.org when this is not given."
            ),
        )
        parser.add_argument(
            "--recreate",
            action="store_true",
            help="Drop the magnetic.picks table before loading.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,
            help="Number of rows per INSERT statement (default 5000).",
        )

    def handle(self, *args, **options):
        try:
            import shapefile  # pyshp
        except ImportError:
            raise CommandError(
                "This command needs the 'pyshp' package. Install it with "
                "'conda install -c conda-forge pyshp' or 'pip install pyshp'."
            )

        data_dir = options["data_dir"]
        recreate = options["recreate"]
        batch_size = options["batch_size"]

        work_dir = None
        if not data_dir:
            work_dir = tempfile.mkdtemp(prefix="gsfml-picks-")
            data_dir = work_dir

        try:
            # Get hold of every shapefile before touching the table, so that a
            # failed download does not leave the database without its picks.
            shapefiles = [
                (
                    region,
                    self._get_shapefile(
                        data_dir, basename, url, download=bool(work_dir)
                    ),
                )
                for region, basename, url in REGIONS
            ]

            self._prepare_table(recreate)
            total = 0
            counts = []
            for region, shp_path in shapefiles:
                n = self._load_region(shapefile, shp_path, region, total, batch_size)
                counts.append((region, n))
                total += n
                self.stdout.write(f"  loaded {n} picks for region '{region}'")

            self._create_indexes()
        finally:
            if work_dir:
                shutil.rmtree(work_dir, ignore_errors=True)

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {total} magnetic picks in total.")
        )
        for region, n in counts:
            self.stdout.write(f"  {region:<24} {n}")

    def _prepare_table(self, recreate):
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL)
            if recreate:
                self.stdout.write("Dropping magnetic.picks ...")
                cursor.execute("DROP TABLE IF EXISTS magnetic.picks")
            cursor.execute(TABLE_SQL)
            cursor.execute("SELECT count(*) FROM magnetic.picks")
            existing = cursor.fetchone()[0]

        if existing:
            raise CommandError(
                f"magnetic.picks already holds {existing} rows. "
                "Use --recreate to drop the table and load the data again."
            )

    def _create_indexes(self):
        self.stdout.write("Creating indexes ...")
        with connection.cursor() as cursor:
            for sql in INDEX_SQL:
                cursor.execute(sql)
            for sql in COMMENT_SQL:
                cursor.execute(sql)
            cursor.execute("ANALYZE magnetic.picks")

    def _get_shapefile(self, data_dir, basename, url, download):
        """Return the path of the region's ".shp" file.

        Looks for an extracted shapefile first, then for a zip file to unpack,
        and downloads the zip file when the data directory was not supplied.

        The ".shp" suffix matters: the GSFML file names contain dots, so pyshp
        would read "GSFML.AtlanticOcean.picks" as a path with a ".picks"
        extension and look for "GSFML.AtlanticOcean.shp" instead.
        """
        extracted = os.path.join(data_dir, basename, basename)
        if os.path.exists(extracted + ".shp"):
            return extracted + ".shp"
        flat = os.path.join(data_dir, basename)
        if os.path.exists(flat + ".shp"):
            return flat + ".shp"

        zip_path = os.path.join(data_dir, basename + ".zip")
        if not os.path.exists(zip_path):
            if not download:
                raise CommandError(
                    f"Could not find '{basename}.shp' or '{basename}.zip' in {data_dir}."
                )
            self.stdout.write(f"Downloading {url} ...")
            os.makedirs(data_dir, exist_ok=True)
            # gsfml.earthbyte.org answers 403 to the default urllib
            # User-Agent, so say who we are.
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    with open(zip_path, "wb") as out:
                        shutil.copyfileobj(response, out)
            except OSError as e:
                if os.path.exists(zip_path):
                    os.remove(zip_path)  # do not leave a half-written zip file
                raise CommandError(f"Failed to download {url}: {e}")

        out_dir = os.path.join(data_dir, basename)
        os.makedirs(out_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                # only take the shapefile parts, and never a path outside out_dir
                if os.path.basename(name) != name:
                    continue
                if not name.lower().endswith((".shp", ".shx", ".dbf", ".prj", ".cpg")):
                    continue
                zf.extract(name, out_dir)

        if not os.path.exists(extracted + ".shp"):
            raise CommandError(f"'{basename}.shp' was not found inside {zip_path}.")
        return extracted + ".shp"

    def _load_region(self, shapefile, shp_path, region, index_offset, batch_size):
        """Insert one region's picks. Returns the number of rows inserted."""
        from psycopg2.extras import execute_values

        reader = shapefile.Reader(shp_path)
        field_names = [f[0] for f in reader.fields[1:]]  # skip the deletion flag
        missing = [src for src, _ in FIELDS if src not in field_names]
        if missing:
            raise CommandError(
                f"{shp_path[:-4]}.dbf is missing the expected column(s): "
                f"{', '.join(missing)}. "
                f"Found: {', '.join(field_names)}."
            )
        positions = {src: field_names.index(src) for src, _ in FIELDS}

        with connection.cursor() as cursor:
            raw_cursor = getattr(cursor, "cursor", cursor)
            batch = []
            count = 0
            for shape_record in reader.iterShapeRecords():
                shape = shape_record.shape
                if not shape.points:
                    continue  # a pick with no geometry cannot be mapped or queried
                lon, lat = shape.points[0][0], shape.points[0][1]
                record = shape_record.record

                values = {}
                for src, column in FIELDS:
                    raw = record[positions[src]]
                    if column in ("anom_end_quality", "geek2007"):
                        values[column] = clean_number(raw)
                    else:
                        values[column] = clean_text(raw)

                quality = values["anom_end_quality"]
                batch.append(
                    (
                        index_offset + count,
                        region,
                        values["chron"],
                        values["anomaly_end"],
                        int(quality) if quality is not None else None,
                        values["cruise_name"],
                        values["reference"],
                        values["doi"],
                        values["geek2007"],
                        values["id_method"],
                        lon,
                        lat,
                    )
                )
                count += 1

                if len(batch) >= batch_size:
                    with transaction.atomic():
                        execute_values(
                            raw_cursor, INSERT_SQL, batch, template=INSERT_TEMPLATE
                        )
                    batch = []

            if batch:
                with transaction.atomic():
                    execute_values(
                        raw_cursor, INSERT_SQL, batch, template=INSERT_TEMPLATE
                    )

        reader.close()
        return count
