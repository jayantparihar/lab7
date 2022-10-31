import connexion
from connexion import NoContent
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from chlorine_level import ChlorineLevel
from ph_level import PhLevel
import datetime
import logging
import logging.config
import yaml
from pykafka import KafkaClient
from threading import Thread 
from pykafka.common import OffsetType

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

create_engine_str = f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}'

DB_ENGINE = create_engine(create_engine_str)
Base.metadata.bind = DB_ENGINE
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)


    
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.debug("Connecting to database %s %s %s",hostname,port,db)


def report_ph_level(body):
    """ Receives a ph_level reading """
    pass
    # session = DB_SESSION()

    # ph = PhLevel(body['location'],
    #                     body['phlevel'],
    #                    body['temperature'],
    #                    body['device_id'],
    #                    body['timestamp'],
    #                    body['waterlevel'],
    #                    body["trace_id"]
    #                     )

    # session.add(ph)
    # session.commit()
    # session.close()
    # logger.debug("Stored event - PH level request with a trace id of %s",body["trace_id"])

    # return NoContent, 201


def report_chlorine_level(body):

    """ Receives a chlorine level reading """
    pass
    # session = DB_SESSION()

    # cl = ChlorineLevel(body['location'],
    #                    body['chlorinelevel'],
    #                    body['temperature'],
    #                    body['device_id'],
    #                    body['timestamp'],
    #                    body['waterlevel'],
    #                    body["trace_id"])

    # session.add(cl)
    # session.commit()
    # session.close()
    # logger.debug("Stored event - Chlorine level request with a trace id of %s",body["trace_id"])


    # return NoContent, 201

def get_ph_level_readings(timestamp):
    """ Gets ph level readings after the timestamp """
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f") #07/28/2014 18:54:55.099

    readings = session.query(PhLevel).filter(PhLevel.date_created >=timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Ph Level readings after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200

def get_chlorine_level_readings(timestamp):
    """ Gets chlorine parts readings after the timestamp """
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f") 

    readings = session.query(ChlorineLevel).filter(ChlorineLevel.date_created >=timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Chlroine level after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200


def process_messages():

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        print(msg['type'])
        
        if msg["type"] == "ph_level": # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()

            ph = PhLevel(payload['location'],
                        payload['phlevel'],
                       payload['temperature'],
                       payload['device_id'],
                       payload['timestamp'],
                       payload['waterlevel'],
                       payload["trace_id"]
                        )

            session.add(ph)

            session.commit()
            session.close()
           

        elif msg["type"] == "chlorine_level": # Change this to your event type
            session = DB_SESSION()
            logger.debug('it gets here')

            cl = ChlorineLevel(payload['location'],
                            payload['chlorinelevel'],
                            payload['temperature'],
                            payload['device_id'],
                            payload['timestamp'],
                            payload['waterlevel'],
                            payload["trace_id"]
                            )

            session.add(cl)
            session.commit()
            session.close()
        # Store the event2 (i.e., the payload) to the DB
        # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)
    