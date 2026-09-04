from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Configuration
URL = "http://localhost:8086"
TOKEN = "XkPuCCCnw8eXUzfv0xKlJF9swrFxBBWv15-IAouSygu33q63QqohqVeMnBPG2LjzsPyMtpTtFL_0ifnVsDwM8w=="
ORG = "portfolio-org"
BUCKET = "ddos-predictions"

# Initialize the InfluxDB client and write API
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_prediction_to_db(prediction_result):
    """
    Takes the dictionary from our ML model and writes it as a 
    time-series point into InfluxDB.
    """
    try:
        # Create a time-series data point
        point = (
            Point("network_traffic_predictions")
            .tag("source_ip", prediction_result.get("source_ip"))
            .tag("destination_ip", prediction_result.get("destination_ip"))
            .tag("attack_type", prediction_result.get("predicted_attack_type"))
            .field("anomaly_score", float(prediction_result.get("anomaly_score")))
            .field("is_threat", bool(prediction_result.get("is_threat")))
        )
        
        # Write the point to our bucket
        write_api.write(bucket=BUCKET, org=ORG, record=point)
        print(f"Successfully wrote record for {prediction_result.get('source_ip')} to InfluxDB.")
        
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")