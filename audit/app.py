import logging
from types import new_class
import uuid
import connexion
import json
import datetime
from connexion import NoContent
import os
from swagger_ui_bundle import swagger_ui_path
import requests
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_ph_level_readings(index):
    """ Get ph level Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving ph level at index %d" % index)
    try:
        lst = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.debug(msg['type'])
            if msg['type'] == 'ph_level':
              
               lst.append(msg) 
        logger.debug(lst[index -1])  
        return lst[index - 1], 201
    # Find the event at the index you want and
    # return code 200
    # i.e., return event, 200

    except IndexError:
        logger.error("No more messages found")
        logger.error("Could not find ph level at index %d" % index)
        return { "message": "Not Found"}, 404


def get_chlorine_level_readings(index):
    """ Get chlorine Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving chlorine level at index %d" % index)
    try:
        lst = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.debug(msg)
            if msg['type'] == 'chlorine_level':
               lst.append(msg) 
        return lst[index - 1], 201
    # Find the event at the index you want and
    # return code 200
    # i.e., return event, 200

    except IndexError:
        logger.error("No more messages found")
        logger.error("Could not find chlorine_level at index %d" % index)
        return { "message": "Not Found"}, 404
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    
    app.run(port=8110)

