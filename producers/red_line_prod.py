from pykafka import KafkaClient
import json
from datetime import datetime
import uuid
import time

input_file = open('../transformed_data/red_line.json')
json_array = json.load(input_file)

def generate_uuid():
    return uuid.uuid4()

client = KafkaClient(hosts="localhost:9092")
topic = client.topics['geodata_line']
producer = topic.get_sync_producer()

data = {}
data['busline'] = 'Red Line'

def generate_checkpoint(features):
    for feature in features:
        coordinates = feature['geometry']['coordinates']
        i = 0
        while i < len(coordinates):
            data['key'] = data['busline'] + '_' + str(generate_uuid())
            data['timestamp'] = str(datetime.utcnow())
            data['latitude'] = coordinates[i][1]
            data['longitude'] = coordinates[i][0]
            message = json.dumps(data)
            print(message)  
            producer.produce(message.encode('ascii'))
            time.sleep(0.5)  
            if i == len(coordinates) - 1:
                break  
            else:
                i += 1

generate_checkpoint(json_array['features'])
