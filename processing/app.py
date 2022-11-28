import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS, cross_origin
import datetime
from base import Base
import requests
from stats import Stats
import yaml
import json
import os
import sqlite3
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler

def create_database(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE stats
    (id INTEGER PRIMARY KEY ASC,
    num_phlevel_reading INTEGER NOT NULL,
    max_phlevel_reading INTEGER NOT NULL,
    max_water_level INTEGER,
    max_chlorine_level INTEGER,
    num_chlorine_level INTEGER,
    last_updated VARCHAR(100) NOT NULL)
''')
    conn.commit()
    conn.close()

path = '/data/data.sqlite'
isExist = os.path.exists(path)
if isExist == True:
    print("Exists")
else:
    create_database(path)

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"sqlite:///{path}")
#DB_ENGINE = create_engine("sqlite:///%s" %app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    logger.info('Request has been started')
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    if not results:
        logger.error("Statistics does not exist")
        return 404
    
    #logger.debug(f"contents of python dictionary {results[-1].to_dict()}")
    logger.info("The request has been completed")
    session.close()
    return results[0].to_dict(), 200

def populate_stats():
    """ Periodically update stats """
    logger.info('Period processing has been started')
    session = DB_SESSION()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    try:
        last_updated = str(results[0].last_updated)
        a,b = last_updated.split(" ")
        url1 = app_config["phlevel"]["url"]+a+'T'+b+"&end_timestamp="+current_timestamp
        url2 = app_config["chlorinelevel"]["url"]+a+'T'+b+"&end_timestamp="+current_timestamp

    
    except IndexError:
        last_updated = '2016-08-29T09:12:33.001000'
        url1 = app_config["phlevel"]["url"]+last_updated+"&end_timestamp="+current_timestamp
        url2 = app_config["chlorinelevel"]["url"]+last_updated+"&end_timestamp="+current_timestamp


    headers = {"content-type": "application/json"}

    response_ph_level = requests.get(url1, headers=headers)
    response_chlorine_level = requests.get(url2, headers=headers)
    
    ph_list = response_ph_level.json() 
    chlorine_list = response_chlorine_level.json()
    logger.info(f"List of ph level - {ph_list}")
    logger.info(f" Length = {len(ph_list)}")

    logger.info(f"List of chlorine level - {chlorine_list}")
    logger.info(f" Length = {len(chlorine_list)}")

    if response_ph_level.status_code != 200: 
        logger.error(f"Status code received {response_ph_level.status_code}")

    try:
        num_phlevel_reading = results[0].num_phlevel_reading + len(ph_list)
        max_phlevel_reading = results[0].max_phlevel_reading
        max_chlorine_level = results[0].max_chlorine_level
        max_water_level = results[0].max_water_level
        num_chlorine_level = results[0].num_chlorine_level + len(chlorine_list)
        last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    except IndexError:
        num_phlevel_reading = len(ph_list)
        max_phlevel_reading = 0
        max_chlorine_level = 0
        max_water_level = 0
        num_chlorine_level = len(chlorine_list)
        last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    session = DB_SESSION()
    for i in ph_list:
        logger.debug(f"new event with a trace id of {i['trace_id']}")
        if i["phlevel"] >  max_phlevel_reading:
            max_phlevel_reading = i["phlevel"] 
        if i["waterlevel"] > max_water_level:
            max_water_level = i["waterlevel"] 

    for i in chlorine_list:
      if i["chlorinelevel"] > max_chlorine_level:
        max_chlorine_level = i["chlorinelevel"]
      if i["waterlevel"] > max_water_level:
        max_water_level = i["waterlevel"] 

    session = DB_SESSION()
    stats = Stats(num_phlevel_reading,
        max_phlevel_reading,
        max_water_level,
        max_chlorine_level,
        num_chlorine_level,
        datetime.datetime.strptime(last_updated,
        "%Y-%m-%dT%H:%M:%S.%f"))
    logger.debug(f"Updated statistics values : max_phlevel_reading ={max_phlevel_reading}, num_phlevel_reading ={num_phlevel_reading}, max_water_level = {max_water_level} , max_chlorine_level = {max_chlorine_level}, num_chlorine_level ={num_chlorine_level}")

    logger.info("Period processing has ended.")

    session.add(stats)

    session.commit()
    session.close()
    
def health_check():
    logger.info("Checking for health")
    dictionary = {"message" : "running"}
    return dictionary, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True,validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
