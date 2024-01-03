### Redis

- `docker pull redis`
- `docker run --name gws-redis --network gws-net -d redis`
- `docker run -it --network gws-net --rm redis redis-cli -h gws-redis`