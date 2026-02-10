import os
import json
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from models import Datastream, Observation
from database import SessionLocal


MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("iot/+/+")

def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    if len(topic_parts) != 3:
        return
    _, thing_id, observed_property = topic_parts
    payload = json.loads(msg.payload.decode())

    session: Session = SessionLocal()
    try:
        ds = session.query(Datastream).filter_by(
            thing_id=thing_id,
            observed_property=observed_property
        ).first()
        if ds is None:
            print(f"No datastream for {thing_id}/{observed_property}")
            return
        
        # Create STA-compliant observation
        obs = Observation(
            phenomenonTime=payload.get("phenomenonTime", datetime.now().isoformat()),
            result=payload["result"],
            resultTime=payload.get("resultTime"),
            parameters=payload.get("parameters", {}),
            datastream_id=ds.id,
            time=datetime.now()  # Your existing timestamp field
        )
        session.add(obs)
        session.commit()
        print(f"Inserted observation for {ds.id}")
    finally:
        session.close()

def start():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
 
