import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

# Kafka Configuration (Matching your Docker setup)
conf = {'bootstrap.servers': "localhost:9092"}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def stream_sensor_data():
    topic = 'mfg_sensor_stream'
    sensors = ['SNS-1001', 'SNS-1002', 'SNS-1003']
    
    print(f"Starting Real-Time Stream to Kafka Topic: {topic}...")
    
    try:
        while True:
            data = {
                'sensor_id': random.choice(sensors),
                'metric_name': 'Vibration (Hz)',
                'metric_value': round(random.uniform(50.0, 150.0), 2),
                'ingestion_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Send to Kafka
            producer.produce(topic, json.dumps(data).encode('utf-8'), callback=delivery_report)
            producer.flush()
            
            time.sleep(2) # Stream an event every 2 seconds
    except KeyboardInterrupt:
        print("Streaming stopped by user.")

if __name__ == "__main__":
    stream_sensor_data()
