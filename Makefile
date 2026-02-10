get_MQTT:
	echo "MQTT broker mqtt://mosquitto:1883"


docker_start:
	docker compose up -d --build fastapi

docker_init_database:
	docker compose run --rm fastapi python /app/init_database.py

docker_status:
	docker compose ps

docker_log_app:
	docker compose logs

docker_stop:
	docker compose stop

docker_delete:
	docker compose down -v
	sudo rm -rf postgres/data
	mkdir -p ./postgres/data

docker_connect_db:
	docker exec -it timescaledb psql -U iot_user -d iot


