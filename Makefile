get_node-red:
	echo "node-red http://localhost:1880"

get_MQTT:
	echo "MQTT broker mqtt://mosquitto:1883"

docker_build:
	docker compose build fastapi

docker_start:
	docker compose up -d --build fastapi

docker_status:
	docker compose ps

docker_log_app:
	docker compose logs

docker_stop:
	docker compose stop

docker_delete:
	docker compose down -v

docker_connect_db:
	docker exec -it timescaledb psql -U iot_user -d iot
