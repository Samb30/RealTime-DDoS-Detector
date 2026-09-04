from fastapi import FastAPI
from kafka import KafkaConsumer
import json
import threading
from contextlib import asynccontextmanager

# A temporary list to hold our traffic before we set up InfluxDB
latest_traffic = []

def consume_messages():
    # Set up the receiver
    consumer = KafkaConsumer(
        'network-traffic',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest' # Only read new messages
    )
    print("FastAPI is now listening to Kafka...")
    
    # Continuously listen for new messages
    for message in consumer:
        traffic_data = message.value
        
        # TODO: We will pass traffic_data to the LSTM model here later!
        
        latest_traffic.append(traffic_data)
        
        # Keep only the last 10 records to save memory
        if len(latest_traffic) > 10:
            latest_traffic.pop(0)

# Lifespan manages what happens when the server starts and stops
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the Kafka listener in the background
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()
    yield # The API runs while yielded

app = FastAPI(title="DDoS Detection API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "Pipeline Active"}

@app.get("/traffic")
def get_traffic():
    return {"live_data": latest_traffic}