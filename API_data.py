
import requests
from datetime import datetime
import json

url = "https://api.tfl.gov.uk/BikePoint/"

def call_api():
    r = requests.get(url)
    response = r.json()
    
    
    time_string = datetime.now().strftime("%Y-%m-%d-H%H-M%M")

    with open(f"C:/Users/jaack/Desktop/cycle-availability-predictor/data/bronze/{time_string}.json", "a") as f:
        json.dump(response, f, indent=2)
        
call_api()