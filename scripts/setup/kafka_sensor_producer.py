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
        print(f"❌ Delivery failed: {err}")
    else:
        # Simplified report for cleaner logs
        print(f"✅ Message {msg.offset() + 1} delivered to {msg.topic()}")

def stream_sensor_data():
    topic = 'mfg_sensor_stream'
    sensors = ['SNS-1001', 'SNS-1002', 'SNS-1003']
    
    print(f"🚀 Starting Real-Time Stream to Kafka Topic: {topic}...")
    print("💡 NOTE: You need 10 messages to 'flush' a file into MinIO kafka-archive.")
    
    msg_count = 0
    try:
        while True:
            data = {
                'sensor_id': random.choice(sensors),
                'metric_name': 'Vibration (Hz)',
                'metric_value': round(random.uniform(50.0, 150.0), 2),
                'ingestion_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Send to Kafka
            producer.produce(
                topic, 
                json.dumps(data).encode('utf-8'), 
                callback=delivery_report
            )
            
            # Flush immediately to ensure the connector sees it
            producer.flush()
            
            msg_count += 1
            if msg_count % 10 == 0:
                print(f"🔔 Threshold reached! Check MinIO bucket: kafka-archive")
            
            # Stream faster (0.5s) to populate the archive quickly
            time.sleep(0.5) 
            
    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")

if __name__ == "__main__":
    stream_sensor_data()
