

## 1. INITIALISATION _________________________________________________
mkdir -p postgres/data

mkdir -p mosquitto/config mosquitto/data mosquitto/log
nano mosquitto/config/mosquitto.conf
````
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data
log_dest stdout
```

make docker_build
make docker_start












