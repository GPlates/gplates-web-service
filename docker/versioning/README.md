# Running GWS versions side by side

Implements the versioning policy in [issue #24](https://github.com/GPlates/gplates-web-service/issues/24):
breaking releases get a new major API version (`/v2/`) and run next to the
old one (`/v1/`), so existing callers keep working.

## How it fits together

```
                        ┌──────────────── host ────────────────┐
 /v1/...     ──┐        │                                       │
 /v2/...     ──┼──► reverse proxy ──► gws-v1 :18001  (/v1/ + unversioned)
 /...  (none)──┘        │         └─► gws-v2 :18002  (/v2/ + unversioned)
                        │                 │
                        │     gplates-postgis, gplates-redis (shared)
                        └───────────────────────────────────────┘
```

- **Each image serves its own prefix.** A v1.x image answers both
  `/reconstruct/...` and `/v1/reconstruct/...`; a v2.x image answers `/...`
  and `/v2/...`. The prefix comes from `VERSION` in
  `django/GWS/GWS/version_info.py`. The proxy passes paths through unchanged.
- **Unversioned URLs go to the default version**, chosen in the proxy config.
- **Every response has `X-GWS-Version`** (e.g. `v1.1.0`), so callers of
  unversioned URLs can log what they got.
- **Redis is shared** but cache keys are prefixed per major version
  (`gws-v1`, `gws-v2`), so one version never serves the other's cached results.

| File | Purpose |
| --- | --- |
| `docker-compose.versions.yml` | One container per major version, each pinned to a release tag |
| `apache-gws-proxy.conf` | Host Apache vhost that routes by prefix |
| `nginx-gws-proxy.conf` | Same, for nginx |

## Release runbook

**Non-breaking release (v1.x → v1.y):** build and tag as usual, bump
`GWS_V1_IMAGE_TAG`, `docker compose ... up -d gws-v1`. Nothing else changes.

**Breaking release (v1 → v2):**

1. Set `VERSION = "v2.0.0"` in `version_info.py`, tag `v2.0.0`; the existing
   workflow builds `gplates/gws:v2.0.0`.
2. Uncomment `gws-v2` in `docker-compose.versions.yml` and start it.
3. Uncomment the `/v2/` lines in the proxy config and reload. Unversioned URLs
   still go to v1.
4. On `gws-v1`, set `GWS_DEPRECATION_DATE`, `GWS_SUNSET_DATE` and
   `GWS_SUCCESSOR_URL` and recreate it. v1 responses now carry `Deprecation`,
   `Sunset` and `Link: <...v2/>; rel="successor-version"` headers.
5. Update docs, examples, the portal and gwspy to call `/v2/` explicitly;
   announce the deprecation and sunset dates in the release notes.

**End of the deprecation period:**

1. Point the unversioned `/` in the proxy config at v2 and reload (one line).
2. Watch `/v1/` traffic in the access logs; once it's negligible (or the sunset
   date has passed), remove the `/v1/` proxy lines and the `gws-v1` container.
   Don't keep old versions forever: an unpatched frozen stack is a security
   and maintenance burden.

## First-time setup (going from one container to this layout)

The image currently running in production (v1.0.0) predates the `/v1/` alias.
Release a v1.x image that includes it first, then:

1. Start `gws-v1` from that tag
   (`docker compose -f docker/versioning/docker-compose.versions.yml up -d`).
   It listens on 127.0.0.1:18001; the existing `docker-gws` on 18000 can keep
   running meanwhile.
2. Check it: `curl -i http://127.0.0.1:18001/v1/version/` should return the
   version and an `X-GWS-Version` header.
3. Install the proxy config on the host, pointing at 18001, and reload.
4. Once traffic is flowing through the new container, stop `docker-gws`.

No caller sees a change: unversioned URLs keep working, `/v1/` is new.
