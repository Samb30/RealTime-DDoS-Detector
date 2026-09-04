import pandas as pd
from kafka import KafkaProducer
import json
import time

# 1. Setup the Kafka Producer
# value_serializer converts our Python dictionary into a JSON byte format Kafka can read
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC_NAME = 'network-traffic'

def stream_data(csv_path):
    print(f"Starting simulation from {csv_path}...")
    
    # 2. Read the CSV using Pandas
    df = pd.read_csv(csv_path)
    
    # 3. Loop through the dataset row by row
    for index, row in df.iterrows():
        # Convert the row data into a Python dictionary
        traffic_record = row.to_dict()
        
        # Send the record to our Kafka topic
        producer.send(TOPIC_NAME, traffic_record)
        
        print(f"Sent record {index + 1}: {traffic_record['source_ip']} -> {traffic_record['destination_ip']} | Label: {traffic_record['label']}")
        
        # Pause for 1 second to simulate live streaming
        time.sleep(1.0)
        
    producer.flush() # Ensure all messages are sent before closing
    print("Simulation finished.")

if __name__ == "__main__":
    # Run the simulator using our dummy data
    stream_data('data/sample_traffic.csv')