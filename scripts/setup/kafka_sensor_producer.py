import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

# Kafka Configuration
conf = {'bootstrap.servers': "localhost:9092"}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message {msg.offset() + 1} delivered to {msg.topic()}")

def stream_sensor_data():
    topic = 'mfg_sensor_stream'
    sensors = ['SNS-1001', 'SNS-1002', 'SNS-1003', 'SNS-1004']
    
    print(f"🚀 Starting HIGH-SPEED Stream to: {topic}")
    print("💡 Sending 50 messages rapidly to force a MinIO archival flush...")
    
    msg_count = 0
    try:
        # Loop 50 times quickly to hit the connector's flush threshold
        for i in range(50):
            data = {
                'sensor_id': random.choice(sensors),
                'metric_name': 'Vibration (Hz)',
                'metric_value': round(random.uniform(50.0, 150.0), 2),
                'status': random.choice(['OK', 'WARNING', 'CRITICAL']),
                'ingestion_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Send to Kafka
            producer.produce(
                topic, 
                json.dumps(data).encode('utf-8'), 
                callback=delivery_report
            )
            
            # Flush local buffer every 5 messages to ensure Kafka receives them
            if i % 5 == 0:
                producer.flush()
            
            msg_count += 1
            time.sleep(0.05) # 50ms delay between messages
            
        # Final flush to ensure all 50 are sent
        producer.flush()
        print(f"🏁 Burst complete. Total sent: {msg_count}")
        print("👀 Refresh your MinIO 'kafka-archive' bucket now!")

    except KeyboardInterrupt:
        print("\nStreaming stopped.")

if __name__ == "__main__":
    stream_sensor_data()
