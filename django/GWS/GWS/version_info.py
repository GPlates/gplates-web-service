"""Version numbers for this GWS release.

Kept free of Django imports so settings.py can import it.

VERSION is the full release number, reported by /version/ and in the
X-GWS-Version response header. API_MAJOR is the major API version this
release serves under (e.g. "v1" for VERSION "v1.2.3"), used for the
/v1/... URL prefix. Bump the major number only for breaking releases;
see the "API versioning" page in the docs and GitHub issue #24.
"""

VERSION = "v1.0.0"

API_MAJOR = VERSION.split(".")[0]
