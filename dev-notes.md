### Redis

- `docker pull redis`
- `docker run --name gws-redis --network gws-net -d redis`
- `docker run -it --network gws-net --rm redis redis-cli -h gws-redis`

### Dev

- ./docker/start-postgis.sh
- ./docker/start-gws-dev.sh

### Test

- ./test/test-dev-server.sh
- ./test/test-pro-server.sh
- <http://localhost:18000/>

### Logging

You need to specify a writable folder for the log files in settings.py. By default, the folder is /gws/log.