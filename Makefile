PROJECT_NAME ?= ddos_python
VERSION = $(shell python3.8 setup.py --version | tr '+' '-')
PROJECT_NAMESPACE ?= necko
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)


start_django:
	gunicorn --chdir django_app  --workers 5 django_app.wsgi

start_aiohttp:
	gunicorn aiohttp_app.app:create_app --bind localhost:8000 --worker-class aiohttp.GunicornWebWorker

start_pyramid:
	gunicorn pyramid_app.app:application --bind localhost:8000 --workers 5

start_bottle:
	python3 bottle_app/app.py

start_falcon:
	gunicorn falcon_app.main:application --bind localhost:8000 --workers 5

start_fast_api:
	uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000

start_locust:
	locust -f locust_ddos/ddos_attack.py --host=http://localhost:8000
