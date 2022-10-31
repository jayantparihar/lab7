from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ChlorineLevel(Base):
    """ Chlorine Level """

    __tablename__ = "chlorine_level"

    id = Column(Integer, primary_key=True)
    location = Column(String(250), nullable=False)
    chlorinelevel = Column(Integer, nullable=False)
    device_id = Column(String(250), nullable=False)
    temperature = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    waterlevel = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)
    

    def __init__(self, location, chlorinelevel, temperature,device_id, timestamp, waterlevel,trace_id):
        """ Initializes Chlorine level reading """
        self.location = location
        self.chlorinelevel = chlorinelevel
        self.temperature = temperature
        self.device_id = device_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.waterlevel = waterlevel
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of Chlorine level reading """
        dict = {}
        dict['id'] = self.id
        dict['location'] = self.location
        dict['device_id'] = self.device_id
        dict['temperature'] = self.temperature
        dict['chlorinelevel'] = self.chlorinelevel
        dict['waterlevel'] = self.waterlevel
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id']= self.trace_id

        return dict
