.PHONY: build up down migrations migrate superuser
build:
	docker-compose build
up:
	docker-compose up -d
down:
	docker-compose down
test:
	docker-compose run app python3 manage.py test

starter:
	docker exec -i `docker ps -aqf "name=^meal_project-db-1$$"` sh -c 'exec mysql -u root -p"$$MYSQL_ROOT_PASSWORD" meal_project' < sql/starter.sql 
