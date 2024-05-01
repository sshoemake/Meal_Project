.PHONY: build up down migrations migrate superuser
build:
	docker-compose build
up:
	docker-compose up -d
test:
	docker-compose run app python3 manage.py test
