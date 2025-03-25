# flask-api
Tiny api sample built on python/flask using redis to queue messages. This example includes authentication, some basic tests and Metrics export to be collected by prometheus.

## Running locally

To locally run this app you can rely on docker-copose.

### Steps:
1. Clone respository
```shell
 git clone git@github.com:c0r0nel/flask-api.git
```
3.  cd into flask-api directory
4. Edit `docker-compose.yaml` file and update the API_KEY env var with some powerful key and then run compose:
```shell
docker-compose up
```
5. Export some needed env vars:
```shell
export APK_KEY="somekey"
export REDIS_HOST="localhost"
```
6. Play with api pushing and poping messages:

```shell
curl -X POST http://127.0.0.1:5001/api/queue/push -H "API-Key: somekey" -H "Content-Type: application/json" -d '{"message": "Testing queuing a single message"}'
```
```shell
curl -X GET http://127.0.0.1:5001/api/queue/count -H "API-Key: somekey"
```
```shell
curl -X POST http://127.0.0.1:5001/api/queue/pop -H "API-Key: somekey"
```
You should receive confirmations or error messages for each request.

In addition you also can query the `/metrics` endpoint to check if it's collectiong data correctly.
```shell
curl -X GET http://127.0.0.1:8000/metrics
```

## Running tests
To run tests you need to create and activate a pyton env first:

```shell
python3 -m venv env
source env/bin/activate
```
then you need to install all dependencies on that env:

```shell
pip install --no-cache-dir -r requirements.txt
```
as last step before running tests, be sure to have env var exported:
```shell
export APK_KEY="somekey"
export REDIS_HOST="localhost"
```
Run test:
```shell
pytest test_app.py
```

## Automation
in .github/workflows directory there are two worflows:
- `ci.ymal` to run tests on every push and merge.
- `docker.yaml` to manully build and push docker image to dockerhub.

In order to test this two workflows you need to set up two repository secrets on your github `/settings/secrets/actions`
- API_KEY (set any value you want)
- DOCKER_HUB_TOKEN
This one is needed to allow github to push images to our DockerHub account. Yo need to create this token on your dockerhub account fisrt and the use the value here.
