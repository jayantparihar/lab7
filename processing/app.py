import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from base import Base
import requests
from stats import Stats
import yaml
import json
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
DB_ENGINE = create_engine("sqlite:///stats.sqlite")
#DB_ENGINE = create_engine("sqlite:///%s" %app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    logger.info('Request has been started')
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    session.close()
    return results[-1].to_dict(), 200

def populate_stats():
    """ Periodically update stats """
    logger.info('Period processing has been started')
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    logger.info('Started Periodic Processing')
    try:
        last_updated = str(results[0].last_updated)
        a,b = last_updated.split(" ")
        url1 = app_config["phlevel"]["url"]+a+'T'+b
        url2 = app_config["chlorinelevel"]["url"]+a+'T'+b
    
    except IndexError:
        last_updated = '2016-08-29T09:12:33.001000'
        url1 = app_config["phlevel"]["url"]+last_updated
        url2 = app_config["chlorinelevel"]["url"]+last_updated

    #print("last updated ---------------------- ", str(results[0].last_updated))
    headers = {"content-type": "application/json"}

    response_orders_received = requests.get(url1, headers=headers)
    response_damaged_parts = requests.get(url2, headers=headers)

    ph_list = response_orders_received.json() 
    chlorine_list = response_damaged_parts.json()

    logger.info(f"Number of ph level events received {results[0].num_phlevel_reading}")
    logger.info(f"Number of chlorine level events received {results[0].num_chlorine_level}")
    if response_orders_received.status_code != 200: 
        logger.error(f"Status code received {response_orders_received.status_code}")


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
        max_water_level =0
        num_chlorine_level = len(chlorine_list)
        last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    session = DB_SESSION()
    for i in ph_list:
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
    logger.info('Period processing ending')
    session.add(stats)
    session.commit()
    session.close()
    

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
