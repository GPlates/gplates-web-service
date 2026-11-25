"""Response headers for API versioning (see GitHub issue #24).

Every response carries ``X-GWS-Version`` so callers of the unversioned URLs
can log which release actually answered them.

When this release is being phased out, set GWS_DEPRECATION_DATE (and
optionally GWS_SUNSET_DATE and GWS_SUCCESSOR_URL) in the environment or .env
and every response also carries:

- ``Deprecation`` (RFC 9745), e.g. ``@1798761600``
- ``Sunset`` (RFC 8594), e.g. ``Sat, 01 Jan 2028 00:00:00 GMT``
- ``Link: <https://gws.gplates.org/v2/>; rel="successor-version"``

Dates are ISO dates (YYYY-MM-DD, taken as 00:00 UTC). A date that can't be
parsed is logged and ignored, so a typo never takes the service down.
"""

import logging
from datetime import date, datetime, timezone
from email.utils import format_datetime

from django.conf import settings

from .version_info import VERSION

logger = logging.getLogger("default")

VERSION_HEADER = "X-GWS-Version"


def _parse_date(name, value):
    if not value:
        return None
    try:
        d = date.fromisoformat(str(value).strip())
    except ValueError:
        logger.error(f"Ignoring {name}={value!r}: expected a date like 2027-06-30")
        return None
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def build_version_headers():
    """Return the (name, value) headers to add to every response."""
    headers = {VERSION_HEADER: VERSION}

    deprecation = _parse_date(
        "GWS_DEPRECATION_DATE", getattr(settings, "GWS_DEPRECATION_DATE", None)
    )
    sunset = _parse_date("GWS_SUNSET_DATE", getattr(settings, "GWS_SUNSET_DATE", None))
    successor = (getattr(settings, "GWS_SUCCESSOR_URL", None) or "").strip()

    if deprecation:
        headers["Deprecation"] = f"@{int(deprecation.timestamp())}"
    if sunset:
        headers["Sunset"] = format_datetime(sunset, usegmt=True)
    if successor and (deprecation or sunset):
        headers["Link"] = f'<{successor}>; rel="successor-version"'

    return headers


class APIVersionHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.headers = build_version_headers()
        # let browser JavaScript on other sites read these headers too
        self.expose = ", ".join(self.headers)

    def __call__(self, request):
        response = self.get_response(request)
        for name, value in self.headers.items():
            # don't clobber a Link header a view set itself
            if name == "Link" and response.has_header("Link"):
                response["Link"] = f"{response['Link']}, {value}"
            else:
                response[name] = value

        existing = response.get("Access-Control-Expose-Headers")
        response["Access-Control-Expose-Headers"] = (
            f"{existing}, {self.expose}" if existing else self.expose
        )
        return response
