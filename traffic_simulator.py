import pandas as pd
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC_NAME = 'network-traffic'

def stream_data(csv_path):
    print(f"Starting simulation from {csv_path}...")
    
    df = pd.read_csv(csv_path)
    
    for index, row in df.iterrows():
        traffic_record = row.to_dict()
        
        producer.send(TOPIC_NAME, traffic_record)
        
        print(f"Sent record {index + 1}: {traffic_record['source_ip']} -> "
              f"{traffic_record['destination_ip']} | True Label: {traffic_record['label']}")
        
        time.sleep(1.0)
        
    producer.flush()
    print("Simulation finished.")

if __name__ == "__main__":
    stream_data('data/sample_traffic.csv')