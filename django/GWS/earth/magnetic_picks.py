"""Query the GSFML magnetic anomaly identification picks.

The picks live in the "magnetic.picks" table, which is created and populated by
"python manage.py load_magnetic_picks". See
django/GWS/earth/management/commands/load_magnetic_picks.py.
"""

import json
import logging
import traceback

from django.db import connection
from django.db.utils import ProgrammingError
from django.http import HttpResponseBadRequest, HttpResponseServerError
from utils.access_control import get_client_ip
from utils.decorators import extract_params, return_HttpResponse
from utils.round_float import round_floats

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")

# The canonical region names, as stored in the database.
REGIONS = ["atlantic", "indian", "pacific", "marginal_backarc_basins"]

# What users may type for each region. The GSFML file names are accepted too,
# so that a name copied from gsfml.earthbyte.org works.
REGION_ALIASES = {
    "atlantic": "atlantic",
    "atlanticocean": "atlantic",
    "atlantic_ocean": "atlantic",
    "indian": "indian",
    "indianocean": "indian",
    "indian_ocean": "indian",
    "pacific": "pacific",
    "pacificocean": "pacific",
    "pacific_ocean": "pacific",
    "marginal_backarc_basins": "marginal_backarc_basins",
    "marginal_backarcbasins": "marginal_backarc_basins",
    "marginalbackarcbasins": "marginal_backarc_basins",
    "marginal": "marginal_backarc_basins",
    "backarc": "marginal_backarc_basins",
}

# Values which mean "do not filter by region".
ALL_REGIONS = {"", "all", "global", "world"}

# How many picks a single request returns when no end_index is given, and the
# largest number it will return at all. The whole data set is around 100,000
# picks, which is too much GeoJSON for one response.
DEFAULT_PAGE_SIZE = 10000
MAX_PAGE_SIZE = 50000

COLUMNS = [
    "pick_index",
    "region",
    "chron",
    "anomaly_end",
    "anom_end_quality",
    "cruise_name",
    "reference",
    "doi",
    "geek2007",
    "id_method",
]


class InvalidParameter(Exception):
    pass


def parse_int(params, name, default):
    """Return an integer parameter. Unlike parameter_helper.get_int, a value
    which is not an integer is an error rather than a silent fallback to the
    default -- a typo in start_index should not quietly return the wrong page.
    """
    raw = params.get(name, None)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(str(raw).strip())
    except ValueError:
        raise InvalidParameter(f"Invalid integer for '{name}': {raw}.")


def parse_float(params, name, default):
    """Return a float parameter, or raise InvalidParameter."""
    raw = params.get(name, None)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return float(str(raw).strip())
    except ValueError:
        raise InvalidParameter(f"Invalid number for '{name}': {raw}.")


def parse_region(params):
    """Return the canonical region name, or None to query all regions."""
    raw = params.get("region", "")
    key = str(raw).strip().lower().replace(" ", "_").replace("-", "_")
    if key in ALL_REGIONS:
        return None
    if key in REGION_ALIASES:
        return REGION_ALIASES[key]
    raise InvalidParameter(
        f"Unknown region: '{raw}'. Valid regions are {', '.join(REGIONS)} "
        "(or omit the parameter to query all regions)."
    )


def build_filters(region, min_age, max_age):
    """Return (sql_where, params) for the given filters."""
    clauses = []
    values = []
    if region is not None:
        clauses.append("region = %s")
        values.append(region)
    if min_age is not None:
        clauses.append("geek2007 >= %s")
        values.append(min_age)
    if max_age is not None:
        clauses.append("geek2007 <= %s")
        values.append(max_age)
    if not clauses:
        return "", values
    return " WHERE " + " AND ".join(clauses), values


@extract_params
@return_HttpResponse()
def get_magnetic_picks(request, params={}):
    """Return GSFML magnetic anomaly identification picks as GeoJSON.

    http://localhost:18000/earth/get_magnetic_picks?region=pacific&min_age=10&max_age=20

    :param region: one of "atlantic", "indian", "pacific",
        "marginal_backarc_basins". Omit it (or use "all") to query every region.
    :param start_index: index of the first pick to return, 0-based (default 0)
    :param end_index: index just past the last pick to return. The range is
        half-open, so start_index=0&end_index=100 returns 100 picks.
        Defaults to start_index + 10000. At most 50000 picks per request.
    :param min_age: only return picks whose age is at least this, in Ma
    :param max_age: only return picks whose age is at most this, in Ma

    The indices count through the picks which match the region and age
    filters, ordered by the "pick_index" column, which is stable across
    requests. Each feature also carries its absolute "pick_index", so paging
    through a filtered query and looking a pick up later both work.

    "min_age" and "max_age" filter on the GeeK2007 column -- the age in Ma on
    the Gee & Kent (2007) timescale.
    """
    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    try:
        region = parse_region(params)
        start_index = parse_int(params, "start_index", 0)
        end_index = parse_int(params, "end_index", None)
        min_age = parse_float(params, "min_age", None)
        max_age = parse_float(params, "max_age", None)
    except InvalidParameter as e:
        return HttpResponseBadRequest(str(e))

    if start_index < 0:
        return HttpResponseBadRequest(
            f"'start_index' cannot be negative ({start_index})."
        )
    if end_index is None:
        end_index = start_index + DEFAULT_PAGE_SIZE
    if end_index <= start_index:
        return HttpResponseBadRequest(
            f"'end_index' ({end_index}) must be greater than "
            f"'start_index' ({start_index})."
        )

    page_size = end_index - start_index
    if page_size > MAX_PAGE_SIZE:
        return HttpResponseBadRequest(
            f"The requested range holds {page_size} picks, which is more than the "
            f"{MAX_PAGE_SIZE} allowed in one request. Ask for a smaller range and "
            "page through the data with 'start_index' and 'end_index'."
        )

    if min_age is not None and min_age < 0:
        return HttpResponseBadRequest(f"'min_age' cannot be negative ({min_age}).")
    if min_age is not None and max_age is not None and min_age > max_age:
        return HttpResponseBadRequest(
            f"'min_age' ({min_age}) is greater than 'max_age' ({max_age})."
        )

    where, filter_values = build_filters(region, min_age, max_age)

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT count(*) FROM magnetic.picks{where}", filter_values)
            total_matched = cursor.fetchone()[0]

            cursor.execute(
                f"""SELECT {', '.join(COLUMNS)}, ST_X(geom), ST_Y(geom)
                    FROM magnetic.picks{where}
                    ORDER BY pick_index
                    LIMIT %s OFFSET %s""",
                filter_values + [page_size, start_index],
            )
            rows = cursor.fetchall()
    except ProgrammingError as e:
        logger.error(e)
        return HttpResponseServerError(
            'The table "magnetic.picks" does not exist. The magnetic picks have '
            "not been loaded into this server's database. See "
            '"manage.py load_magnetic_picks".'
        )
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseServerError("Failed to query the magnetic picks.")

    features = []
    for row in rows:
        properties = dict(zip(COLUMNS, row[: len(COLUMNS)]))
        lon, lat = row[len(COLUMNS)], row[len(COLUMNS) + 1]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": properties,
            }
        )

    data = {
        "type": "FeatureCollection",
        "region": region if region is not None else "all",
        "start_index": start_index,
        "end_index": start_index + len(features),
        "returned": len(features),
        "total_matched": total_matched,
        "features": features,
    }

    return json.dumps(round_floats(data, decimals=6))
